#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CurseForge CDN 链接补全 + 下载 + SHA1 校验
- 只下载文本中标记为 “✘ 未找到” 的条目
- 下载完成后按文本中的哈希值做 SHA1 校验
"""

import argparse
import hashlib
import os
import re
import sys
import time
import urllib.request
import urllib.error

# 匹配每个条目：
#   文件名：URL
#   哈希值：hash ✔/✘ 状态
ENTRY_PATTERN = re.compile(
    r'(?P<filename>[^\s：:]+\.jar)(?:[：:]\s*|\s+)'
    r'(?P<url>https?://\S+/download/(?P<fileid>\d+))[^\n]*\n'
    r'\s*哈希值[：:]\s*(?P<hash>[0-9a-fA-F]{40})\s*'
    r'(?P<mark>✔|✘)[^\n]*',
    re.IGNORECASE
)

USER_AGENT = "Mozilla/5.0 (compatible; CFDownloader/1.1)"
MAX_RETRIES = 3
CHUNK_SIZE = 64 * 1024  # 64 KiB


# ---------- 解析 ----------

def parse_entries(text):
    """解析所有条目，返回 [(filename, fileid, sha1, need_download), ...]，已去重"""
    seen = set()
    results = []
    for m in ENTRY_PATTERN.finditer(text):
        filename = m.group('filename')
        fileid = m.group('fileid')
        filehash = m.group('hash').lower()
        need = (m.group('mark') == '✘')
        key = (filename, fileid)
        if key in seen:
            continue
        seen.add(key)
        results.append((filename, fileid, filehash, need))
    return results


def build_cdn_url(filename, fileid):
    fid = int(fileid)
    return f"https://edge.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{filename}"


# ---------- 哈希 ----------

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------- 下载 ----------

def download_file(url, dest_path, filename, expected_sha1=None):
    """下载并校验 SHA1；成功返回 True"""
    # 目标已存在：先校验，匹配则跳过，不匹配则删掉重下
    if os.path.exists(dest_path):
        if expected_sha1 and sha1_file(dest_path) == expected_sha1:
            print(f"[跳过] 已存在且哈希匹配: {filename}")
            return True
        print(f"[重下] 已存在但哈希不匹配（或为空）: {filename}")
        try:
            os.remove(dest_path)
        except OSError as e:
            print(f"[错误] 无法删除旧文件: {e}")
            return False

    tmp_path = dest_path + ".part"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
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
                            speed = downloaded / 1024 / max(time.time() - start, 0.001)
                            print(
                                f"\r  {filename}  {pct:5.1f}%  "
                                f"{downloaded/1024/1024:.1f}/{total/1024/1024:.1f} MB  "
                                f"{speed:.0f} KB/s",
                                end="", flush=True
                            )
                print()  # 换行

            # 大小校验（若服务器给了 Content-Length）
            if total > 0 and downloaded != total:
                raise IOError(f"下载不完整 ({downloaded}/{total})")

            # 哈希校验
            if expected_sha1:
                actual = sha1_file(tmp_path)
                if actual != expected_sha1:
                    raise IOError(
                        f"哈希不匹配 期望={expected_sha1} 实际={actual}"
                    )

            os.replace(tmp_path, dest_path)
            print(f"[完成] {filename}" + (f"  SHA1 校验通过" if expected_sha1 else ""))
            return True

        except (urllib.error.HTTPError, urllib.error.URLError,
                TimeoutError, IOError, OSError) as e:
            print(f"\n[失败] 第 {attempt}/{MAX_RETRIES} 次: {filename} -> {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
        except KeyboardInterrupt:
            print("\n[中断] 用户取消")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False

    print(f"[放弃] 下载失败: {filename}")
    return False