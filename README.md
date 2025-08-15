# Comatnhi Bot

Bot Discord đa năng cho server cá nhân — nghe nhạc, mini-game, và các tiện ích quản lý server.

---

## Tính năng

### Âm nhạc
- Phát nhạc từ YouTube (yt-dlp)
- Queue, skip, pause, resume, stop
- Audio filters: bass boost, nightcore
- Tự động ngắt kết nối khi không dùng

### Tiện ích
- Uptime bot
- Thông tin server/user

### Mini-game
- Các game nhỏ trong server

### Admin
- Quản lý bot nội bộ

---

## Cài đặt

```bash
git clone https://github.com/fee-191/comatnhi-bot.git
cd comatnhi-bot
pip install -r requirements.txt
cp .env.example .env
# Điền DISCORD_TOKEN vào .env
python main.py
```

## Cấu hình `.env`

```env
DISCORD_TOKEN=your_token_here
COMMAND_PREFIX=>
SAY_CHANNEL_ID=
CHAT_IN_CHANNEL_ID=
CHAT_OUT_CHANNEL_ID=
SPECIAL_ROLE_NAME=
```

## Stack
Python · discord.py · yt-dlp · FFmpeg
