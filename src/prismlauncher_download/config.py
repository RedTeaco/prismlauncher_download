from pathlib import Path

"""项目常量集中管理。"""
USER_AGENT = "Mozilla/5.0 (compatible; CFDownloader/1.1)"
MAX_RETRIES = 3
CHUNK_SIZE = 64 * 1024  # 64 KiB
REQUEST_TIMEOUT = 30
CDN_URL_TEMPLATE = "https://edge.forgecdn.net/files/{major}/{minor}/{filename}"
EXTRACT_TO_FILE = False # 是否将提取的文本写入文件（否则直接打印）

DEFAULT_OUTPUT_DIR = Path(r"D:/Programs/Games/Minecraft/PrismLauncher/mods")          # 想改默认就只改这里
DEFAULT_EXTRACT_FILE = Path("blocked_mods.txt")