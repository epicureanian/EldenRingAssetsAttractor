"""步骤1: 解压 .msb.dcx 文件并移动到目标目录。

流程:
  1. 在 {GAME_DIR}/map/mapstudio/ 下找到 {map_number}.msb.dcx
  2. 用 WitchyBND 解压 → 生成 {map_number}-msb-dcx/ 文件夹
  3. 将文件夹移动到指定目标路径
"""

import shutil
import subprocess
from pathlib import Path

from .config import MAPSTUDIO_DIR, WITCHY_BND


def extract_msb_dcx(map_number: str, destination_dir: str | Path) -> Path:
    """解压 .msb.dcx 文件并将结果文件夹移动到目标目录。

    Args:
        map_number: 地图序号，如 "m61_54_39_00"
        destination_dir: 目标目录路径

    Returns:
        移动后的文件夹路径

    Raises:
        FileNotFoundError: .msb.dcx 文件不存在
        subprocess.CalledProcessError: WitchyBND 执行失败
    """
    msb_dcx_path = MAPSTUDIO_DIR / f"{map_number}.msb.dcx"
    if not msb_dcx_path.exists():
        raise FileNotFoundError(f"找不到文件: {msb_dcx_path}")

    dest = Path(destination_dir)
    dest.mkdir(parents=True, exist_ok=True)

    # WitchyBND 在当前工作目录生成输出，所以先切到 mapstudio
    print(f"[1/3] WitchyBND 解压: {msb_dcx_path.name}")
    subprocess.run(
        [str(WITCHY_BND), str(msb_dcx_path)],
        cwd=str(MAPSTUDIO_DIR),
        check=True,
    )

    output_dir = MAPSTUDIO_DIR / f"{map_number}-msb-dcx"
    if not output_dir.exists():
        raise RuntimeError(f"WitchyBND 未能生成预期的输出目录: {output_dir}")

    # 移动文件夹
    target = dest / output_dir.name
    print(f"[2/3] 移动: {output_dir} -> {target}")

    # 如果目标已存在则先删除（覆盖模式）
    if target.exists():
        shutil.rmtree(target)

    shutil.move(str(output_dir), str(target))
    print(f"[3/3] 完成: {target}")

    return target
