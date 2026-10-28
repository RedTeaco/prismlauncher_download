"""CurseForge CDN 链接补全 + 下载 + SHA1 校验。"""
from .hasher import sha1_file
from .models import Entry
from .parser import parse_entries

__version__ = "0.1.0"
__all__ = ["Entry", "parse_entries", "sha1_file"]