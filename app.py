import os
import sys

# Get absolute path of root and app_build
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")

# Add app_build to path so imports inside it work correctly
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

# Change working directory so relative paths in pages and managers resolve correctly
os.chdir(APP_BUILD_DIR)

# Set __file__ correctly for the app_build/app.py execution context
exec_globals = globals().copy()
exec_globals["__file__"] = os.path.join(APP_BUILD_DIR, "app.py")

# Execute the main streamlit entry point
with open(os.path.join(APP_BUILD_DIR, "app.py"), "r", encoding="utf-8") as f:
    code = f.read()

exec(code, exec_globals)
