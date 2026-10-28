"""解析包含 CurseForge 下载信息的文本。"""
import re

from .models import Entry

ENTRY_PATTERN = re.compile(
    r'(?P<filename>[^\s：:]+\.jar)(?:[：:]\s*|\s+)'
    r'(?P<url>https?://\S+/download/(?P<fileid>\d+))[^\n]*\n'
    r'\s*哈希值[：:]\s*(?P<hash>[0-9a-fA-F]{40})\s*'
    r'(?P<mark>✔|✘)[^\n]*',
    re.IGNORECASE,
)


def parse_entries(text: str) -> list[Entry]:
    """解析文本，返回去重后的条目列表。"""
    seen: set[tuple[str, str]] = set()
    results: list[Entry] = []
    for m in ENTRY_PATTERN.finditer(text):
        key = (m.group("filename"), m.group("fileid"))
        if key in seen:
            continue
        seen.add(key)
        results.append(
            Entry(
                filename=m.group("filename"),
                fileid=m.group("fileid"),
                sha1=m.group("hash").lower(),
                need_download=(m.group("mark") == "✘"),
            )
        )
    return results