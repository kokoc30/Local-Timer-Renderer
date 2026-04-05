from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import routes_system, routes_render, routes_capabilities, routes_jobs
from app.core import config
import uvicorn

app = FastAPI(title=config.APP_NAME, version=config.VERSION)

# Main Application Entry Point
# - Connects system and render API routes
# - Serves static frontend files

# Register API routers
app.include_router(routes_system.router)
app.include_router(routes_render.router)
app.include_router(routes_capabilities.router)
app.include_router(routes_jobs.router)

# Mount the static directory
# This allows serving index.html, styles.css, and app.js
app.mount("/", StaticFiles(directory=str(config.STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    # Start the application using uvicorn
    # Default: 127.0.0.1:[DEFAULT_PORT]
    uvicorn.run("app.main:app", host="127.0.0.1", port=config.DEFAULT_PORT, reload=True)
