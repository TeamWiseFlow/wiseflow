#!/usr/bin/env python3
"""Deterministic PPTX layout checks for obvious visual defects.

This catches the failure modes a visual pass often hand-waves away:
title/header collisions, text-box overlaps, text likely overflowing its box,
misaligned repeated picture groups, distorted images, and off-slide objects.
"""

from __future__ import annotations

import argparse
import json
import math
import posixpath
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
EMU_PER_INCH = 914400


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def center_x(self) -> float:
        return self.x + self.w / 2

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)


def read_xml(zf: zipfile.ZipFile, path: str) -> ET.Element:
    return ET.fromstring(zf.read(path))


def rels_path_for(part_path: str) -> str:
    folder, name = posixpath.split(part_path)
    return posixpath.join(folder, "_rels", f"{name}.rels")


def load_rels(zf: zipfile.ZipFile, part_path: str) -> dict[str, str]:
    rels_path = rels_path_for(part_path)
    if rels_path not in zf.namelist():
        return {}
    root = read_xml(zf, rels_path)
    base = posixpath.dirname(part_path)
    out: dict[str, str] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        if rel_id:
            out[rel_id] = posixpath.normpath(posixpath.join(base, target))
    return out


def slide_order(zf: zipfile.ZipFile) -> list[str]:
    rels = load_rels(zf, "ppt/presentation.xml")
    root = read_xml(zf, "ppt/presentation.xml")
    ordered = []
    for node in root.findall(".//p:sldId", NS):
        rid = node.attrib.get(f"{{{NS['r']}}}id")
        if rid in rels:
            ordered.append(rels[rid])
    return ordered


def slide_size(zf: zipfile.ZipFile) -> tuple[float, float]:
    root = read_xml(zf, "ppt/presentation.xml")
    sld_sz = root.find(".//p:sldSz", NS)
    if sld_sz is None:
        return 13.333, 7.5
    return int(sld_sz.attrib["cx"]) / EMU_PER_INCH, int(sld_sz.attrib["cy"]) / EMU_PER_INCH


def shape_box(node: ET.Element) -> Box | None:
    xfrm = node.find(".//a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return Box(
        int(off.attrib.get("x", 0)) / EMU_PER_INCH,
        int(off.attrib.get("y", 0)) / EMU_PER_INCH,
        int(ext.attrib.get("cx", 0)) / EMU_PER_INCH,
        int(ext.attrib.get("cy", 0)) / EMU_PER_INCH,
    )


def node_name(node: ET.Element) -> str:
    c_nv_pr = node.find(".//p:cNvPr", NS)
    return c_nv_pr.attrib.get("name", "") if c_nv_pr is not None else ""


def pic_descr(node: ET.Element) -> str:
    c_nv_pr = node.find(".//p:cNvPr", NS)
    return c_nv_pr.attrib.get("descr", "") if c_nv_pr is not None else ""


def text_of(node: ET.Element) -> str:
    return "".join(t.text or "" for t in node.findall(".//a:t", NS)).strip()


def max_font_size_pt(node: ET.Element) -> float:
    sizes = []
    for rpr in node.findall(".//a:defRPr", NS) + node.findall(".//a:rPr", NS):
        if "sz" in rpr.attrib:
            sizes.append(int(rpr.attrib["sz"]) / 100)
    return max(sizes) if sizes else 18.0


def overlap_area(a: Box, b: Box) -> float:
    x = max(0.0, min(a.right, b.right) - max(a.x, b.x))
    y = max(0.0, min(a.bottom, b.bottom) - max(a.y, b.y))
    return x * y


def image_size_from_bytes(data: bytes) -> tuple[int, int] | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        idx = 2
        while idx + 9 < len(data):
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            idx += 2
            if marker in (0xD8, 0xD9):
                continue
            length = int.from_bytes(data[idx : idx + 2], "big")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h = int.from_bytes(data[idx + 3 : idx + 5], "big")
                w = int.from_bytes(data[idx + 5 : idx + 7], "big")
                return w, h
            idx += length
    return None


def pic_target(node: ET.Element, rels: dict[str, str]) -> str | None:
    blip = node.find(".//a:blip", NS)
    if blip is None:
        return None
    rid = blip.attrib.get(f"{{{NS['r']}}}embed")
    return rels.get(rid) if rid else None


def likely_text_overflows(text: str, box: Box, font_size: float) -> bool:
    if not text or box.w <= 0 or box.h <= 0:
        return False
    avg_char_w = max(0.07, font_size * 0.0062)
    chars_per_line = max(4, int(box.w / avg_char_w))
    manual_lines = text.count("\n") + 1
    wrapped_lines = sum(max(1, math.ceil(len(line) / chars_per_line)) for line in text.splitlines() or [text])
    line_count = max(manual_lines, wrapped_lines)
    required_h = line_count * font_size / 72 * 1.15
    return required_h > box.h * 1.15


