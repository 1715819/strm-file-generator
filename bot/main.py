import os
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown

# ============== 配置部分 ==============
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))
FOLDER_NAME = os.getenv("FOLDER_NAME", "alist")
MAX_FILENAME_LENGTH = 255
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.join(BASE_DIR, FOLDER_NAME)

def generate_random_string(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def sanitize_filename(name):
    """安全的文件名处理"""
    safe_name = os.path.basename(name)
    replace_dict = {
        '/': '／', '\\': '＼', ':': '：',
        '*': '＊', '?': '？', '"': '“',
        '<': '＜', '>': '＞', '|': '｜'
    }
    for char, replacement in replace_dict.items():
        safe_name = safe_name.replace(char, replacement)
    return safe_name.strip()

# bot/main.py（完整修复版）

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    
    if not text:
        await update.message.reply_markdown_v2(escape_markdown("❌ 错误：输入内容不能为空", version=2))
        return
    
    clean_name = sanitize_filename(text)
    if not clean_name:
        await update.message.reply_markdown_v2(escape_markdown("❌ 错误：无效文件名（处理后为空）", version=2))
        return
    
    if len(clean_name) > MAX_FILENAME_LENGTH - 5:
        await update.message.reply_markdown_v2(
            escape_markdown(f"❌ 文件名过长（最大允许 {MAX_FILENAME_LENGTH-5} 字符）", version=2)
        )
        return
    
    filename = f"{clean_name}.strm"
    file_path = os.path.join(FOLDER_PATH, filename)
    content = generate_random_string(20)
    
    try:
        os.makedirs(FOLDER_PATH, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        
        success_msg = (
            "✅ *文件创建成功* \\!\n"
            f"▪ 文件名： `{escape_markdown(filename, version=2)}`\n"
            f"▪ 随机内容： `{escape_markdown(content, version=2)}`\n"
            f"▪ 存储路径： `{escape_markdown(FOLDER_PATH, version=2)}`"
        )
        await update.message.reply_markdown_v2(success_msg)
        
    except Exception as e:
        error_msg = f"❌ *创建失败* \\: {escape_markdown(str(e), version=2)}"
        await update.message.reply_markdown_v2(error_msg)

async def post_init(application: Application):
    bot = application.bot
    bot_info = await bot.get_me()
    
    print(f"\n{'='*40}")
    print(f"Bot @{bot_info.username} 已启动")
    print(f"用户ID: {bot_info.id}")
    print(f"存储目录: {FOLDER_PATH}")
    print(f"{'='*40}\n")
    
    startup_msg = (
        "🤖 *Bot启动成功* \\!\n"
        f"▪ 用户名: @{escape_markdown(bot_info.username, version=2)}\n"
        f"▪ ID: `{escape_markdown(str(bot_info.id), version=2)}`\n"
        f"▪ 版本: `v2\\.2`\n"
        f"▪ 存储目录: `{escape_markdown(FOLDER_PATH, version=2)}`"
    )
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=startup_msg,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"[警告] 无法发送启动通知: {str(e)}")

def main():
    proxy_url = os.getenv('HTTP_PROXY')
    
    builder = Application.builder().token(BOT_TOKEN)
    
    if proxy_url:
        builder = builder.proxy_url(proxy_url).get_updates_proxy_url(proxy_url)
    
    app = builder.post_init(post_init).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("正在启动Bot服务...")
    app.run_polling()

if __name__ == "__main__":
    main()
