sync:
    cd backend && uv sync
    cd frontend && bun install

run: build run-fastapi

run-fastapi:
    cd backend && uv run gazetrack-web

build: build-py build-svelte copy-svelte

build-py:
    cd backend && uv build --all-packages

build-svelte:
    cd frontend && bun install && bun run build

copy-svelte:
    # Clean old UI files and copy new build
    rm -rf backend/packages/web/src/gazetrack_web/ui
    mkdir -p backend/packages/web/src/gazetrack_web/ui
    cp -r frontend/build/* backend/packages/web/src/gazetrack_web/ui/

vendor-core:
    # 1. Clean old core files
    rm -rf backend/packages/web/src/gazetrack_core
    # 2. Copy core files
    cp -r backend/packages/core/src/gazetrack_core backend/packages/web/src/

package:
    cd backend/packages/web && hatch build && export PYAPP_PROJECT_PATH=$(fd -t f --absolute-path 'py3-none-any.whl' -1) && hatch build -t binary

rename-executable:
    uv run python backend/scripts/rename_build_artifact.py

build-dist: clean build vendor-core merge-deps package rename-executable unmerge-deps clean

merge-deps:
    uv run --with tomlkit python backend/scripts/manage_deps.py merge backend/packages/web/pyproject.toml backend/packages/core/pyproject.toml

unmerge-deps:
    uv run --with tomlkit python backend/scripts/manage_deps.py unmerge backend/packages/web/pyproject.toml backend/packages/core/pyproject.toml

clean:
    # Clean up workspace build artifacts
    rm -rf backend/dist
    # Clean up web app build artifacts
    rm -rf backend/packages/web/src/gazetrack_core
    rm -rf backend/packages/web/src/gazetrack_web/ui
    rm -rf backend/packages/web/dist
    # Clean up frontend build artifacts
    rm -rf frontend/build

storybook:
    cd frontend && bun run storybook