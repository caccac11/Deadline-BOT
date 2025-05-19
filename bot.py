import discord
from discord.ext import commands
import json
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'deadline_data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'Đã đăng nhập với tên: {bot.user}')

@bot.command()
async def giao(ctx, member: discord.Member, *, content):
    try:
        task_name, deadline = content.rsplit('-', 1)
        task_name = task_name.strip()
        deadline = deadline.strip()

        data = load_data()
        uid = str(member.id)

        if uid not in data:
            data[uid] = {"tasks": []}

        data[uid]["tasks"].append({
            "name": task_name,
            "deadline": deadline,
            "assigned_by": str(ctx.author.id),
            "completed": False
        })

        save_data(data)
        await ctx.send(f'✅ Đã giao task "{task_name}" cho {member.mention}, hạn: {deadline}')
    except:
        await ctx.send("❌ Cú pháp sai. Dùng: `!giao @user tên task - hạn (YYYY-MM-DD)`")

@bot.command()
async def deadline(ctx):
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data or not data[uid]["tasks"]:
        await ctx.send("📭 Bạn chưa có task nào.")
        return
    msg = "📋 **Danh sách deadline của bạn:**\n"
    for i, t in enumerate(data[uid]["tasks"], 1):
        status = "✅" if t["completed"] else "❌"
        msg += f"{i}. {t['name']} - hạn: {t['deadline']} - {status}\n"
    await ctx.send(msg)

@bot.command()
async def hoanthanh(ctx, *, task_name):
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data:
        await ctx.send("❌ Không tìm thấy task.")
        return
    for task in data[uid]["tasks"]:
        if task["name"].lower() == task_name.lower() and not task["completed"]:
            task["completed"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d")
            # Tính lương đơn giản
            task["salary"] = 100000
            deadline_dt = datetime.strptime(task["deadline"], "%Y-%m-%d")
            done_dt = datetime.strptime(task["completed_at"], "%Y-%m-%d")
            if done_dt > deadline_dt:
                task["salary"] -= 30000  # trừ tiền
            save_data(data)
            await ctx.send(f'✅ Task "{task_name}" đã được đánh dấu hoàn thành.')
            return
    await ctx.send("❌ Không tìm thấy task phù hợp hoặc đã hoàn thành.")

@bot.command()
async def luong(ctx):
    data = load_data()
    uid = str(ctx.author.id)
    if uid not in data:
        await ctx.send("❌ Không có dữ liệu lương.")
        return
    total = 0
    for task in data[uid]["tasks"]:
        if task.get("completed"):
            total += task.get("salary", 0)
    await ctx.send(f"💰 Tổng lương của bạn là: {total:,} VNĐ")

bot.run("TOKEN_BOT_CUA_BAN")
