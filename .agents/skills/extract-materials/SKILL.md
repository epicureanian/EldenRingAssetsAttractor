---
name: extract-materials
description: 使用 WitchyBND 从 .matData.json 中提取材质 .matbin 文件。当用户需要提取材质、处理 .matbin、读取 .matData.json、或查询材质贴图参数时触发。通常在 extract-assets 和 extract-map-piece 之后执行。
---

# 提取材质 Matbin

从 Assets/ 和 MapPiece/ 目录下的 `.flver.matData.json` 文件中读取材质引用，通过 MTD 路径和 Name 定位游戏目录中对应的 `.matbin` 文件，用 WitchyBND 解压为 `.matbin.xml`，移动到 `Material/` 子目录。自动按 Name 去重，相同材质只解压一次。

## 前置条件

- 已完成 [extract-assets](../extract-assets/SKILL.md) 和/或 [extract-map-piece](../extract-map-piece/SKILL.md)（需要 `.flver.matData.json` 文件）
- WitchyBND 可用：`E:\Program\AssetProjects\WitchyBND-v3.0.0.1-win-x64\WitchyBND.exe`
- 对游戏目录的写操作需获得用户许可

## .matData.json 结构

```json
[
  {
    "Name": "m61_00_640",
    "MTD": "N:\\GR\\data\\Material\\mtd_DLC02\\Map_m61_00\\matxml\\m61_00_640.matxml",
    "Textures": [...],
    "GXIndex": 0,
    "Index": 0
  }
]
```

每个条目通过 `Name` + `MTD` 定位材质文件。一个 `.matData.json` 可能包含多个条目（数组），也可能只有一条。

## MTD → matbin 映射规则

MTD 路径格式：
```
N:\GR\data\Material\{mtd_kind}\{sub_path}\{name}.matxml  (或 .mtd)
```

### mtd_kind → material 目录

| MTD 路径含 | 游戏目录 |
|---|---|
| `mtd_DLC02` | `material/allmaterial_dlc02-matbinbnd-dcx/` |
| `mtd_DLC01` | `material/allmaterial_dlc01-matbinbnd-dcx/` |
| `mtd` (无 DLC 后缀) | `material/allmaterial-matbinbnd-dcx/` |

规则：`mtd_{DLC}` → `allmaterial_{dlc_lower}-matbinbnd-dcx`；纯 `mtd` → `allmaterial-matbinbnd-dcx`。

### sub_path

MTD 路径中 `{mtd_kind}\` 之后、文件名之前的部分。例如：
```
mtd_DLC02\Map_m61_00\matxml\m61_00_640.matxml
           ↑______sub_path______↑
```

### 最终路径

```
{GAME_DIR}/material/{mat_dir}/{sub_path}/{Name}.matbin
```

实例：`m61_00_640` → `material/allmaterial_dlc02-matbinbnd-dcx/Map_m61_00/matxml/m61_00_640.matbin`

## 步骤

### 1. 扫描 .matData.json

递归遍历 `{destination}/Assets/` 和 `{destination}/MapPiece/` 下所有 `*.flver.matData.json`。

### 2. 解析材质引用

对每个 JSON 条目提取 `Name` 和 `MTD`。Name 为空则跳过。按 Name 去重，已处理的材质不再重复解压。

### 3. 解析 MTD 路径

从 MTD 中提取 `mtd_kind` 和 `sub_path`，根据 `mtd_kind` 映射到 material 子目录。

### 4. 定位并解压 .matbin

```
WitchyBND.exe {matbin文件完整路径}
```

产物为 `.matbin.xml`，生成在源文件同目录。

### 5. 移动产物到 Material/

将 `.matbin.xml` 移动到 `{destination}/Material/{Name}.matbin.xml`。

## 代码实现

```bash
uv run extract materials <目标项目根目录>
```

示例：
```bash
uv run extract materials \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena"
```

相关文件：
- `src/extractor/materials.py` — 步骤逻辑实现 (`extract_materials`)，含 `_MTD_PATTERN` 正则和 `_mtd_kind_to_dir` 映射
- `src/extractor/cli.py` — 子命令 `materials`

## 完成标准

- 所有唯一的材质 Name 对应 `.matbin` 已解压
- `.matbin.xml` 文件存在于 `{destination}/Material/`
- 相同 Name 只处理一次（去重）
- 缺失的 `.matbin` 文件已报告但不阻塞流程
