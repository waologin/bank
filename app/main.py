from fastapi import FastAPI
from app.server import setup_routes

app = FastAPI()

# ルーティング設定
setup_routes(app)

@app.get("/")
def root():
    return {"message": "FastAPI Discord Bot System is running"}
