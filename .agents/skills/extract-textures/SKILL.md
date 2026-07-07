---
name: extract-textures
description: 使用 SoulsModelTool 从 .matbin.xml 中提取贴图 .dds 文件。当用户需要提取贴图、处理 .tpf.dcx、导出 DDS 纹理、或读取 Sampler Path 时触发。在 extract-materials 之后执行。
---

# 提取贴图 Textures

从 `Material/` 目录下的 `.matbin.xml` 文件中读取 `<Samplers>` → `<Sampler>` → `<Path>` 纹理引用，通过 TIF 文件名定位游戏目录中对应的 `.tpf.dcx` 文件，用 SoulsModelTool 解压出 `.dds` 贴图，移动到 `Textures/` 子目录。按 TPF DCX 去重，同一个 TPF 包只解压一次。

## 前置条件

- 已完成 [extract-materials](../extract-materials/SKILL.md)（需要 `Material/*.matbin.xml`）
- SoulsModelTool 可用：`E:\Program\AssetProjects\AquaToolset\net9.0-windows7.0\SoulsModelTool.exe`
- 对游戏目录的写操作需获得用户许可

## .matbin.xml Sampler 结构

```xml
<Samplers>
  <Sampler>
    <Type>M_AMSN_..._AlbedoMap_1</Type>
    <Path>N:\GR\data\Asset\Environment\texture\AET051\AET051_005_a.tif</Path>
    <Key>2682721978</Key>
    <Unk14>...</Unk14>
  </Sampler>
  ...
</Samplers>
```

每个 `<Sampler>` 的 `<Path>` 指向一个 `.tif` 纹理文件。Path 可能为空（游戏中未配置的贴图槽），需跳过。

## TIF Path → TPF DCX 映射规则

TIF Path 格式：
```
N:\GR\data\Asset\Environment\texture\{PREFIX}\{PREFIX}_{NUM}_{SUFFIX}.tif
```

解析 `{PREFIX}_{NUM}_{SUFFIX}.tif`：
- `{PREFIX}` — 资产前缀，如 `AET051`
- `{NUM}` — 资产编号，如 `005`
- `{SUFFIX}` — 纹理类型后缀，如 `a` (albedo)、`n` (normal)、`r` (roughness)、`1m` (mask1) 等

### TPF DCX 路径

```
asset/{group}/{folder}/{folder}_{num}.tpf.dcx

  group  = PREFIX[:3].lower()   (AET → aet)
  folder = PREFIX.lower()        (AET051 → aet051)
```

实例：`AET051_005_a.tif` → `asset/aet/aet051/aet051_005.tpf.dcx`

### 去重

同一个 `.tpf.dcx` 包含该资产的所有纹理变体（`_a`, `_n`, `_r`, `_1m` 等），多个 Sampler 可能引用同一 TPF 包。按 `{PREFIX}_{NUM}`（小写）去重，一个 TPF DCX 只解压一次。

## 步骤

### 1. 解析 .matbin.xml

遍历 `{destination}/Material/*.matbin.xml`，用 XML 解析器提取每个 `<Sampler>` 的 `<Path>` 文本。Path 为空则跳过。

### 2. 解析 TIF 路径

用正则 `^([A-Z]+\d+)_(\d+)_.+\.tif$` 匹配文件名，提取 PREFIX 和 NUM。不匹配的跳过。

### 3. 去重并定位 TPF DCX

按 `{prefix}_{num}`（小写）去重，收集唯一的 TPF DCX 引用。每个引用按 `asset/{group}/{folder}/{folder}_{num}.tpf.dcx` 定位。

### 4. 执行 SoulsModelTool 解压

对每个唯一 TPF DCX：
- 记录源目录下已有 `.dds` 文件集合
- 运行 `SoulsModelTool.exe {dcx_path}`
- 对比找出新生成的 `.dds` 文件

### 5. 移动 DDS 到 Textures/

将新生成的 `.dds` 文件移动到 `{destination}/Textures/`。同名文件覆盖。

## 代码实现

```bash
uv run extract textures <目标项目根目录>
```

示例：
```bash
uv run extract textures \
  "E:/Program/BlenderProjects/eldenring_scene/BayleArena"
```

相关文件：
- `src/extractor/textures.py` — 步骤逻辑实现 (`extract_textures`)，含 `_TIF_PATTERN` 和 `_resolve_tpf_dcx`
- `src/extractor/cli.py` — 子命令 `textures`

## 完成标准

- 所有 `.matbin.xml` 中的 Sampler Path 已解析
- 唯一的 `.tpf.dcx` 文件已解压
- `.dds` 贴图文件存在于 `{destination}/Textures/`
- 同一 TPF DCX 只处理一次（去重）
