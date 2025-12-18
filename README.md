# GazeTrack

[![Paper](https://img.shields.io/badge/Paper-10.1145/3757376.3771419-blue)](https://doi.org/10.1145/3757376.3771419)

Official implementation of [Multi-user Gaze Tracking via Dynamic Image Mapping in 360 Immersive 3D
Visualization Systems](https://doi.org/10.1145/3757376.3771419)

[![Hero](https://raw.githubusercontent.com/cityuscm/assets/refs/heads/main/images/gazetrack/img.webp)](https://raw.githubusercontent.com/cityuscm/assets/refs/heads/main/images/gazetrack/img.webp)

---

## Getting Started

### Prerequisites

- **Python**: Version `>=3.13` is required.
- **Package Manager**: We **strongly recommend** using [uv](https://docs.astral.sh/uv/) or [pixi](https://pixi.sh/) to manage your python versions and dependencies.

### Installation & Running

The easiest way to get started is to use the prebuilt app.

#### Download Prebuilt App

Download the prebuilt app from [releases](./releases).

### Running from Source

#### Getting the source

```bash
# Clone the repository
git clone https://github.com/cityuscm/GazeTrack.git
cd gazematch
```

#### 1. Using `just` (Recommended)

If you have [Just](https://just.systems/) installed:

```bash
# Install dependencies
just sync

# Run the app
just run
```

#### 2. Manually

```bash
# Install backend dependencies
cd backend && uv sync

# Install frontend dependencies
cd frontend && bun install

# Build the frontend
cd frontend && bun run build

# Copy the built artifacts to the backend
cp -r frontend/build/* backend/packages/web/src/gazematch_web/ui/

# Run the app
cd backend && uv run gazematch-web
```
