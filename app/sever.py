from fastapi import FastAPI, HTTPException
import json
import os

DATA_DIR = "app/data"
POINTS_FILE = os.path.join(DATA_DIR, "points.json")
ITEMS_FILE = os.path.join(DATA_DIR, "items.json")


# データ読み込み・保存関数
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# 初期化
points_data = load_json(POINTS_FILE)
items_data = load_json(ITEMS_FILE)

# ルート設定
def setup_routes(app: FastAPI):
    @app.get("/balance/{user_id}")
    async def get_balance(user_id: str):
        if user_id not in points_data:
            return {"user_id": user_id, "balance": 0}
        return {"user_id": user_id, "balance": points_data[user_id]["balance"]}

    @app.get("/items")
    async def get_items():
        return {"items": [{"name": name, "price": details["price"]} for name, details in items_data.items()]}

    @app.post("/update_balance")
    async def update_balance(user_id: str, amount: int, reason: str):
        if user_id not in points_data:
            points_data[user_id] = {"balance": 0, "history": []}
        points_data[user_id]["balance"] += amount
        points_data[user_id]["history"].append({"amount": amount, "reason": reason})
        save_json(POINTS_FILE, points_data)
        return {"status": "success", "new_balance": points_data[user_id]["balance"]}

    @app.post("/buy")
    async def buy_item(user_id: str, item_name: str):
        if user_id not in points_data or item_name not in items_data:
            raise HTTPException(status_code=404, detail="ユーザーまたは商品が見つかりません")
        if points_data[user_id]["balance"] < items_data[item_name]["price"]:
            raise HTTPException(status_code=400, detail="残高不足")
        points_data[user_id]["balance"] -= items_data[item_name]["price"]
        points_data[user_id]["history"].append({"amount": -items_data[item_name]["price"], "reason": f"購入: {item_name}"})
        save_json(POINTS_FILE, points_data)
        return {"status": "success", "message": f"{item_name}を購入しました"}
