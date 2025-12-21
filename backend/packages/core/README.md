# GazeTrack Core

**The core runtime library for GazeTrack.**

This package contains the core runtime API, reference implementations, and protocols for building gaze tracking and scene analysis pipelines. It is designed to be modular and decoupled, allowing developers to mix and match components or implement their own.

Refer to the [docs](../../../docs) or the [API Reference](../../../docs/src/content/docs/core/index.mdx) for more information.

---

## Modules

The Core library is organized into several key modules:

- **Engine**: Async orchestration, lifecycle management, and configuration surface.
- **Pipeline Stages**: Protocols and reference implementations for `collect`, `compress`, `process`, `match`, `validate`, and `project` stages.
- **Producers**: Streaming input implementations for POV cameras, gaze trackers, and scene data.
- **Aggregators**: Discovery utilities that mint producers per hardware source.
- **Interfaces**: Shared detector protocols and functional contracts.
- **Structs & Timestamping**: Data classes, payload hierarchy, and projection math helpers.
- **Event Bus**: Event structures and pub/sub contract for inter-component communication.
- **Exporters**: Protocols and implementations for exporting data (e.g., OSC exporter).
