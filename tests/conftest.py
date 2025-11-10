# tests/conftest.py
import sys, pathlib
# Add project root to sys.path so `import verifier...` works
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))