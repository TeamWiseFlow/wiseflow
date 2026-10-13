#!/usr/bin/env python3
"""Validate the WorkBuddy expert's supported schema and packaged resources."""

import argparse
import json
from pathlib import Path
import re
import struct
import sys


DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "expert"
RESOURCE_DIRS = (".codebuddy-plugin", "agents", "avatars", "skills")
NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def local_path(root, value, *, directory=False):
    require(isinstance(value, str) and value, "resource path must be a nonempty string")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts, f"resource escapes package: {value}")
    target = (root / path).resolve()
    require(target.is_relative_to(root.resolve()), f"resource escapes package: {value}")
    require(target.is_dir() if directory else target.is_file(), f"missing resource: {value}")
    return target


def frontmatter(file):
    text = file.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"missing frontmatter: {file.name}")
    header, separator, body = text[4:].partition("\n---\n")
    require(bool(separator) and bool(body.strip()), f"missing frontmatter end or instructions: {file.name}")
    require(not re.search(r"^tools\s*:", header, re.M), f"expert cannot declare custom tools: {file.name}")
    return header


def scalar(header, field):
    match = re.search(rf"^{re.escape(field)}: +([^\n]+)$", header, re.M)
    require(match is not None, f"missing scalar field: {field}")
    value = match.group(1).strip()
    require(value not in (">", "|", "null", "~") and not value.startswith(("[", "{")), f"use a nonempty scalar for {field}")
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValidationError(f"invalid quoted scalar: {field}") from error
    elif value.startswith("'"):
        require(value.endswith("'"), f"invalid quoted scalar: {field}")
        value = value[1:-1].replace("''", "'")
    require(isinstance(value, str) and bool(value.strip()), f"empty scalar: {field}")
    return value


def localized(value, field):
    require(isinstance(value, dict), f"{field} must have zh/en fields")
    for language in ("zh", "en"):
        require(isinstance(value.get(language), str) and bool(value[language].strip()), f"missing {field}.{language}")


def files_for_package(root):
    files = [local_path(root, "README.md")]
    if (root / 'LICENSE').is_file():
        files.append(root / 'LICENSE')
    for directory in RESOURCE_DIRS:
        location = local_path(root, directory, directory=True)
        for path in sorted(location.rglob("*")):
            relative = path.relative_to(root)
            if any(part in {"node_modules", "__pycache__"} or part.startswith(".") for part in relative.parts[1:]):
                continue
            require(not path.is_symlink(), f"symlinks cannot be packaged: {relative}")
            if path.is_file() and (path.name in {'LICENSE', 'NOTICE'} or path.suffix in {".md", ".json", ".mjs", ".js", ".ts", ".sh", ".py", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".html", ".css", ".txt", ".sql", ".proto", ".toml", ".yaml", ".yml", ".woff", ".woff2", ".ttf", ".otf", ".mp3"}):
                files.append(path)
    return sorted(files)


