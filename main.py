"""
兼容入口：`uv run python main.py download mods.txt -d ./mods`
修改config.py中的DEFAULT_OUTPUT_DIR即可改变默认下载目录。
快速使用：`uv run python main.py all`，会自动提取被屏蔽的mod列表并下载。
"""
from prismlauncher_download.cli import main

if __name__ == "__main__":
    raise SystemExit(main())