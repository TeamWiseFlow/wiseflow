#!/usr/bin/env python3
"""
Apple 国区 ICP 豁免申请附件生成器
生成符合 Apple 要求的正式申请附件 PDF

前置依赖：
  - Python 3.8+
  - reportlab (pip install reportlab)
  - 中文字体包（如 fonts-wqy-zenhei），需提前安装
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


def get_today_chinese():
    """返回今天的中文日期，如 2024年12月01日"""
    today = datetime.today()
    return f"{today.year}年{today.month:02d}月{today.day:02d}日"


def generate_pdf(team_id: str, name: str, app_id: str, date: str, output_path: str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
    except ImportError:
        print("错误：缺少 reportlab 库，请运行 pip install reportlab", file=sys.stderr)
        sys.exit(1)

    # Escape user input to prevent reportlab XML markup injection
    team_id = escape(team_id)
    name = escape(name)
    app_id = escape(app_id)
    date = escape(date)

    # Try to register a CJK font for Chinese characters
    font_name = "Helvetica"  # fallback
    bold_font_name = "Helvetica-Bold"

    cjk_fonts = [
        ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WQYZenHei"),
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WQYMicroHei"),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "NotoSansCJK"),
        ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "NotoSansCJK"),
        ("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", "NotoSansCJK"),
    ]

    for font_path, font_reg_name in cjk_fonts:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_reg_name, font_path))
                font_name = font_reg_name
                bold_font_name = font_reg_name  # use same font for bold too
                break
            except Exception:
                continue

    if font_name == "Helvetica":
        print(
            "警告：未找到中文字体，PDF 中的中文可能无法正常显示。\n"
            "请安装中文字体包，例如：sudo apt-get install fonts-wqy-zenhei",
            file=sys.stderr,
        )

    # Page layout
    page_width, page_height = A4
    margin = 30 * mm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        title="Apple 国区 ICP 豁免申请附件",
        author=name,
    )

    # Styles
    def style(name_s, **kwargs):
        defaults = dict(fontName=font_name, fontSize=11, leading=18, spaceAfter=0, spaceBefore=0)
        defaults.update(kwargs)
        return ParagraphStyle(name_s, **defaults)

    title_style = style("Title", fontName=bold_font_name, fontSize=16, leading=26,
                        alignment=TA_CENTER, spaceBefore=0, spaceAfter=8)
    subtitle_style = style("Subtitle", fontSize=11, alignment=TA_CENTER, spaceAfter=4)
    section_header_style = style("SectionHeader", fontName=bold_font_name, fontSize=12,
                                  leading=20, spaceBefore=14, spaceAfter=4)
    body_style = style("Body", fontSize=11, leading=20, alignment=TA_JUSTIFY)
    info_key_style = style("InfoKey", fontName=bold_font_name, fontSize=11, leading=20)
    info_val_style = style("InfoVal", fontSize=11, leading=20)
    declaration_style = style("Declaration", fontSize=11, leading=22, alignment=TA_JUSTIFY)
    sign_label_style = style("SignLabel", fontName=bold_font_name, fontSize=11, leading=22)
    sign_val_style = style("SignVal", fontSize=11, leading=22)
    footer_style = style("Footer", fontSize=9, leading=14, alignment=TA_CENTER,
                          textColor=colors.grey)

    story = []

    # ── Title ──────────────────────────────────────────────
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Apple 国区 ICP 豁免申请附件", title_style))
    story.append(Paragraph("App Store Connect 中国大陆地区 ICP 备案例外申请", subtitle_style))
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black))
    story.append(Spacer(1, 5 * mm))

    # ── 账户信息 ──────────────────────────────────────────
    story.append(Paragraph("一、账户信息", section_header_style))

    info_data = [
        [Paragraph("Team ID（团队 ID）", info_key_style),
         Paragraph(f"：{team_id}", info_val_style)],
        [Paragraph("账户持有人法定姓名", info_key_style),
         Paragraph(f"：{name}", info_val_style)],
    ]
    info_table = Table(info_data, colWidths=[65 * mm, None])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(info_table)

    # ── App 信息 ───────────────────────────────────────────
    story.append(Paragraph("二、App 信息", section_header_style))

    app_data = [
        [Paragraph("App ID（应用 ID）", info_key_style),
         Paragraph(f"：{app_id}", info_val_style)],
    ]
    app_table = Table(app_data, colWidths=[65 * mm, None])
    app_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(app_table)

    # ── 声明 ──────────────────────────────────────────────
    story.append(Paragraph("三、申请声明", section_header_style))

    declarations = [
        f"本人 {name}，Team ID 为 {team_id}，现就 App ID 为 {app_id} 的独立应用，向 Apple 申请中国大陆地区 ICP 备案豁免例外批准。本人声明如下：",
        "",
        "1. 本人有意就上述独立 App 向 Apple 申请例外批准。",
        "",
        "2. 本人已充分了解并遵守所有相关法律法规及 Apple 的相关政策要求，确认本 App 属于以下豁免情形之一：",
        "    • 完全离线应用，不进行任何网络通信；或",
        "    • 仅通过 iCloud 同步数据，不连接其他任何服务器；或",
        "    • 仅通过 Apple 内购（IAP）进行交易，无自建支付系统及其他联网功能。",
        "",
        "3. 本人确认所提交的所有信息真实、准确、完整，与 App Store Connect 账户信息完全一致。",
        "",
        "4. 如存在任何虚假陈述或误导信息，本人愿意承担由此产生的全部法律责任。",
    ]

    for line in declarations:
        if line == "":
            story.append(Spacer(1, 3 * mm))
        else:
            story.append(Paragraph(line, declaration_style))

    # ── 签署 ──────────────────────────────────────────────
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#aaaaaa")))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("四、签署", section_header_style))
    story.append(Spacer(1, 2 * mm))

    # Signature area as a table
    sig_line = "_" * 20
    sign_data = [
        [Paragraph("手写签名：", sign_label_style),
         Paragraph(sig_line, sign_val_style),
         Paragraph("", sign_val_style)],
        [Paragraph("正楷姓名：", sign_label_style),
         Paragraph(name, sign_val_style),
         Paragraph("", sign_val_style)],
        [Paragraph("日　　期：", sign_label_style),
         Paragraph(date, sign_val_style),
         Paragraph("", sign_val_style)],
    ]
    sign_table = Table(sign_data, colWidths=[30 * mm, 80 * mm, None])
    sign_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sign_table)

    story.append(Spacer(1, 10 * mm))

    # ── 注意事项 ─────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#aaaaaa")))
    story.append(Spacer(1, 4 * mm))
    notice_style = style("Notice", fontSize=9, leading=15, textColor=colors.HexColor("#555555"),
                          alignment=TA_JUSTIFY)
    story.append(Paragraph(
        "【注意事项】本附件仅供 Apple App Store Connect ICP 豁免申请使用。"
        "请在手写签名后将本文件扫描或拍照，作为附件上传至 App Store Connect 申诉流程中。"
        "如有多个 App 需要申请，请为每个 App 单独准备并提交一份附件。",
        notice_style
    ))

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        f"本文件由 Apple ICP 豁免申请助手自动生成  ·  生成日期：{date}",
        footer_style
    ))

    doc.build(story)
    print(f"PDF 生成成功：{output_path}")


def main():
    parser = argparse.ArgumentParser(description="生成 Apple 国区 ICP 豁免申请附件 PDF")
    parser.add_argument("--team-id", required=True, help="Team ID（团队 ID）")
    parser.add_argument("--name", required=True, help="账户持有人法定姓名")
    parser.add_argument("--app-id", required=True, help="App ID")
    parser.add_argument("--date", default="", help="申请日期（留空则使用今天）")
    parser.add_argument("--output", default="",
                        help="输出路径（留空则保存到当前目录）")
    args = parser.parse_args()

    date = args.date if args.date else get_today_chinese()

    output_path = args.output
    if not output_path:
        output_path = str(Path.cwd() / "ICP豁免申请附件.pdf")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_pdf(args.team_id, args.name, args.app_id, date, output_path)


if __name__ == "__main__":
    main()