def validate(root):
    root = root.resolve()
    config_path = local_path(root, ".codebuddy-plugin/plugin.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValidationError("plugin.json is not valid JSON") from error
    require(isinstance(config, dict), "plugin.json must be an object")
    require(NAME.fullmatch(config.get("name", "")), "invalid plugin name")
    require(re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", config.get("version", "")), "invalid version")
    require(isinstance(config.get("description"), str) and re.search(r"[A-Za-z]", config["description"]), "English description required")
    author = config.get("author", {})
    require(isinstance(author, dict) and bool(author.get("name")), "author.name required")
    require(isinstance(author.get("email"), str) and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", author["email"]), "author.email required")
    require(config.get("expertType") == "agent" and "teamInfo" not in config, "first release must be a single expert")
    require(config.get("plugin") == config["name"], "plugin must match name")
    require(config.get("categoryId") == "05-MarketingGrowth", "expected marketing/growth category")
    for field in ("displayName", "profession", "displayDescription", "defaultInitPrompt"):
        localized(config.get(field), field)
    require(40 <= len(config["displayDescription"]["zh"]) <= 50, "Chinese display description must contain 40-50 characters")
    for field in ("tags", "quickPrompts"):
        require(isinstance(config.get(field), list) and len(config[field]) == 3, f"{field} must contain exactly 3 entries")
        for item in config[field]:
            localized(item, field)
    require(config["defaultInitPrompt"] == config["quickPrompts"][0], "defaultInitPrompt must match first quickPrompt")
    require(isinstance(config.get("agents"), list) and len(config["agents"]) == 1, "one agent definition required")
    agent = local_path(root, config["agents"][0])
    header = frontmatter(agent)
    require(agent.parent == root / "agents", "agent must be stored under agents/")
    require(scalar(header, "name") == config.get("agentName") == agent.stem, "agent name mismatch")
    scalar(header, "description")
    for field in ("displayName", "profession"):
        match = re.search(rf"^{field}:\n((?: +[^\n]+\n?)+)", header, re.M)
        require(match is not None, f"missing agent {field} mapping")
        for language in ("zh", "en"):
            line = re.search(rf"^  {language}: +(.+)$", match.group(1), re.M)
            require(line is not None, f"missing agent {field}.{language}")
            require(line.group(1).strip().strip('"') == config[field][language], f"agent {field}.{language} mismatch")
    require(isinstance(config.get("skills"), list) and config["skills"], "skills required")
    names = set()
    for resource in config["skills"]:
        directory = local_path(root, resource, directory=True)
        require(directory.parent == root / "skills", "skill must be stored under skills/")
        skill = frontmatter(local_path(directory, "SKILL.md"))
        name = scalar(skill, "name")
        require(NAME.fullmatch(name) and name == directory.name and name not in names, "invalid or duplicate skill name")
        names.add(name)
        for field in ("description", "description_zh", "description_en", "version", "author"):
            scalar(skill, field)
        require(scalar(skill, "version") == config["version"], "skill version mismatch")
    declared = re.search(r"^skills:\n((?:  - [^\n]+\n?)+)", header, re.M)
    require(declared is not None, "agent preload skills required")
    preloaded = re.findall(r"^  - (.+)$", declared.group(1), re.M)
    require(len(preloaded) == len(set(preloaded)) and set(preloaded).issubset(names), "agent preload skills must be unique and packaged")
    avatar = local_path(root, config.get("avatar"))
    data = avatar.read_bytes()
    require(len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n", "PNG avatar required")
    require(struct.unpack(">II", data[16:24]) == (512, 512), "avatar must be 512x512")
    require(len(data) <= 500 * 1024, "avatar exceeds 500KB")
    files = files_for_package(root)
    for file in files:
        if file.suffix != ".md":
            continue
        text = re.sub(r'```.*?```', '', file.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r'`[^`\n]*`', '', text)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if re.match(r"(?:https?://|#)", target):
                continue
            relative = target.split("#", 1)[0]
            destination = (file.parent / relative).resolve()
            require(destination.is_relative_to(root) and destination in files, f"broken or unpackaged local reference in {file.name}: {target}")
    require(len(files) > 4, "empty expert package")
    native = root / '.codebuddy-plugin/native-index.json'
    if native.is_file():
        import hashlib
        index = json.loads(native.read_text())
        require(index['version'] == config['version'], 'native version mismatch')
        require(set(index['skills']).issubset(names), 'native skills must be declared')
        for record in index['files']:
            path = local_path(root, 'skills/' + record['target'])
            require(path in files, f"native resource not packaged: {record['target']}")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], f"native export out of sync: {record['target']}")
            if root == DEFAULT_SOURCE.resolve():
                source = DEFAULT_SOURCE.parents[1] / record['source']
                require(source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == record['source_sha256'], f"native source changed; run sync_native.py: {record['source']}")
        allowed = {record['target'] for record in index['files']}
        for file in files:
            relative = file.relative_to(root).parts
            if len(relative) >= 3 and relative[0] == 'skills' and relative[1] in index['skills']:
                require('/'.join(relative[1:]) in allowed, f"unexpected native file: {file.relative_to(root)}")
        for command, path in index['commands'].items():
            require(local_path(root, 'skills/' + path) in files, f"missing native wrapper: {command}")
        product = json.loads(local_path(root, '.codebuddy-plugin/product.json').read_text())
        require(product['relay_base_url'] == index['relay_base_url'] == 'https://relay.openclaw-for-business.com', 'default official relay changed')
        contact = local_path(root, product['contact_image'])
        require(contact in files, 'contact QR image must be packaged')
        for record in index['assets']:
            path = local_path(root, record['target'])
            require(path in files and hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], 'brand asset changed: ' + record['target'])
            if root == DEFAULT_SOURCE.resolve():
                source = DEFAULT_SOURCE.parents[1] / record['source']
                require(hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256'], 'source brand asset changed; run sync_native.py')
        persona = index['persona']
        require(hashlib.sha256(local_path(root, persona['target']).read_bytes()).hexdigest() == persona['sha256'], 'agent changed; run sync_native.py')
        if root == DEFAULT_SOURCE.resolve():
            for record in persona['sources']:
                require(hashlib.sha256((DEFAULT_SOURCE.parents[1] / record['source']).read_bytes()).hexdigest() == record['sha256'], 'native persona changed; run sync_native.py')
        require('expert-wx-channel' not in names and 'xiaobei-operations' not in names, 'removed platform or generic skill still declared')
        require('wx-mp-hunter' not in names and not (root / 'skills/wx-mp-hunter').exists(), 'removed WeChat hunter cannot be packaged')
        banned = re.compile(r'\b(?:douyin-publish|douyin-engagement|wx-mp-engagement|wx-channel-engagement|wechat-channels-publish|wx-channel-style-profiler|wx-mp-hunter homepage)\s+(?:check|login|video|note|fetch|fetch-all|daily|get-link|report|build)\b')
        for file in files:
            if file.suffix in {'.md', '.py', '.mjs', '.ts', '.sh', '.js'}:
                text = file.read_text()
                require('wx-mp-hunter' not in text and 'wx_mp_hunter' not in text, 'removed WeChat hunter still referenced: ' + str(file.relative_to(root)))
                require('relay.xiaobei-workbuddy-for-business.com' not in text, 'relay domain was rewritten: ' + str(file.relative_to(root)))
                if file.suffix == '.md':
                    require(not banned.search(text), 'removed command still instructed: ' + str(file.relative_to(root)))
    return config, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    try:
        config, files = validate(args.source)
    except (ValidationError, OSError, TypeError) as error:
        print(json.dumps({"success": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"success": True, "name": config["name"], "version": config["version"], "files": len(files)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
