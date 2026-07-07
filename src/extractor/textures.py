"""步骤5: 从 .matbin.xml 中读取贴图引用，定位 .tpf.dcx 并解压。

流程:
  1. 扫描 Material/ 下的 .matbin.xml 文件
  2. 从 <Samplers>/<Sampler>/<Path> 提取 .tif 引用
  3. 定位游戏目录中对应的 .tpf.dcx 文件
  4. 用 SoulsModelTool 解压 → .dds 文件
  5. 将 .dds 移动到 {destination}/Textures/
"""

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import ASSET_DIR, SOULS_MODEL_TOOL

# Sampler Path 格式: N:\GR\data\Asset\Environment\texture\{PREFIX}\{PREFIX}_{NUM}_{SUFFIX}.tif
# 例: AET051_005_a.tif
_TIF_PATTERN = re.compile(r"^([A-Z]+\d+)_(\d+)_.+\.tif$", re.IGNORECASE)


def _parse_tif_path(path: str) -> tuple[str, str] | None:
    """从 TIF Path 解析 (prefix_upper, number)。

    >>> _parse_tif_path('N:\\GR\\data\\Asset\\Environment\\texture\\AET051\\AET051_005_a.tif')
    ('AET051', '005')
    """
    filename = Path(path).name
    m = _TIF_PATTERN.match(filename)
    if not m:
        return None
    return m.group(1).upper(), m.group(2)


def _resolve_tpf_dcx(prefix: str, number: str) -> Path:
    """定位 .tpf.dcx 文件。

    AET051, 005 → asset/aet/aet051/aet051_005.tpf.dcx
    """
    group = prefix[:3].lower()       # AET → aet
    folder = prefix.lower()           # AET051 → aet051
    dcx_name = f"{folder}_{number}.tpf.dcx"
    return ASSET_DIR / group / folder / dcx_name


def extract_textures(destination_dir: str | Path) -> list[Path]:
    """提取所有贴图 .tpf.dcx → .dds。

    扫描 {destination}/Material/*.matbin.xml，提取 Sampler Path，
    定位并解压 .tpf.dcx，将 .dds 移动到 Textures/。

    Args:
        destination_dir: 目标项目根目录 (包含 Material/ 子目录)

    Returns:
        移动后的 .dds 文件路径列表
    """
    dest = Path(destination_dir)
    material_dir = dest / "Material"

    if not material_dir.exists():
        print("Material 目录不存在，跳过")
        return []

    xml_files = sorted(material_dir.glob("*.matbin.xml"))
    if not xml_files:
        print("没有找到 .matbin.xml 文件，跳过")
        return []

    # 收集所有 tif path → (prefix, number)，去重 tpf_dcx
    tpf_targets: dict[str, tuple[str, str, list[str]]] = {}  # dcx_key → (prefix, num, [tif_paths])

    for xml_path in xml_files:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"  警告: {xml_path.name} XML 解析失败 - {e}")
            continue

        for sampler in root.findall(".//Sampler"):
            path_el = sampler.find("Path")
            if path_el is None or not path_el.text:
                continue

            tif_path = path_el.text.strip()
            if not tif_path:
                continue

            parsed = _parse_tif_path(tif_path)
            if parsed is None:
                continue

            prefix, number = parsed
            dcx_key = f"{prefix}_{number}".lower()

            if dcx_key not in tpf_targets:
                tpf_targets[dcx_key] = (prefix, number, [tif_path])
            else:
                tpf_targets[dcx_key][2].append(tif_path)

    print(f"找到 {len(tpf_targets)} 个唯一 .tpf.dcx")

    dest_textures = dest / "Textures"
    dest_textures.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    failed: list[str] = []

    for dcx_key, (prefix, number, _tifs) in sorted(tpf_targets.items()):
        dcx_path = _resolve_tpf_dcx(prefix, number)

        if not dcx_path.exists():
            failed.append(f"{dcx_key}: 找不到 {dcx_path}")
            continue

        # 记录运行前的 .dds 文件（用于后续识别新生成的文件）
        parent_dir = dcx_path.parent
        before = set(parent_dir.glob("*.dds"))

        print(f"  SoulsModelTool: {dcx_path.name}")

        subprocess.run(
            [str(SOULS_MODEL_TOOL), str(dcx_path)],
            cwd=str(parent_dir),
            check=True,
        )

        # 找到新生成的 .dds
        after = set(parent_dir.glob("*.dds"))
        new_dds = sorted(after - before, key=lambda p: p.name)

        if not new_dds:
            failed.append(f"{dcx_key}: 未生成 .dds 文件")
            continue

        for dds_path in new_dds:
            target = dest_textures / dds_path.name
            if target.exists():
                target.unlink()
            shutil.move(str(dds_path), str(target))
            results.append(target)

    print(f"\n完成: {len(results)} 个贴图提取成功")
    if failed:
        print(f"失败 {len(failed)} 个:")
        for f in failed:
            print(f"  - {f}")

    return results
