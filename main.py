#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tải Video Facebook HD - Bản Android (chạy trong Termux, dùng qua trình duyệt điện thoại)
Yêu cầu: pip install flask yt-dlp   |   pkg install ffmpeg (khuyên dùng)
Chạy:    python app.py
Mở:      http://127.0.0.1:5000  trên Chrome/trình duyệt của điện thoại
"""

import os
import re
import sys
import uuid
import threading
import subprocess
from pathlib import Path

from flask import Flask, request, jsonify, render_template_string

try:
    import yt_dlp
except ImportError:
    print("Thiếu yt-dlp, đang cài...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

APP_TITLE = "Tải Video Facebook HD"

# Thư mục lưu: ưu tiên bộ nhớ dùng chung của Android qua Termux (~/storage/downloads),
# nếu chưa setup termux-setup-storage thì lưu trong thư mục Home.
ANDROID_SHARED = Path.home() / "storage" / "downloads" / "FacebookVideos"
FALLBACK_DIR = Path.home() / "FacebookVideos"
OUTPUT_DIR = ANDROID_SHARED if (Path.home() / "storage").exists() else FALLBACK_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RES_OPTIONS = {
    "best": "bestvideo+bestaudio/best",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "audio": "bestaudio/best",
}

app = Flask(__name__)

# Trạng thái các job tải, lưu trong bộ nhớ (mất khi restart server - đủ dùng cho 1 phiên)
JOBS = {}
JOBS_LOCK = threading.Lock()


def is_facebook_url(u: str) -> bool:
    return "facebook.com" in u or "fb.watch" in u


def run_download(job_id, url, quality, cookies_path):
    with JOBS_LOCK:
        JOBS[job_id]["status"] = "downloading"

    def hook(d):
        if d.get("status") == "downloading":
            pct = d.get("_percent_str", "0%").strip()
            with JOBS_LOCK:
                JOBS[job_id]["progress"] = pct
        elif d.get("status") == "finished":
            with JOBS_LOCK:
                JOBS[job_id]["progress"] = "100%"

    is_audio_only = quality == "audio"
    ydl_opts = {
        "format": RES_OPTIONS.get(quality, RES_OPTIONS["best"]),
        "outtmpl": str(OUTPUT_DIR / "%(title).150s.%(ext)s"),
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if not is_audio_only:
        ydl_opts["merge_output_format"] = "mp4"
    if is_audio_only:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts["cookiefile"] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", url) if info else url
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "done"
            JOBS[job_id]["title"] = title
    except Exception as e:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = str(e)[:200]


@app.route("/")
def index():
    return render_template_string(PAGE, title=APP_TITLE, out_dir=str(OUTPUT_DIR))


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(force=True)
    urls_raw = data.get("urls", "")
    quality = data.get("quality", "best")
    cookies_path = data.get("cookies_path", "").strip()

    urls = [u.strip() for u in re.split(r"[\r\n]+", urls_raw) if u.strip()]
    urls = [u for u in urls if is_facebook_url(u)]
    if not urls:
        return jsonify({"error": "Không có link Facebook hợp lệ."}), 400

    job_ids = []
    for u in urls:
        job_id = uuid.uuid4().hex[:10]
        with JOBS_LOCK:
            JOBS[job_id] = {"url": u, "status": "queued", "progress": "0%", "title": u, "error": None}
        threading.Thread(target=run_download, args=(job_id, u, quality, cookies_path), daemon=True).start()
        job_ids.append(job_id)

    return jsonify({"job_ids": job_ids})


@app.route("/api/status")
def api_status():
    with JOBS_LOCK:
        return jsonify(JOBS)


PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }}</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Roboto, sans-serif; background:#0f1115; color:#eee; margin:0; padding:16px; }
  h1 { font-size:1.3rem; margin:0 0 4px; }
  .sub { color:#9aa0a6; font-size:0.85rem; margin-bottom:16px; word-break:break-all; }
  textarea { width:100%; min-height:90px; border-radius:10px; border:1px solid #333; background:#1a1d24; color:#eee; padding:10px; font-size:0.95rem; }
  select, input[type=text] { width:100%; padding:10px; border-radius:10px; border:1px solid #333; background:#1a1d24; color:#eee; font-size:0.95rem; margin-top:6px; }
  label { font-size:0.85rem; color:#c7c9cc; display:block; margin-top:14px; }
  button { width:100%; padding:14px; margin-top:16px; border:none; border-radius:12px; background:#3b82f6; color:white; font-size:1rem; font-weight:600; }
  button:active { background:#2563eb; }
  .item { background:#1a1d24; border-radius:10px; padding:10px 12px; margin-top:10px; }
  .item .top { display:flex; justify-content:space-between; font-size:0.85rem; }
  .item .title { word-break:break-all; margin-bottom:4px; font-size:0.9rem; }
  .badge { padding:2px 8px; border-radius:20px; font-size:0.75rem; }
  .queued { background:#3a3d44; }
  .downloading { background:#7c5cff; }
  .done { background:#22c55e; }
  .error { background:#ef4444; }
  #list { margin-top:8px; }
</style>
</head>
<body>
  <h1>📥 {{ title }}</h1>
  <div class="sub">Lưu tại: {{ out_dir }}</div>

  <label>Dán link Facebook (mỗi link một dòng)</label>
  <textarea id="urls" placeholder="https://www.facebook.com/..."></textarea>

  <label>Chất lượng</label>
  <select id="quality">
    <option value="best">Cao nhất có thể</option>
    <option value="1080">1080p trở xuống</option>
    <option value="720">720p trở xuống</option>
    <option value="480">480p trở xuống</option>
    <option value="audio">Chỉ âm thanh (MP3)</option>
  </select>

  <label>Đường dẫn file cookies.txt (tùy chọn, cho video riêng tư)</label>
  <input type="text" id="cookies" placeholder="/data/data/com.termux/files/home/cookies.txt">

  <button onclick="addUrls()">⬇ Tải xuống</button>

  <div id="list"></div>

<script>
async function addUrls() {
  const urls = document.getElementById('urls').value;
  const quality = document.getElementById('quality').value;
  const cookies_path = document.getElementById('cookies').value;
  if (!urls.trim()) return;
  const res = await fetch('/api/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({urls, quality, cookies_path})
  });
  const data = await res.json();
  if (data.error) { alert(data.error); return; }
  document.getElementById('urls').value = '';
}

function badgeClass(status) {
  if (status === 'done') return 'done';
  if (status === 'error') return 'error';
  if (status === 'downloading') return 'downloading';
  return 'queued';
}
function badgeText(status) {
  return {queued:'Đang chờ', downloading:'Đang tải', done:'Xong ✔', error:'Lỗi'}[status] || status;
}

async function poll() {
  try {
    const res = await fetch('/api/status');
    const jobs = await res.json();
    const list = document.getElementById('list');
    list.innerHTML = '';
    Object.keys(jobs).reverse().forEach(id => {
      const j = jobs[id];
      const div = document.createElement('div');
      div.className = 'item';
      div.innerHTML = `
        <div class="title">${j.title}</div>
        <div class="top">
          <span class="badge ${badgeClass(j.status)}">${badgeText(j.status)}</span>
          <span>${j.status === 'error' ? (j.error||'') : (j.progress||'')}</span>
        </div>`;
      list.appendChild(div);
    });
  } catch(e) {}
  setTimeout(poll, 1200);
}
poll();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
