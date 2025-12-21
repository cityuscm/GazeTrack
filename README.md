# GazeTrack

[![Paper](https://img.shields.io/badge/Paper-10.1145/3757376.3771419-blue)](https://doi.org/10.1145/3757376.3771419) [![Build](https://github.com/cityuscm/GazeTrack/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/cityuscm/GazeTrack/actions/workflows/build.yml)

This is a monorepo containing the official implementation of [Multi-user Gaze Tracking via Dynamic Image Mapping in 360 Immersive 3D
Visualization Systems](https://doi.org/10.1145/3757376.3771419)

[![Hero](https://raw.githubusercontent.com/cityuscm/assets/refs/heads/main/images/gazetrack/img.webp)](https://raw.githubusercontent.com/cityuscm/assets/refs/heads/main/images/gazetrack/img.webp)

For a more comprehensive documentation, please refer to the [docs](docs/).

---

## Getting Started

### Prerequisites

- **Python**: Version `>=3.13` is required.
- **Package Manager**: We **strongly recommend** using [uv](https://docs.astral.sh/uv/) or [pixi](https://pixi.sh/) to manage your python versions and dependencies.

### Installation & Running

The easiest way to get started is to use the prebuilt app.

#### Download Prebuilt App

Download the prebuilt app from [releases](https://github.com/cityuscm/GazeTrack/releases).

Unzip the downloaded file and run the executable with a terminal:

> On Unix-like systems, you may need to make it executable first by running: `chmod +x <executable_name>`

```bash
./gazetrack-web # or any derivation of the file name
```

### Running from Source

#### Getting the source

```bash
# Clone the repository
git clone https://github.com/cityuscm/GazeTrack.git
cd GazeTrack
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

# Copy the frontend artifacts to the backend
cp -r frontend/build/* backend/packages/web/src/gazetrack_web/ui/

# Run the app
cd backend && uv run gazetrack-web
```
