import subprocess
import sys
import os

# Run indexer.py as a module with the "nosave" argument
# Use sys.executable to ensure the same Python interpreter is used
result = subprocess.run([sys.executable, "-m", "python_indexer.indexer", "nosave"])

# Set the exit code of check.py to match indexer.py's exit code
sys.exit(result.returncode)
