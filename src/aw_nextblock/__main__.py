import sys
from aw_nextblock.commands import cli

def main() -> int:
    """CLI main function"""
    try:
        cli()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())