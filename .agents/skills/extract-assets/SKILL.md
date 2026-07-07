---
name: extract-assets
description: 使用 SoulsModelTool 从 msb-dcx 产物中提取模型资产。当用户需要提取 .geombnd.dcx 模型、生成 .fbx 文件、处理 Asset 资产、或用 SoulsModelTool/AquaTool 解压模型时触发。通常在 extract-msb-dcx 之后执行。
---

# 提取模型资产

从第一步 WitchyBND 产物的 `Model/Asset/` 目录读取 XML 文件列表，通过文件名定位游戏目录中对应的 `.geombnd.dcx` 文件，用 SoulsModelTool 解压出 `.fbx` 模型及贴图锁定数据，移动到目标目录的 `Assets/` 子目录。

## 前置条件

- 已完成 [extract-msb-dcx](../extract-msb-dcx/SKILL.md)（需要 `Model/Asset/` 下的 XML 列表）
- SoulsModelTool 可用：`E:\Program\AssetProjects\AquaToolset\net9.0-windows7.0\SoulsModelTool.exe`
- 游戏目录 `asset/` 下存在对应的 `.geombnd.dcx` 文件
- 对游戏目录的写操作需获得用户许可（SoulsModelTool 会在源文件旁生成临时产物，随后自动清理）

## 文件映射规则

XML 文件名格式为 `{PREFIX}_{NUMBER}.xml`（如 `AEG050_392.xml`），映射到游戏目录路径：

```
{PREFIX}_{NUMBER}.xml
  → group  = PREFIX[:3].lower()   (AEG → aeg)
  → folder = PREFIX.lower()        (AEG050 → aeg050)
  → target = {GAME_DIR}/asset/{group}/{folder}/{folder}_{number}.geombnd.dcx
```

实例：`AEG050_392.xml` → `asset/aeg/aeg050/aeg050_392.geombnd.dcx`

## 步骤

### 1. 扫描 XML 文件

列出 `{msb_dcx_dir}/Model/Asset/*.xml`，解析每个文件名获取 `{PREFIX}` 和 `{NUMBER}`（均为保留原始大小写，PREFIX 统一转大写）。

### 2. 定位 .geombnd.dcx

按映射规则在游戏目录 `asset/` 下定位对应的 `.geombnd.dcx` 文件。文件不存在时跳过并记录失败。

### 3. 执行 SoulsModelTool 解压

```
SoulsModelTool.exe {geombnd.dcx文件完整路径}
```

产物结构：
```
{dcx_path}_/                    ← 临时外层目录（以 _ 结尾）
  └── {PREFIX}_{NUMBER}/        ← 需要保留的内层目录
      ├── {PREFIX}_{NUMBER}.fbx
      ├── {PREFIX}_{NUMBER}.flver.boneData.json
      ├── {PREFIX}_{NUMBER}.flver.dummyData.json
      └── {PREFIX}_{NUMBER}.flver.matData.json
```

### 4. 移动资产到目标目录

将内层 `{PREFIX}_{NUMBER}/` 目录移动到 `{destination}/Assets/` 下。目标已存在时先删除再覆盖。

移动后清理外层临时目录（`{dcx_path}_/`），不留在游戏目录中。

### 5. 报告

遍历完成后报告成功数量与失败列表。

## 代码实现

```bash
uv run extract assets <msb_dcx产物目录> <目标项目根目录>
```

示例：
```bash
uv run extract assets \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena/m61_54_39_00-msb-dcx" \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena"
```

相关文件：
- `src/extractor/config.py` — SOULS_MODEL_TOOL, ASSET_DIR
- `src/extractor/assets.py` — 步骤逻辑实现 (`extract_assets`)
- `src/extractor/cli.py` — 子命令 `assets`

## 完成标准

- 所有 XML 对应的 `.geombnd.dcx` 已解压
- 每个资产的 `{PREFIX}_{NUMBER}/` 文件夹存在于 `{destination}/Assets/`
- 游戏目录中无残留临时文件夹（`*_/` 已清理）
