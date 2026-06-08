# Nhiệm vụ refactor cho Claude Code

Đây là repo một Discord bot (`comatnhi`) viết bằng discord.py, music engine dùng yt-dlp + FFmpeg. Mục tiêu: refactor để **dễ deploy lên server mới**. Đọc kỹ `main.py`, `utils.py` và toàn bộ `cogs/` trước khi sửa. Đừng đổi logic tính năng, chỉ làm sạch + tách config + viết tài liệu.

## 1. Tách config ra `.env` (mục tiêu chính)
- Trong `cogs/utility.py`, các cấu hình kênh hiện lưu dạng biến runtime trên RAM: `self.bot._say_channel`, `self.bot._chat_cmd_channel`, `self.bot._chat_out_channel`, `self.bot._afk_owner`. Vì lưu trên RAM nên cứ restart bot là mất, phải set lại thủ công bằng `>setvoice`/`>setchatin`/`>setchatout`. Hãy cho chúng **persist**: đọc giá trị mặc định từ `.env` lúc khởi động, vẫn giữ các lệnh set để đổi runtime, và khi set thì ghi xuống file (ví dụ `data/config.json`) để giữ qua lần restart. Key tương ứng: `SAY_CHANNEL_ID`, `CHAT_IN_CHANNEL_ID`, `CHAT_OUT_CHANNEL_ID`.
- Dòng trong `utility.py` có `name="đệ của Đại Sư Tỷ"` đang hardcode tên role gắn với 1 server cụ thể — tách ra `.env` thành `SPECIAL_ROLE_NAME`.
- Prefix `>` đọc từ `.env` (`COMMAND_PREFIX`), mặc định `>`.
- Cập nhật `.env.example` cho khớp tất cả key (file này đã có sẵn, kiểm tra và bổ sung nếu thiếu).

## 2. Môi trường & deploy
- Sinh `requirements.txt` có pin version (discord.py, yt-dlp, PyNaCl, python-dotenv, và các lib khác mà code import — kiểm tra import trong tất cả file).
- Viết `README.md` tiếng Việt gồm: mô tả tính năng (music 2-tab panel, minigame Lucky Player + LiveStream, utility `>chat`/`>say`/`>afk`), yêu cầu hệ thống (Python 3.10+, **FFmpeg cài bằng apt**), các bước deploy: clone → tạo venv → `pip install -r requirements.txt` → copy `.env.example` thành `.env` và điền token + ID → chạy `python main.py`. Kèm 1 block cấu hình PM2 mẫu cho bot này (interpreter `./venv/bin/python3`, script `main.py`).
- Kiểm tra `.gitignore` đã chặn `.env`, `venv/`, `__pycache__/`, `*.bak`, `cookies.txt`, `data/*.csv` (đã có sẵn, xác nhận lại).

Làm xong, commit với message rõ ràng và push lên `main`.
