"""步骤3: 从 .msb-dcx 产物中提取地面模型 (MapPiece)。

流程:
  1. 扫描 {msb_dcx_dir}/Model/MapPiece/ 下的 .xml 文件
  2. 解析文件名 (如 m543900.xml) → piece_number
  3. 在游戏目录 map/{root}/{map_number}/ 定位 .mapbnd.dcx
  4. 用 SoulsModelTool 解压
  5. 将产物子文件夹移动到 {destination}/MapPiece/
"""

import re
import shutil
import subprocess
from pathlib import Path

from .config import GAME_DIR, SOULS_MODEL_TOOL

# 文件名格式: m{number}.xml  例如 m543900.xml
_XML_PATTERN = re.compile(r"^m(\d+)\.xml$")


def _parse_xml_filename(filename: str) -> str:
    """解析 MapPiece XML 文件名，返回 piece_number。

    >>> _parse_xml_filename('m543900.xml')
    '543900'
    """
    m = _XML_PATTERN.match(filename)
    if not m:
        raise ValueError(f"无法解析文件名: {filename}")
    return m.group(1)


def extract_map_pieces(
    msb_dcx_dir: str | Path,
    destination_dir: str | Path,
    map_number: str,
) -> list[Path]:
    """从 msb-dcx 产物目录提取所有地面模型。

    Args:
        msb_dcx_dir: 第一步 WitchyBND 解压产物目录
        destination_dir: 目标项目根目录，产物放入其 MapPiece/ 子目录
        map_number: 地图序号，如 "m61_54_39_00"

    Returns:
        移动后的所有 MapPiece 文件夹路径列表
    """
    msb_dir = Path(msb_dcx_dir)
    map_piece_dir = msb_dir / "Model" / "MapPiece"

    if not map_piece_dir.exists():
        raise FileNotFoundError(f"MapPiece 目录不存在: {map_piece_dir}")

    xml_files = sorted(map_piece_dir.glob("*.xml"))
    if not xml_files:
        print("没有找到 .xml 文件，跳过")
        return []

    # 地图序号前三位 → map 子目录
    map_root = map_number[:3]  # m61_54_39_00 → m61
    map_dcx_dir = GAME_DIR / "map" / map_root / map_number

    if not map_dcx_dir.exists():
        raise FileNotFoundError(f"地图目录不存在: {map_dcx_dir}")

    dest_map_piece = Path(destination_dir) / "MapPiece"
    dest_map_piece.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    failed: list[str] = []

    for xml_path in xml_files:
        try:
            piece_number = _parse_xml_filename(xml_path.name)
        except ValueError as e:
            failed.append(f"{xml_path.name}: {e}")
            continue

        dcx_name = f"{map_number}_{piece_number}.mapbnd.dcx"
        dcx_path = map_dcx_dir / dcx_name

        if not dcx_path.exists():
            failed.append(f"{xml_path.name}: 找不到 {dcx_path}")
            continue

        print(f"  SoulsModelTool: {dcx_name}")
        subprocess.run(
            [str(SOULS_MODEL_TOOL), str(dcx_path)],
            cwd=str(dcx_path.parent),
            check=True,
        )

        # 产物结构: {dcx_path}_/  →  {map_number}_{piece_number}/
        output_parent = Path(str(dcx_path) + "_")
        inner_dir = output_parent / f"{map_number}_{piece_number}"

        if not inner_dir.exists():
            failed.append(f"{xml_path.name}: 解压产物未找到 {inner_dir}")
            continue

        target = dest_map_piece / inner_dir.name
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

    print(f"\n完成: {len(results)} 个地面模型提取成功")
    if failed:
        print(f"失败 {len(failed)} 个:")
        for f in failed:
            print(f"  - {f}")

    return results
