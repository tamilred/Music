# Telegram Audio Player Bot

### ✅ Features
- Password or invite-based access
- Playlist & reverse playback
- Monthly subscription access control (auto-expire)
- Admin-only uploads
- Protected audio (no download/forward)
- MongoDB integration
- Tamil + English UI (optional)

### 📦 Setup

1. **Clone & Install**
```bash
pip install -r requirements.txt
```

2. **Set `.env` Variables**
Fill in your bot token, Mongo URI, etc.

3. **Run the Bot**
```bash
python bot.py
```

### 🔐 Admin Commands
- `/upload` – Upload new audio
- `/generate_link username` – One-time user invite
- `/renew @username 30` – Extend access
- `/expire @username` – Revoke access
- `/check @username` – Show expiry

### 🎵 User Commands
- `/start` – Unlock access (with password or link)
- `/playlist` – View audios
- `/play <number>` – Play selected track

