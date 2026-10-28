import os
from prismlauncher_download.cf_download import build_cdn_url, download_file, parse_entries
from prismlauncher_download.extract_prism_dialog import extract_blocked_mods_text


def main():
    text = extract_blocked_mods_text()
    print(f"[DEBUG] text:{text}")
    if text:
        entries = parse_entries(text)
        print(f"[DEBUG] entries:{entries}")
        print(f"解析到 {len(entries)} 个条目")
        output_dir = r"E:/Minecraft/prism Launcher/mods"
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, fileid, filehash, need in entries:
            if not need:
                continue
            url = build_cdn_url(filename,fileid)
            dest = os.path.join(output_dir, filename)
            print(f"开始处理{filename}")
            download_file(url, dest, filename, expected_sha1=filehash)

if __name__ == '__main__':
    main()