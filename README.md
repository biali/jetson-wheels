# Wheels (PEP 503 simple index)

This repository holds **pre-built Python wheels** for a fixed stack (Linux, Python 3.10, PyTorch 2.6 / CUDA 12.6, `aarch64`), laid out as a **[PEP 503](https://peps.python.org/pep-0503/) “simple” repository** so you can install packages with `pip` from a static HTTP server—useful alongside Docker, ComfyUI, or any environment where you want reproducible installs without building from source.

## Layout

- **`wheels_linux_py310_torch2.6.0_cu126/`** — Root of the index. It contains a root `index.html` that links to each package, and one subdirectory per **normalized project name** (hyphens, lowercase), each with its `.whl` file(s) and an `index.html` listing them.

The helper script **`rebuild_simple_index.py`** keeps that layout and the HTML indexes in sync. The wheels directory path is configured inside that script (`ROOT`).

## Serving the index

Point your web server’s document root (or a location block) at **`wheels_linux_py310_torch2.6.0_cu126/`**, or copy/sync that folder to your host. Static files are enough: no application server is required.

- Ensure **directory index** serves `index.html` (nginx default `index index.html;` is typical).
- The URL you give to `pip` must be the **base URL** of that folder (the one that contains the root `index.html`).

Example nginx concept: `location /wheels/ { alias /path/to/wheels_linux_py310_torch2.6.0_cu126/; }` so the base URL is `https://your-server/wheels/`.

## Installing with pip

Use **`--extra-index-url`** so PyPI (or another index) remains available for packages you do not mirror here:

```bash
pip install --extra-index-url https://your-server/wheels gpytoolbox
```

You can combine with version pins or `requirements.txt` as usual. Package names follow normal PyPI normalization (for example `opencv_contrib_python` matches the `opencv-contrib-python` directory).

## Adding or updating wheels

1. Place new `.whl` files **in the root of** `wheels_linux_py310_torch2.6.0_cu126/` (not inside a package subfolder).
2. Run the rebuild script from the repository root:

   ```bash
   python3 rebuild_simple_index.py
   ```

   It moves each wheel into the correct subfolder (by parsed package name), then regenerates every package `index.html` and the root `index.html`.

**Requirement:** Python 3 with the **`packaging`** library (`pip install packaging` if needed).

## Notes

- Wheels are **platform-specific**; they match the ABI and CUDA tags in the filenames. Use them only on compatible systems.
- If you change the wheels directory name or path, update the `ROOT` variable in `rebuild_simple_index.py` to match.
