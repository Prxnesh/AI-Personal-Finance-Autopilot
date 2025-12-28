from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.base import init_db
from .api import auth, transactions, dashboard, insights, predictions, recommendations

# Initialize FastAPI app
app = FastAPI(
    title="AI Personal Finance Autopilot",
    description="AI-powered personal finance management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(insights.router)
app.include_router(predictions.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    return {
        "message": "AI Personal Finance Autopilot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
