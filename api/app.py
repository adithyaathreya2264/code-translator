from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles      # ✅ import added
from contextlib import asynccontextmanager
from datetime import timezone
from api.config import require_mongo_uri
from api.routes import router
from fastapi.responses import RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensures MongoDB URI exists at startup
    require_mongo_uri()
    yield
    # (Optional cleanup code later if needed)


# Create FastAPI app with lifespan context
app = FastAPI(title="Code Translator Verifier API", lifespan=lifespan)

# Include all API endpoints (/verify, /runs, /runs/{id})
app.include_router(router)

# ✅ Serve static UI files from /ui path
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

# Redirect root "/" to the UI
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/ui/")