"""Read publication text or an explicit @UTF-8-file reference."""
from pathlib import Path


class PublishTextError(ValueError):
    """A requested publication text file cannot be read."""


def read_publish_text(value: str) -> str:
    if not value.startswith('@'):
        return value
    if len(value) == 1:
        raise PublishTextError('CONTENT_FILE_INVALID: @ 后必须提供正文文件路径')
    path = Path(value[1:]).expanduser()
    try:
        if not path.is_file():
            raise PublishTextError(f'CONTENT_FILE_INVALID: 正文文件不存在或不是普通文件：{path}')
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        raise PublishTextError(f'CONTENT_FILE_INVALID: 无法读取 UTF-8 正文文件：{path}') from exc