def inspect_pptx(path: Path, header_safe_top_in: float, fail_on_warning: bool) -> dict:
    findings: list[dict] = []
    with zipfile.ZipFile(path) as zf:
        width, height = slide_size(zf)
        slides = slide_order(zf)
        for idx, slide_path in enumerate(slides, 1):
            root = read_xml(zf, slide_path)
            rels = load_rels(zf, slide_path)
            nodes = list(root.findall(".//p:spTree/*", NS))
            text_shapes = []
            pictures = []
            for node in nodes:
                box = shape_box(node)
                if box is None:
                    continue
                label = node_name(node) or pic_descr(node) or node.tag.rsplit("}", 1)[-1]
                if box.x < -0.01 or box.y < -0.01 or box.right > width + 0.01 or box.bottom > height + 0.01:
                    findings.append({"slide": idx, "level": "error", "code": "off-slide-object", "object": label})
                if node.tag == f"{{{NS['p']}}}sp":
                    text = text_of(node)
                    if text:
                        size = max_font_size_pt(node)
                        text_shapes.append((label, text, box, size))
                        if size >= 24 and box.y < header_safe_top_in and idx != 1:
                            findings.append(
                                {
                                    "slide": idx,
                                    "level": "error",
                                    "code": "title-in-header-safe-zone",
                                    "object": label,
                                    "text": text[:60],
                                }
                            )
                        if likely_text_overflows(text, box, size):
                            findings.append(
                                {
                                    "slide": idx,
                                    "level": "warning" if not fail_on_warning else "error",
                                    "code": "possible-text-overflow",
                                    "object": label,
                                    "text": text[:60],
                                }
                            )
                elif node.tag == f"{{{NS['p']}}}pic":
                    pictures.append((label, box, node))
                    target = pic_target(node, rels)
                    if target and target in zf.namelist():
                        natural = image_size_from_bytes(zf.read(target))
                        if natural:
                            src_ratio = natural[0] / natural[1]
                            box_ratio = box.w / box.h if box.h else src_ratio
                            if abs(src_ratio - box_ratio) / src_ratio > 0.08:
                                findings.append(
                                    {
                                        "slide": idx,
                                        "level": "error",
                                        "code": "image-aspect-distorted",
                                        "object": label,
                                        "source_ratio": round(src_ratio, 3),
                                        "box_ratio": round(box_ratio, 3),
                                    }
                                )

            for a_i, (a_label, a_text, a_box, _a_size) in enumerate(text_shapes):
                for b_label, b_text, b_box, _b_size in text_shapes[a_i + 1 :]:
                    area = overlap_area(a_box, b_box)
                    if area > min(a_box.area, b_box.area) * 0.08:
                        findings.append(
                            {
                                "slide": idx,
                                "level": "error",
                                "code": "text-box-overlap",
                                "objects": [a_label, b_label],
                                "texts": [a_text[:40], b_text[:40]],
                            }
                        )

            content_pics = [(label, box) for label, box, _node in pictures if box.y > header_safe_top_in]
            if len(content_pics) >= 3:
                tops = [box.y for _label, box in content_pics]
                heights = [box.h for _label, box in content_pics]
                centers = sorted(box.center_x for _label, box in content_pics)
                gaps = [centers[i + 1] - centers[i] for i in range(len(centers) - 1)]
                repeated_group = min(heights) > 0 and max(heights) / min(heights) < 1.25
                if repeated_group:
                    if max(tops) - min(tops) > 0.10:
                        findings.append({"slide": idx, "level": "error", "code": "picture-group-top-misaligned"})
                    if max(heights) - min(heights) > 0.14:
                        findings.append({"slide": idx, "level": "warning" if not fail_on_warning else "error", "code": "picture-group-height-mismatch"})
                    if len(gaps) >= 2 and max(gaps) - min(gaps) > 0.35:
                        findings.append({"slide": idx, "level": "warning" if not fail_on_warning else "error", "code": "picture-group-uneven-spacing"})

    errors = [item for item in findings if item["level"] == "error"]
    return {"ok": not errors, "error_count": len(errors), "finding_count": len(findings), "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check PPTX layout geometry")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--header-safe-top-in", type=float, default=0.9)
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = inspect_pptx(args.pptx, args.header_safe_top_in, args.fail_on_warning)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "ok" if result["ok"] else "failed"
        print(f"[{status}] {result['error_count']} error(s), {result['finding_count']} finding(s)")
        for item in result["findings"]:
            print(json.dumps(item, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
