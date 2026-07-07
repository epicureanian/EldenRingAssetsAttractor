"""步骤4: 从 .matData.json 中读取材质引用，定位 .matbin 并解压。

流程:
  1. 扫描 Assets/ 和 MapPiece/ 下的 .flver.matData.json
  2. 解析 MTD 路径 → 定位游戏目录中的 .matbin 文件
  3. 用 WitchyBND 解压 .matbin → .matbin.xml
  4. 将 .matbin.xml 移动到 {destination}/Material/（按 Name 去重）
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

from .config import GAME_DIR, WITCHY_BND

# MTD 路径格式: N:\GR\data\Material\{mtd_kind}\{sub_path}\{name}.matxml (或 .mtd)
_MTD_PATTERN = re.compile(
    r"N:\\GR\\data\\Material\\(mtd(?:_DLC\d+)?)\\(.+?)\\([^\\]+)\.(matxml|mtd)"
)

# mtd_kind → 游戏目录 material 子目录 的映射规则
# mtd_DLC02 → allmaterial_dlc02-matbinbnd-dcx
# mtd      → allmaterial-matbinbnd-dcx
def _mtd_kind_to_dir(mtd_kind: str) -> str:
    """将 MTD 路径中的 material 类型映射到 material 子目录名。"""
    if mtd_kind == "mtd":
        return "allmaterial-matbinbnd-dcx"
    # mtd_DLC02 → dlc02
    rest = mtd_kind.removeprefix("mtd_").lower()  # DLC02 → dlc02
    return f"allmaterial_{rest}-matbinbnd-dcx"


def extract_materials(destination_dir: str | Path) -> list[Path]:
    """提取所有引用的材质 .matbin 文件。

    扫描 {destination}/Assets/ 和 {destination}/MapPiece/ 下的
    .flver.matData.json，从中提取材质引用，定位并解压 .matbin。

    Args:
        destination_dir: 目标项目根目录
                        (包含 Assets/ 和 MapPiece/ 子目录)

    Returns:
        移动后的 .matbin.xml 文件路径列表
    """
    dest = Path(destination_dir)
    matdata_files: list[Path] = []

    for sub in ("Assets", "MapPiece"):
        scan_dir = dest / sub
        if scan_dir.exists():
            matdata_files.extend(sorted(scan_dir.rglob("*.flver.matData.json")))

    if not matdata_files:
        print("没有找到 .matData.json 文件，跳过")
        return []

    dest_material = dest / "Material"
    dest_material.mkdir(parents=True, exist_ok=True)

    # 去重：记录已处理的 Name → 已移动到目标路径
    seen: set[str] = set()
    results: list[Path] = []
    failed: list[str] = []

    for json_path in matdata_files:
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            failed.append(f"{json_path.name}: JSON 解析失败 - {e}")
            continue

        if not isinstance(data, list):
            data = [data]

        for entry in data:
            name = entry.get("Name", "")
            mtd = entry.get("MTD", "")

            if not name or not mtd:
                continue

            # 去重
            if name in seen:
                continue

            m = _MTD_PATTERN.match(mtd)
            if not m:
                failed.append(f"{json_path.name}: 无法解析 MTD 路径 - {mtd}")
                continue

            mtd_kind = m.group(1)   # mtd_DLC02
            sub_path = m.group(2)   # Map_m61_00\matxml
            mat_dir = _mtd_kind_to_dir(mtd_kind)

            matbin_path = GAME_DIR / "material" / mat_dir / sub_path / f"{name}.matbin"

            if not matbin_path.exists():
                failed.append(f"{name}: 找不到 {matbin_path}")
                continue

            print(f"  WitchyBND: {name}.matbin ({mtd_kind})")

            # WitchyBND 在当前工作目录生成 .matbin.xml
            subprocess.run(
                [str(WITCHY_BND), str(matbin_path)],
                cwd=str(matbin_path.parent),
                check=True,
            )

            xml_path = matbin_path.with_suffix(matbin_path.suffix + ".xml")
            # .matbin → .matbin.xml 实际路径是 matbin_path + ".xml"
            # WitchyBND 输出: {name}.matbin.xml 紧邻原文件
            xml_path = Path(str(matbin_path) + ".xml")

            if not xml_path.exists():
                failed.append(f"{name}: 解压产物未生成 {xml_path}")
                continue

            target = dest_material / f"{name}.matbin.xml"
            if target.exists():
                target.unlink()

            shutil.move(str(xml_path), str(target))
            seen.add(name)
            results.append(target)

    print(f"\n完成: {len(results)} 个材质提取成功（去重后）")
    if failed:
        print(f"失败 {len(failed)} 个:")
        for f in failed:
            print(f"  - {f}")

    return results
