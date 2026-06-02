# Samrachna — AI Design & Architecture

An AI-powered application for conceptualizing, estimating, and rendering architectural design specifications and 3D models.

## Project Structure

* **`/`** (Root): Deployment and run scripts.
* **`prompt/frontend-webapp/`**: Pure HTML/CSS/Vanilla JavaScript client. Includes the dashboard overview, metrics tracking, and 3D model viewer.
* **`prompt/Design-Engine-/backend/`**: FastAPI backend service managing auth, specs creation, database storage (MongoDB GridFS), and AI adapters.

## Features

1. **AI Design Generator**: Input prompts, style options, and locations to generate complete architectural JSON specs and designs.
2. **Interactive 3D Preview (3D Editor)**: View generated `.glb` 3D layouts directly in the browser or upload custom GLB models.
3. **Design History**: Browse past designs, view their details, and load them dynamically.
4. **Estimated Costs & Metrics**: Instantly see total designs and active estimated costs.
