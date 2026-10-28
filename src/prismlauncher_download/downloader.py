"""CurseForge CDN 下载 + 校验。"""
import time
import urllib.error
import urllib.request
from pathlib import Path

from .config import CHUNK_SIZE, MAX_RETRIES, REQUEST_TIMEOUT, USER_AGENT
from .hasher import sha1_file
from .models import Entry


def download_entry(entry: Entry, dest_dir: Path) -> bool:
    """下载并校验单个条目，成功返回 True。"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    return _download(
        url=entry.cdn_url,
        dest_path=dest_dir / entry.safe_filename,
        filename=entry.filename,
        expected_sha1=entry.sha1,
    )


def _download(
    url: str,
    dest_path: Path,
    filename: str,
    expected_sha1: str | None = None,
) -> bool:
    if dest_path.exists():
        if expected_sha1 and sha1_file(dest_path) == expected_sha1:
            print(f"[跳过] 已存在且哈希匹配: {filename}")
            return True
        print(f"[重下] 已存在但哈希不匹配: {filename}")
        try:
            dest_path.unlink()
        except OSError as e:
            print(f"[错误] 无法删除旧文件: {e}")
            return False

    tmp_path = dest_path.with_suffix(dest_path.suffix + ".part")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                start = time.time()
                with open(tmp_path, "wb") as f:
                    while True:
                        chunk = resp.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = downloaded * 100 / total
                            speed = downloaded / 1024 / max(
                                time.time() - start, 0.001
                            )
                            print(
                                f"\r  {filename}  {pct:5.1f}%  "
                                f"{downloaded/1024/1024:.1f}/{total/1024/1024:.1f} MB  "
                                f"{speed:.0f} KB/s",
                                end="",
                                flush=True,
                            )
                print()

            if total > 0 and downloaded != total:
                raise IOError(f"下载不完整 ({downloaded}/{total})")

            if expected_sha1:
                actual = sha1_file(tmp_path)
                if actual != expected_sha1:
                    raise IOError(
                        f"哈希不匹配 期望={expected_sha1} 实际={actual}"
                    )

            tmp_path.replace(dest_path)
            suffix = "  SHA1 校验通过" if expected_sha1 else ""
            print(f"[完成] {filename}{suffix}")
            return True

        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            IOError,
            OSError,
        ) as e:
            print(f"\n[失败] 第 {attempt}/{MAX_RETRIES} 次: {filename} -> {e}")
            tmp_path.unlink(missing_ok=True)
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
        except KeyboardInterrupt:
            print("\n[中断] 用户取消")
            tmp_path.unlink(missing_ok=True)
            return False

    print(f"[放弃] 下载失败: {filename}")
    return False