"""项目路径与工具配置。"""

from pathlib import Path

# 艾尔登法环游戏根目录
GAME_DIR = Path("E:/SteamLibrary/steamapps/common/ELDEN RING/Game")

# 工具路径
WITCHY_BND = Path("E:/Program/AssetProjects/WitchyBND-v3.0.0.1-win-x64/WitchyBND.exe")
SOULS_MODEL_TOOL = Path("E:/Program/AssetProjects/AquaToolset/net9.0-windows7.0/SoulsModelTool.exe")

# 游戏内子目录
MAPSTUDIO_DIR = GAME_DIR / "map" / "mapstudio"
ASSET_DIR = GAME_DIR / "asset"
