"""命令行入口：download / extract / all。"""
import argparse
import sys
from pathlib import Path

from prismlauncher_download.config import DEFAULT_EXTRACT_FILE, DEFAULT_OUTPUT_DIR, EXTRACT_TO_FILE

from .downloader import download_entry
from .parser import parse_entries


def _run_download(input_path: Path, output_dir: Path) -> int:
    text = input_path.read_text(encoding="utf-8")
    targets = [e for e in parse_entries(text) if e.need_download]
    if not targets:
        print("没有需要下载的条目（标记为 ✘）。")
        return 0

    print(f"共 {len(targets)} 个待下载条目 → {output_dir.resolve()}")
    success = fail = 0
    for entry in targets:
        if download_entry(entry, output_dir):
            success += 1
        else:
            fail += 1
    print(f"\n完成：成功 {success}，失败 {fail}")
    return 0 if fail == 0 else 1


def _cmd_download(args: argparse.Namespace) -> int:
    return _run_download(args.input, args.output_dir)


def _cmd_extract(args: argparse.Namespace) -> int:
    from .prism_extractor import extract_blocked_mods_text

    text = extract_blocked_mods_text()
    if not text:
        print("未提取到任何文本。", file=sys.stderr)
        return 1
    args.output.write_text(text, encoding="utf-8")
    print(f"已写入 {args.output}")
    return 0


def _cmd_all(args: argparse.Namespace) -> int:
    from .prism_extractor import extract_blocked_mods_text

    text = extract_blocked_mods_text()
    if not text:
        print("提取失败。", file=sys.stderr)
        return 1
    if EXTRACT_TO_FILE:
        args.output.write_text(text, encoding="utf-8")
        print(f"已写入 {args.output}\n")
    print(f"共 {len(parse_entries(text))} 个条目 → {text}")
    return _run_download(args.output, args.output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prismlauncher-downloader",
        description="获取prismlauncher被屏蔽的模组列表，并下载这些模组",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_dl = sub.add_parser("download", help="从文本文件下载")
    p_dl.add_argument("input", type=Path, help="包含哈希值的文本文件")
    p_dl.add_argument("-d", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p_dl.set_defaults(func=_cmd_download)

    p_ex = sub.add_parser("extract", help="从 PrismLauncher 弹窗提取文本")
    p_ex.add_argument("-o", "--output", type=Path, default=DEFAULT_EXTRACT_FILE)
    p_ex.set_defaults(func=_cmd_extract)

    p_all = sub.add_parser("all", help="提取 + 下载一步完成")
    p_all.add_argument("-o", "--output", type=Path, default=DEFAULT_EXTRACT_FILE)
    p_all.add_argument("-d", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p_all.set_defaults(func=_cmd_all)

    args = parser.parse_args(argv)
    return args.func(args)