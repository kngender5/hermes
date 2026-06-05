import sys
from pathlib import Path

# Add scripts directory to path to allow importing clean.py
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
