import argparse
from pathlib import Path

from app import main

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("root", help="Root directory")
parser.add_argument(
    "--recurse", "-r", action="store_true", help="Recurse into child directories"
)
parser.add_argument("--output", "-o", help="Output directory")

args = parser.parse_args()

if __name__ == "__main__":
    rootdir = Path(args.root)
    recurse = args.recurse
    output = args.output
    main(rootdir, recurse, output)
