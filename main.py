import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "8759118827:AAGGfklUI72a5aRAZ-60pJW76QkFYeM2wuU"

TH_MAPPING = {
    "TH1": "Tài 15",  "TH2": "Tài 14",  "TH3": "Tài 13",  "TH4": "Tài 12",
    "TH5": "Tài 11",  "TH6": "Xỉu 10",  "TH7": "Xỉu 9",   "TH8": "Xỉu 8",
    "TH9": "Xỉu 7",   "TH10": "Xỉu 6",  "TH11": "Xỉu 5",  "TH12": "Xỉu 4",  "TH13": "Xỉu 3"
}

KNOWLEDGE_BASE = {
    ("1-1", 15, 10): {"main": "TH4", "sub": "TH1"},
    ("123", 14, 12): {"main": "TH6", "sub": "TH8"},
    ("NÉN_10X", 10, 10): {"main": "TH4", "sub": "TH3"}
}

history_scores = []

def detect_pattern(hist):
    if len(hist) < 4:
        return "TÍCH LŨY DỮ LIỆU"
    tx = ["T" if s >= 11 else "X" for s in hist]
    if hist[-3:] == [10, 10, 10]:
        return "NÉN_10X"
    elif tx[-4:] in [["T", "X", "T", "X"], ["X", "T", "X", "T"]]:
        return "1-1"
    elif tx[-4:] in [["T", "T", "X", "X"], ["X", "X", "T", "T"]]:
        return "2-2"
    elif len(set(tx[-4:])) == 1:
        return "BỆT"
    return "NHẢY_TỰ_DO"

def analyze_and_store(score):
    history_scores.append(score)
    if len(history_scores) > 100:
        history_scores.pop(0)
        
    total_loaded = len(history_scores)
    
    if total_loaded < 2:
        return (
            f"📥 **Đã nhận điểm đầu tiên:** `{score}` ({'TÀI' if score>=11 else 'XỈU'})\n"
            f"📌 Bộ nhớ hiện tại: **{total_loaded}/100 phiên**.\n"
            f"👉 Nhập tiếp con số phiên thứ 2 để bắt đầu soi cầu!"
        )
        
    pattern = detect_pattern(history_scores)
    prev, current = history_scores[-2], history_scores[-1]
    key = (pattern, prev, current)
    recent_chain = " ➔ ".join(map(str, history_scores[-5:]))
    
    if key in KNOWLEDGE_BASE:
        main_th = KNOWLEDGE_BASE[key]["main"]
        sub_th = KNOWLEDGE_BASE[key]["sub"]
        return (
            f"🧠 **PHÂN TÍCH MA TRẬN AUTOMATION**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📜 Chuỗi 5 phiên gần nhất: `{recent_chain}`\n"
            f"💾 Đã nạp bộ nhớ: **{total_loaded} phiên**\n"
            f"📊 Cầu nhận diện: **{pattern}** | Nhịp: `{prev}` ➔ `{current}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 **DỰ ĐOÁN CHÍNH:** {TH_MAPPING[main_th].upper()} ({main_th})\n"
            f"🛡️ **PHƯƠNG ÁN LÓT:** {TH_MAPPING[sub_th]} ({sub_th})"
        )
    else:
        if current <= 6:
            pred = "TÀI 12 (Nảy cực trị)"
        elif current >= 15:
            pred = "XỈU 8 (Xả đỉnh)"
        elif pattern == "NÉN_10X":
            pred = "TÀI 12 (Bung lực 10X)"
        elif current > prev:
            pred = f"TÀI {min(current + 1, 17)} (Theo đà tăng)"
        else:
            pred = f"XỈU {max(current - 1, 4)} (Theo đà giảm)"
            
        return (
            f"🧠 **PHÂN TÍCH BIÊN ĐỘ QUÁN TÍNH**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📜 Chuỗi 5 phiên gần nhất: `{recent_chain}`\n"
            f"💾 Đã nạp bộ nhớ: **{total_loaded} phiên**\n"
            f"📊 Cầu nhận diện: **{pattern}**\n"
            f"💡 **DỰ ĐOÁN:** {pred}\n"
            f"📝 *(Đã tự lưu nhịp `{prev}` ➔ `{current}` vào bộ nhớ)*"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nums = re.findall(r'\d+', update.message.text.strip())
    if nums:
        score = int(nums[0])
        if 3 <= score <= 18:
            await update.message.reply_text(analyze_and_store(score), parse_mode="Markdown")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history_scores
    history_scores = []
    await update.message.reply_text("🔄 **Đã xóa toàn bộ bộ nhớ cũ!** Sẵn sàng nạp ca làm việc mới.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
