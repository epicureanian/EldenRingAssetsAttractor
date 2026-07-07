"""命令行接口。"""

import argparse
import sys

from .msb_dcx import extract_msb_dcx
from .assets import extract_assets
from .map_piece import extract_map_pieces
from .materials import extract_materials
from .textures import extract_textures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="艾尔登法环资产提取工具"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 子命令: msb-dcx
    msb_parser = subparsers.add_parser("msb-dcx", help="解压 .msb.dcx 文件并移动产物")
    msb_parser.add_argument("map_number", help="地图序号，如 m61_54_39_00")
    msb_parser.add_argument("destination", help="目标目录路径")

    # 子命令: assets
    assets_parser = subparsers.add_parser("assets", help="从 msb-dcx 产物提取模型资产")
    assets_parser.add_argument("msb_dcx_dir", help="第一步产物目录 (如 .../m61_54_39_00-msb-dcx)")
    assets_parser.add_argument("destination", help="目标目录路径 (产物放入其 Assets/ 子目录)")

    # 子命令: map-piece
    mp_parser = subparsers.add_parser("map-piece", help="从 msb-dcx 产物提取地面模型")
    mp_parser.add_argument("msb_dcx_dir", help="第一步产物目录 (如 .../m61_54_39_00-msb-dcx)")
    mp_parser.add_argument("destination", help="目标目录路径 (产物放入其 MapPiece/ 子目录)")
    mp_parser.add_argument("map_number", help="地图序号，如 m61_54_39_00")

    # 子命令: materials
    mat_parser = subparsers.add_parser("materials", help="从 Assets/MapPiece 中提取材质引用并解压 .matbin")
    mat_parser.add_argument("destination", help="目标目录路径 (产物放入其 Material/ 子目录)")

    # 子命令: textures
    tex_parser = subparsers.add_parser("textures", help="从 Material 中提取贴图引用并解压 .tpf.dcx")
    tex_parser.add_argument("destination", help="目标目录路径 (产物放入其 Textures/ 子目录)")

    args = parser.parse_args()

    try:
        if args.command == "msb-dcx":
            extract_msb_dcx(args.map_number, args.destination)
        elif args.command == "assets":
            extract_assets(args.msb_dcx_dir, args.destination)
        elif args.command == "map-piece":
            extract_map_pieces(args.msb_dcx_dir, args.destination, args.map_number)
        elif args.command == "materials":
            extract_materials(args.destination)
        elif args.command == "textures":
            extract_textures(args.destination)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
