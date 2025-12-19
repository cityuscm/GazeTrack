# GazeTrack Backend Monorepo

This is a [uv](https://docs.astral.sh/uv/) monorepo containing the Python packages for GazeTrack.

Refer to the [docs](../docs) or the respective package READMEs for more information.

---

## Packages

- **[gazetrack-core](packages/core)**: The core runtime library containing the API, engine, and reference implementations.
- **[gazetrack-web](packages/web)**: The FastAPI-based backend for the prebuilt application and Web UI.

## Development

We recommend using `uv` for dependency management.

```bash
# Sync dependencies for all packages
uv sync

# Run the web server
uv run uvicorn gazetrack_web.app:app --reload
```

## Running

```bash
uv run gazetrack-web
```

The web app will be available at `http://localhost:8000`.
