# Build file .APK thật — Tải Video Facebook HD

## Vì sao không có sẵn file .apk ngay bây giờ?
Mình không build được APK trực tiếp trong môi trường trò chuyện này (không có quyền
tải Android SDK/NDK). Nhưng bộ file trong thư mục này sẽ **tự động build ra file
.apk thật** thông qua GitHub Actions (máy chủ miễn phí của GitHub) — bạn không cần
cài gì nặng trên máy tính hay điện thoại.

**Quan trọng:** bộ cấu hình này mình chưa build-thử được (không có môi trường Android
ở đây), nên có khả năng cần chỉnh sửa 1-2 lần nếu log build báo lỗi thiếu recipe cho
gói nào đó (thường gặp nhất là `yt-dlp` hoặc `pycryptodomex`). Nếu gặp lỗi, gửi log
lỗi (trong tab Actions) cho mình, mình sẽ sửa `buildozer.spec` tiếp.

## Các bước thực hiện

### Bước 1 — Tạo tài khoản & repo GitHub (nếu chưa có)
1. Vào https://github.com → đăng ký tài khoản miễn phí.
2. Bấm **New repository** → đặt tên ví dụ `tai-video-facebook` → chọn **Public**
   (repo Public thì Actions chạy miễn phí không giới hạn) → **Create repository**.

### Bước 2 — Đưa toàn bộ file trong thư mục `apk_project` này lên repo
Có 2 cách:

**Cách A — Kéo thả trên web (dễ nhất, không cần cài gì):**
1. Trong trang repo vừa tạo, bấm **Add file → Upload files**.
2. Kéo thả 3 mục sau vào:
   - `main.py`
   - `buildozer.spec`
   - cả thư mục `.github` (kéo thả cả folder, GitHub tự giữ đúng đường dẫn
     `.github/workflows/build-apk.yml`)
3. Bấm **Commit changes**.

**Cách B — Dùng Git (nếu bạn quen dùng):**
```bash
git init
git add .
git commit -m "Tai video facebook APK"
git branch -M main
git remote add origin https://github.com/<ten-ban>/tai-video-facebook.git
git push -u origin main
```

### Bước 3 — Xem quá trình build
1. Vào tab **Actions** trên repo.
2. Sẽ thấy job "Build APK" đang chạy (biểu tượng vàng xoay) — build lần đầu mất
   khoảng **20–35 phút** (GitHub phải tải toàn bộ Android SDK/NDK về máy chủ của họ).
3. Khi chuyển thành dấu ✔ xanh là build xong.
4. Nếu chuyển thành ✘ đỏ: bấm vào job → xem log → copy đoạn báo lỗi gửi cho mình.

### Bước 4 — Tải file APK về điện thoại
1. Trong job build đã chạy xong (dấu ✔ xanh), kéo xuống mục **Artifacts**.
2. Bấm tải **TaiVideoFacebook-apk** (file .zip chứa file .apk bên trong).
3. Chuyển file vào điện thoại (qua Google Drive, Zalo gửi cho chính mình, cáp USB...).
4. Giải nén, được file `.apk`.

### Bước 5 — Cài đặt trên điện thoại
1. Mở file `.apk` vừa tải.
2. Android sẽ hỏi "Cho phép cài từ nguồn không xác định" → bấm **Cài đặt / Cho phép**
   (vì đây không phải app từ Google Play, đây là bình thường với app tự build).
3. Cài xong, mở app như app bình thường — có icon riêng trên màn hình chính.

## Giới hạn cần biết
- App cần quyền **Internet** và **Bộ nhớ** — Android sẽ hỏi xin quyền lần đầu mở app,
  bấm Cho phép để lưu video được.
- Tính năng "Chỉ âm thanh (MP3)" cần `ffmpeg` để tách nhạc — bản APK này **chưa** đóng
  gói ffmpeg (khó build cho Android), nên tùy chọn MP3 có thể không chạy được ngay;
  tải video MP4 bình thường thì không vấn đề gì. Nếu bạn cần MP3 hoạt động, nói mình
  thêm recipe ffmpeg cho Android (phức tạp hơn, sẽ tăng thời gian build).
- Đây là app tự build (không qua Google Play kiểm duyệt) nên máy sẽ luôn cảnh báo
  "nguồn không xác định" khi cài — đó là bình thường, không phải app có vấn đề.
