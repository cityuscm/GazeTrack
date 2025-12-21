# GazeTrack Web UI

**The reference frontend implementation for GazeTrack, powered by [SvelteKit](https://svelte.dev/).**

This project serves as the example control surface for the GazeTrack prebuilt application. It allows users to control the pipeline, visualize state, and configure the system.

For comprehensive documentation, please refer to the [docs](../docs).

---

## Overview

The Web UI communicates with the GazeTrack control backend over HTTP to:

- **Trigger actions**: Start and stop pipeline components, calibrate trackers, etc.
- **Read state**: View real-time configuration and runtime status.
- **Exchange data**: Handle necessary data flow for operating the application.

## Getting Started

### Prerequisites

- **Node.js**: Ensure you have a recent version of Node.js installed.
- **Package Manager**: Any modern package manager that is compatible with [npm](https://npmjs.com/), we recommend [bun](https://bun.sh/) or [pnpm](https://pnpm.io/).

### Installation & Running

1. **Install dependencies**:

   ```bash
   # or yarn, pnpm, bun, etc.
   npm install
   ```

2. **Run the development server**:

   ```bash
   # or yarn, pnpm, bun, etc.
   npm run dev
   ```

   The application should now be accessible at `http://localhost:5173` (or the port shown in your terminal).
