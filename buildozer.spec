[app]
title = Tai Video Facebook
package.name = taivideofacebook
package.domain = com.tieu.fbdownloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt
version = 1.0

# Các thư viện Python cần cho app (yt-dlp cần các gói phụ trợ này)
requirements = python3,flask,werkzeug,jinja2,markupsafe,itsdangerous,click,blinker,yt-dlp,requests,certifi,charset-normalizer,idna,urllib3,pycryptodomex,mutagen,brotli,websockets

# Dùng bootstrap "webview": app sẽ chạy server Flask nội bộ rồi tự mở
# một WebView (trình duyệt nhúng) trỏ vào http://127.0.0.1:5000
p4a.bootstrap = webview

orientation = portrait
fullscreen = 0

# Quyền cần thiết: mạng (để lấy video từ Facebook) + lưu file vào bộ nhớ máy
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

# Icon mặc định (Buildozer tự tạo nếu bạn không cung cấp icon.png)
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
