---
name: extract-msb-dcx
description: 使用 WitchyBND 解压 .msb.dcx 文件并将产物移动到目标目录。当用户提到需要解压地图文件、处理 msb.dcx、提取地图资产、或指定地图序号（如 m61_54_39_00）要求处理时触发。
---

# 解压 MSB DCX 文件

从艾尔登法环游戏目录的 `map/mapstudio/` 下找到指定地图序号的 `.msb.dcx` 文件，用 WitchyBND 解压，并将生成的文件夹移动到用户指定的目标路径。

## 前置条件

- WitchyBND 工具可用：`E:\Program\AssetProjects\WitchyBND-v3.0.0.1-win-x64\WitchyBND.exe`
- 游戏目录下存在目标文件：`E:\SteamLibrary\steamapps\common\ELDEN RING\Game\map\mapstudio\{map_number}.msb.dcx`
- 对游戏目录的写操作需获得用户许可

## 步骤

### 1. 确认输入

从用户获取两个参数：
- **地图序号** — 格式如 `m61_54_39_00`，对应 `map/mapstudio/` 下的 `.msb.dcx` 文件名
- **目标目录** — 解压产物文件夹的最终存放位置

### 2. 定位源文件

检查 `E:\SteamLibrary\steamapps\common\ELDEN RING\Game\map\mapstudio\{map_number}.msb.dcx` 是否存在。若不存在，报错退出。

### 3. 执行 WitchyBND 解压

```
WitchyBND.exe {msb_dcx文件完整路径}
```

WitchyBND 在**当前工作目录**（即 `.msb.dcx` 所在目录）生成输出文件夹。运行前将 shell 的 `cwd` 切换到 `map/mapstudio/`，确保产物落在此处。

产物文件夹命名规则：`{map_number}-msb-dcx`（如 `m61_54_39_00-msb-dcx`）。

完成后验证输出目录已生成，未生成则报错。

### 4. 移动产物到目标目录

将 `{map_number}-msb-dcx/` 整个文件夹**移动**（非复制）到用户指定的目标目录。

目标路径若已存在同名文件夹，先删除再移动（覆盖模式）。

### 5. 验证

确认目标路径下 `{map_number}-msb-dcx/` 存在，且源位置（`map/mapstudio/` 下）已无此文件夹。

## 代码实现

本步骤已封装为 Python 模块，优先使用：

```bash
uv run extract msb-dcx <地图序号> <目标目录>
```

相关文件：
- `src/extractor/config.py` — 路径配置（GAME_DIR, WITCHY_BND, MAPSTUDIO_DIR）
- `src/extractor/msb_dcx.py` — 步骤逻辑实现
- `src/extractor/cli.py` — CLI 入口，子命令 `msb-dcx`

## 完成标准

- WitchyBND 执行无报错
- 产物文件夹已从游戏目录移动到目标目录
- 目标目录下存在完整的 `{map_number}-msb-dcx/` 文件夹
