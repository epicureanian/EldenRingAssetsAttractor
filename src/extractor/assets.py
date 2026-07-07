"""步骤2: 从 .msb-dcx 产物中提取模型资产。

流程:
  1. 扫描 {msb_dcx_dir}/Model/Asset/ 下的 .xml 文件
  2. 解析文件名 (如 AEG050_392.xml) → prefix + number
  3. 在游戏目录定位对应的 .geombnd.dcx 文件
  4. 用 SoulsModelTool 解压
  5. 将产物子文件夹移动到 {destination}/Assets/
"""

import re
import shutil
import subprocess
from pathlib import Path

from .config import ASSET_DIR, SOULS_MODEL_TOOL

# 文件名格式: PREFIX_NUMBER.xml  例如 AEG050_392.xml
_XML_PATTERN = re.compile(r"^([A-Z]+\d+)_(\d+)\.xml$", re.IGNORECASE)


def _parse_xml_filename(filename: str) -> tuple[str, str]:
    """解析 XML 文件名，返回 (prefix_uppercase, number)。

    >>> _parse_xml_filename('AEG050_392.xml')
    ('AEG050', '392')
    """
    m = _XML_PATTERN.match(filename)
    if not m:
        raise ValueError(f"无法解析文件名: {filename}")
    return m.group(1).upper(), m.group(2)


def _resolve_dcx_path(prefix: str, number: str) -> Path:
    """根据 prefix 和 number 定位游戏目录中的 .geombnd.dcx 文件。

    AEG050, 392 → asset/aeg/aeg050/aeg050_392.geombnd.dcx
    """
    group = prefix[:3].lower()        # AEG → aeg
    folder = prefix.lower()            # AEG050 → aeg050
    dcx_name = f"{folder}_{number}.geombnd.dcx"
    dcx_path = ASSET_DIR / group / folder / dcx_name
    return dcx_path


def extract_assets(msb_dcx_dir: str | Path, destination_dir: str | Path) -> list[Path]:
    """从 msb-dcx 产物目录提取所有模型资产。

    Args:
        msb_dcx_dir: 第一步 WitchyBND 解压产物目录
                      (如 .../BayleArena/m61_54_39_00-msb-dcx)
        destination_dir: 目标项目根目录，产物放入其 Assets/ 子目录

    Returns:
        移动后的所有资产文件夹路径列表
    """
    msb_dir = Path(msb_dcx_dir)
    asset_xml_dir = msb_dir / "Model" / "Asset"

    if not asset_xml_dir.exists():
        raise FileNotFoundError(f"Asset 目录不存在: {asset_xml_dir}")

    xml_files = sorted(asset_xml_dir.glob("*.xml"))
    if not xml_files:
        print("没有找到 .xml 文件，跳过")
        return []

    dest_assets = Path(destination_dir) / "Assets"
    dest_assets.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    failed: list[str] = []

    for xml_path in xml_files:
        try:
            prefix, number = _parse_xml_filename(xml_path.name)
        except ValueError as e:
            failed.append(f"{xml_path.name}: {e}")
            continue

        dcx_path = _resolve_dcx_path(prefix, number)

        if not dcx_path.exists():
            failed.append(f"{xml_path.name}: 找不到 {dcx_path}")
            continue

        # SoulsModelTool 在源文件所在目录生成输出
        print(f"  SoulsModelTool: {dcx_path.name}")
        subprocess.run(
            [str(SOULS_MODEL_TOOL), str(dcx_path)],
            cwd=str(dcx_path.parent),
            check=True,
        )

        # 产物结构: {dcx_path}_/  →  {PREFIX}_{number}/
        output_parent = Path(str(dcx_path) + "_")
        inner_dir = output_parent / f"{prefix}_{number}"

        if not inner_dir.exists():
            failed.append(f"{xml_path.name}: 解压产物未找到 {inner_dir}")
            continue

        # 移动到 destination/Assets/
        target = dest_assets / inner_dir.name
        if target.exists():
            shutil.rmtree(target)

        shutil.move(str(inner_dir), str(target))
        results.append(target)

        # 清理空的外层目录
        if output_parent.exists():
            try:
                shutil.rmtree(output_parent)
            except OSError:
                pass

    print(f"\n完成: {len(results)} 个资产提取成功")
    if failed:
        print(f"失败 {len(failed)} 个:")
        for f in failed:
            print(f"  - {f}")

    return results
