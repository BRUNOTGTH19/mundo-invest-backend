from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clientes, webhooks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mundo Invest - Backend", version="1.0.0")

app.include_router(clientes.router)
app.include_router(webhooks.router)

@app.get("/")
def root():
    return {"status": "online"}