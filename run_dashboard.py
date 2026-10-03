try:
    from waitress import serve
except ImportError:
    print("Error: waitress module not found. Install it using: pip install waitress")
    exit(1)

import importlib.util
from pathlib import Path


api_path = Path(__file__).resolve().parent / "Mobile_Control.py"
spec = importlib.util.spec_from_file_location("Mobile_Control", api_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load API module from {api_path}")

api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
app = api_module.app

print("="*60)
print("Yukti Dashboard Started")
print("http://0.0.0.0:5050")
print("="*60)

serve(
    app,
    host="0.0.0.0",
    port=5050,
    threads=8
)
