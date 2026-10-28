"""数据模型。"""
from dataclasses import dataclass
from pathlib import Path

from .config import CDN_URL_TEMPLATE


@dataclass(frozen=True)
class Entry:
    """一条模组下载记录。"""

    filename: str
    fileid: str
    sha1: str
    need_download: bool

    @property
    def cdn_url(self) -> str:
        fid = int(self.fileid)
        return CDN_URL_TEMPLATE.format(
            major=fid // 1000,
            minor=fid % 1000,
            filename=self.filename,
        )

    @property
    def safe_filename(self) -> str:
        """防止文件名携带路径分隔符导致路径穿越。"""
        return Path(self.filename).name