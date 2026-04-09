"""
api.py
------
Application entry point — ONLY wires things together.
No business logic, no SQL, no astrological computation lives here.

To run:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI

from core.config import settings
from core.logging_setup import configure_logging

from routers import panchang, dasha, horoscope, dosha, predictions, ashtakavarga, chart, pdf

# ── Configure logging before anything else ────────────────────────────────────
configure_logging()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = settings.APP_TITLE,
    version     = settings.APP_VERSION,
    description = "Vedic Astrology API — Dashas, Panchang, AshtakaVarga, Horoscopes & more",
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(panchang.router)
app.include_router(dasha.router)
app.include_router(horoscope.router)
app.include_router(dosha.router)
app.include_router(predictions.router)
app.include_router(ashtakavarga.router)
app.include_router(chart.router)
app.include_router(pdf.router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.APP_TITLE}",
        "version": settings.APP_VERSION,
        "docs"   : "/docs",
    }


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
