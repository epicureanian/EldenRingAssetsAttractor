---
name: extract-map-piece
description: 使用 SoulsModelTool 从 msb-dcx 产物中提取地面模型 (MapPiece)。当用户需要提取地面、.mapbnd.dcx、MapPiece 资产时触发。通常在 extract-assets 之后执行。
---

# 提取地面模型 (MapPiece)

从第一步 WitchyBND 产物的 `Model/MapPiece/` 目录读取 XML 文件列表，通过地图序号和 piece 编号定位游戏目录中对应的 `.mapbnd.dcx` 文件，用 SoulsModelTool 解压出 `.fbx` 地面模型，移动到目标目录的 `MapPiece/` 子目录。

## 前置条件

- 已完成 [extract-msb-dcx](../extract-msb-dcx/SKILL.md)（需要 `Model/MapPiece/` 下的 XML 列表）
- SoulsModelTool 可用：`E:\Program\AssetProjects\AquaToolset\net9.0-windows7.0\SoulsModelTool.exe`
- 游戏目录 `map/{root}/{map_number}/` 下存在对应的 `.mapbnd.dcx` 文件
- 对游戏目录的写操作需获得用户许可

## 文件映射规则

XML 文件名格式为 `m{number}.xml`（如 `m543900.xml`），与地图序号组合定位：

```
m543900.xml
  → piece_number = 543900
  → map_root     = map_number[:3]       (m61_54_39_00 → m61)
  → dcx_name     = {map_number}_{piece_number}.mapbnd.dcx
  → target       = {GAME_DIR}/map/{map_root}/{map_number}/{dcx_name}
```

实例：`m543900.xml` + `m61_54_39_00` → `map/m61/m61_54_39_00/m61_54_39_00_543900.mapbnd.dcx`

## 步骤

### 1. 扫描 XML 文件

列出 `{msb_dcx_dir}/Model/MapPiece/*.xml`，解析每个文件名获取 piece 编号（去掉前缀 `m` 和 `.xml` 后缀）。

### 2. 定位 .mapbnd.dcx

地图序号前 3 位确定 `map/` 下的根目录：

```
map_number[:3] → map_root  (如 m61)
```

在 `{GAME_DIR}/map/{map_root}/{map_number}/` 下查找 `{map_number}_{piece_number}.mapbnd.dcx`。文件不存在时跳过并记录失败。

### 3. 执行 SoulsModelTool 解压

```
SoulsModelTool.exe {mapbnd.dcx文件完整路径}
```

产物结构：
```
{dcx_path}_/                              ← 临时外层目录（以 _ 结尾）
  └── {map_number}_{piece_number}/        ← 需要保留的内层目录
      ├── {map_number}_{piece_number}.fbx
      ├── ...flver.boneData.json
      ├── ...flver.dummyData.json
      └── ...flver.matData.json
```

### 4. 移动资产到目标目录

将内层 `{map_number}_{piece_number}/` 目录移动到 `{destination}/MapPiece/` 下。目标已存在时先删除再覆盖。

移动后清理外层临时目录，不留在游戏目录中。

### 5. 报告

遍历完成后报告成功数量与失败列表。

## 代码实现

```bash
uv run extract map-piece <msb_dcx产物目录> <目标项目根目录> <地图序号>
```

示例：
```bash
uv run extract map-piece \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena/m61_54_39_00-msb-dcx" \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena" \
  m61_54_39_00
```

相关文件：
- `src/extractor/map_piece.py` — 步骤逻辑实现 (`extract_map_pieces`)
- `src/extractor/cli.py` — 子命令 `map-piece`

## 完成标准

- 所有 XML 对应的 `.mapbnd.dcx` 已解压
- 每个 MapPiece 的 `{map_number}_{piece_number}/` 文件夹存在于 `{destination}/MapPiece/`
- 游戏目录中无残留临时文件夹
