import discord
from discord.ext import commands
import json
import os

# Botの設定
intents = discord.Intents.default()
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# JSONファイル
POINTS_FILE = "points.json"
ITEMS_FILE = "items.json"

# データ読み込み
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# データ保存
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ポイントデータと商品データ
points_data = load_json(POINTS_FILE)
items_data = load_json(ITEMS_FILE)

# 残高照会コマンド
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    if user_id not in points_data:
        points_data[user_id] = {"balance": 0, "history": []}
        save_json(POINTS_FILE, points_data)

    balance = points_data[user_id]["balance"]
    await ctx.author.send(f"あなたの現在の残高: {balance}コイン")

# 商品一覧表示コマンド
@bot.command()
async def items(ctx):
    if not items_data:
        await ctx.author.send("現在、商品が登録されていません。")
        return

    item_list = "\n".join(
        [f"- {name}: {details['price']}コイン" for name, details in items_data.items()]
    )
    await ctx.author.send(f"利用可能な商品一覧:\n{item_list}")

# 商品購入コマンド（前回のコードを保持）
@bot.command()
async def buy(ctx, item_name: str):
    user_id = str(ctx.author.id)
    if user_id not in points_data:
        points_data[user_id] = {"balance": 0, "history": []}
        save_json(POINTS_FILE, points_data)

    if item_name not in items_data:
        await ctx.author.send("指定された商品は存在しません。")
        return

    item = items_data[item_name]
    balance = points_data[user_id]["balance"]

    if balance < item["price"]:
        await ctx.author.send("残高が不足しています。")
        return

    await ctx.author.send(f"商品名: {item_name}\n価格: {item['price']}コイン\nこの商品を購入しますか？ (はい/いいえ)")

    def check(m):
        return m.author == ctx.author and m.content in ["はい", "いいえ"]

    try:
        response = await bot.wait_for("message", check=check, timeout=30)
        if response.content == "はい":
            points_data[user_id]["balance"] -= item["price"]
            points_data[user_id]["history"].append({"amount": -item["price"], "reason": f"購入: {item_name}"})
            save_json(POINTS_FILE, points_data)

            await ctx.author.send("購入ありがとうございます！商品を送信します。")
            await ctx.author.send(file=discord.File(item["file"]))

            admin_channel = discord.utils.get(ctx.guild.channels, name="管理チャンネル名")
            if admin_channel:
                await admin_channel.send(f"{ctx.author.name}さんが{item_name}を購入しました。\n価格: {item['price']}コイン")

        else:
            await ctx.author.send("購入をキャンセルしました。")
    except TimeoutError:
        await ctx.author.send("時間切れのため、購入がキャンセルされました。")

# Bot起動
bot.run(os.getenv("DISCORD_TOKEN"))
