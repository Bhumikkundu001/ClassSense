import sys
from pathlib import Path


# Add the src folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)


from classesense.app import main


if __name__ == "__main__":
    main()