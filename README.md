
  <h1>Chính sách bảo mật · Privacy Policy</h1>
  <p class="en">Discord bot: <strong>Cơ Mật Nhi</strong></p>
  <p class="updated">Cập nhật: 25/08/2026 · Người vận hành: Fee · Liên hệ: phildhe160155@gmail.com</p>

  <p>Tài liệu này mô tả dữ liệu bot thu thập, mục đích, cách lưu trữ và quyền của bạn. Bằng việc dùng bot hoặc thêm bot vào máy chủ, bạn đồng ý với chính sách này.</p>
  <p class="en">This document describes what data the bot collects, why, how it is stored, and your rights. By using the bot or adding it to a server, you agree to this policy.</p>

  <h2>1. Dữ liệu thu thập · Data collected</h2>
  <ul>
    <li><strong>Nội dung tin nhắn</strong> (Message Content Intent): bot đọc nội dung tin để nhận lệnh có tiền tố <code>&gt;</code> (phát nhạc, tiện ích) và để xử lý đăng ký minigame trong đúng một kênh được cấu hình. Bot <strong>không</strong> đọc hay lưu các tin nhắn không phải lệnh và không liên quan minigame.</li>
    <li><strong>Thông tin thành viên</strong> (Server Members Intent): dùng để gán/gỡ vai trò khi tham gia minigame, và để hiển thị thông tin cơ bản (ngày vào server, vai trò) khi bạn dùng lệnh xem hồ sơ.</li>
    <li><strong>Bản ghi đăng ký minigame</strong>: khi bạn tự đăng ký, bot lưu ID game và tên game <em>do bạn tự nhập</em>, cùng Discord ID, tên hiển thị và thời điểm — chỉ để chống trùng ID và cho quản trị viên xuất danh sách người tham gia.</li>
  </ul>
  <p>Bot <strong>không</strong> thu thập: email, số điện thoại, mật khẩu, thông tin thanh toán, hay bất kỳ dữ liệu nào ngoài Discord.</p>

  <h2>2. Mục đích · Purpose</h2>
  <p>Dữ liệu chỉ dùng để vận hành tính năng bạn tương tác: phát nhạc, tiện ích quản trị, và minigame đăng ký. Dữ liệu <strong>không</strong> được dùng để huấn luyện mô hình học máy hay AI, và <strong>không</strong> được bán hay cho thuê.</p>
  <p class="en">Data is used only to operate features you interact with. It is never used to train machine-learning or AI models, and is never sold or rented.</p>

  <h2>3. Lưu trữ & bảo mật · Storage & security</h2>
  <ul>
    <li>Bản ghi đăng ký minigame được lưu trong tệp cục bộ trên máy chủ do người vận hành kiểm soát. Không có cơ sở dữ liệu bên thứ ba.</li>
    <li>Lệnh nhạc và tiện ích xử lý tại thời điểm gọi và <strong>không</strong> được lưu lại.</li>
    <li>Truy cập giới hạn cho người vận hành. Dữ liệu chỉ giữ trong thời gian cần cho tính năng; khi bot bị gỡ khỏi máy chủ, dữ liệu liên quan sẽ được xoá trong vòng [30] ngày.</li>
  </ul>

  <h2>4. Chia sẻ · Sharing</h2>
  <p>Bot không chia sẻ dữ liệu với bên thứ ba, trừ khi luật pháp yêu cầu. Bot hoạt động dựa trên API chính thức của Discord và tuân thủ <a href="https://discord.com/developers/docs/policies-and-agreements/developer-policy" target="_blank" rel="noopener">Developer Policy</a> cùng <a href="https://discord.com/terms" target="_blank" rel="noopener">Terms of Service</a> của Discord.</p>

  <h2>5. Quyền của bạn & cách xoá · Your rights</h2>
  <p>Bạn có thể yêu cầu xem hoặc xoá dữ liệu đăng ký của mình bất cứ lúc nào:</p>
  <ul>
    <li>Nhờ quản trị viên máy chủ dùng lệnh gỡ đăng ký của bạn, hoặc</li>
    <li>Liên hệ người vận hành qua email <a href="mailto:phildhe160155@gmail.com">phildhe160155@gmail.com</a>.</li>
  </ul>
  <p>Quản trị viên có thể gỡ bot khỏi máy chủ để dừng mọi việc thu thập dữ liệu cho máy chủ đó.</p>

  <h2>6. Trẻ vị thành niên · Minors</h2>
  <p>Bot tuân theo Điều khoản của Discord, yêu cầu người dùng đủ 13 tuổi (hoặc độ tuổi tối thiểu theo quy định địa phương).</p>

  <h2>7. Thay đổi · Changes</h2>
  <p>Chính sách có thể được cập nhật; thay đổi quan trọng sẽ được thông báo qua [server hỗ trợ]. Ngày ở đầu trang phản ánh phiên bản mới nhất.</p>

  <h2>8. Liên hệ · Contact</h2>
  <p><a href="mailto:phildhe160155@gmail.com">phildhe160155@gmail.com</a></p>

  <hr>
  <p class="en">This policy is available in Vietnamese above; an English summary is included inline for Discord's review.</p>
</main>
</body>
</html>


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
