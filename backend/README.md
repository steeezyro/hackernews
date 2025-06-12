# basic setup
- We use `uv` for Python dependency management (https://docs.astral.sh/uv/)
    - install `uv` first
    - Run `uv venv --python 3.12`
    - Activate the venv: `source .venv/bin/activate`
    - Install dependencies: `uv sync`
- We use `playwright` for browser automation (https://playwright.dev/python/)
    - Run `uv run playwright install` to install browser locally after adding the Python package `pytest-playwright`
- After all above setup, run `uv run main.py` to run the script
    ![screenshot](screenshot.png)