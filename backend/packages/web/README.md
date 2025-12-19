# GazeTrack Web Backend

**The reference backend implementation for the GazeTrack Prebuilt App.**

Powered by [FastAPI](https://fastapi.tiangolo.com/), this package provides the HTTP API and websocket connections required to control the GazeTrack runtime and serve the frontend.

You can use this package as the reference implementation for your own web app, or use it directly for your own projects.

Refer to the [docs](../../../docs) for more information.

---

## Features

- **Control API**: Endpoints to start/stop the engine and manage pipeline lifecycle.
- **State Management**: Exposes current configuration and runtime status.
- **Integration**: Designed to work seamlessly with the [GazeTrack Core](../core) library and the [Web UI](../../../frontend).

## Usage

This package is typically run as part of the full GazeTrack stack. See the root [README](../../../README.md) for running instructions.
