import os, re, json, time, webbrowser

base = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(base, "books")
hymns_dir = os.path.join(base, "hymns")
videos_dir = os.path.join(base, "videos")
videos_txt = os.path.join(base, "videos.txt")
os.makedirs(books_dir, exist_ok=True)
os.makedirs(hymns_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)

AUDIO = (".mp3", ".m4a", ".ogg", ".wav", ".aac")
VIDEO = (".mp4", ".webm", ".ogv", ".mov", ".m4v")
DEFAULT_CAT = "فيديوهات"


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1256"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def natural(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def build_books():
    data = {}
    for f in sorted(os.listdir(books_dir)):
        if f.lower().endswith(".txt"):
            data[f[:-4]] = read_text(os.path.join(books_dir, f))
    with open(os.path.join(base, "books-data.js"), "w", encoding="utf-8") as out:
        out.write("const BOOKS = " + json.dumps(data, ensure_ascii=False) + ";")
    return len(data)


def build_hymns():
    items = []
    for f in sorted(os.listdir(hymns_dir), key=natural):
        if f.lower().endswith(AUDIO):
            stem = os.path.splitext(f)[0]
            title = re.sub(r"^\d+[\s._-]+", "", stem).strip() or stem   # يشيل رقم الترتيب من أول الاسم
            items.append({"file": f, "title": title})
    with open(os.path.join(base, "hymns-list.js"), "w", encoding="utf-8") as out:
        out.write("const HYMNS = " + json.dumps(items, ensure_ascii=False) + ";")
    return len(items)


def youtube_id(url):
    m = re.search(r"(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/|v/))([\w-]{11})", url)
    return m.group(1) if m else None


def build_videos():
    items = []
    # 1) فيديوهات يوتيوب من videos.txt  (# تصنيف  /  العنوان | الرابط)
    if os.path.exists(videos_txt):
        cat = DEFAULT_CAT
        for line in read_text(videos_txt).splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if line.startswith("#"):
                cat = line.lstrip("#").strip() or DEFAULT_CAT
                continue
            title, _, url = line.rpartition("|")
            url = url.strip()
            vid = youtube_id(url)
            if not vid:
                print("  (تجاهل سطر مش رابط يوتيوب صحيح):", line[:60])
                continue
            items.append({"type": "youtube", "id": vid, "title": title.strip() or "فيديو", "cat": cat})
    # 2) ملفات فيديو من فولدر videos (الفولدر الفرعي = التصنيف)
    files = []
    for root, _, names in os.walk(videos_dir):
        for f in names:
            if f.lower().endswith(VIDEO):
                rel = os.path.relpath(os.path.join(root, f), videos_dir).replace(os.sep, "/")
                files.append(rel)
    for rel in sorted(files, key=natural):
        parts = rel.split("/")
        stem = os.path.splitext(parts[-1])[0]
        title = re.sub(r"^\d+[\s._-]+", "", stem).strip() or stem
        cat = parts[0] if len(parts) > 1 else DEFAULT_CAT
        items.append({"type": "file", "src": rel, "title": title, "cat": cat})
    with open(os.path.join(base, "videos-list.js"), "w", encoding="utf-8") as out:
        out.write("const VIDEOS = " + json.dumps(items, ensure_ascii=False) + ";")
    return len(items)


def snapshot():
    snap = []
    for d, exts in ((books_dir, (".txt",)), (hymns_dir, AUDIO)):
        for f in os.listdir(d):
            if f.lower().endswith(exts):
                p = os.path.join(d, f)
                snap.append((d, f, os.path.getmtime(p), os.path.getsize(p)))
    for root, _, names in os.walk(videos_dir):
        for f in names:
            if f.lower().endswith(VIDEO):
                p = os.path.join(root, f)
                snap.append((root, f, os.path.getmtime(p), os.path.getsize(p)))
    if os.path.exists(videos_txt):
        snap.append(("txt", "videos.txt", os.path.getmtime(videos_txt), os.path.getsize(videos_txt)))
    return sorted(snap)


def report():
    print("Books:", build_books(), "| Hymns:", build_hymns(), "| Videos:", build_videos())


report()
webbrowser.open("file:///" + os.path.join(base, "index.html").replace("\\", "/"))
print("Watching books / hymns / videos. Add/edit files, then refresh the page. Ctrl+C to stop.")

last = snapshot()
try:
    while True:
        time.sleep(1)
        now = snapshot()
        if now != last:
            last = now
            print("Updated!", end=" ")
            report()
except KeyboardInterrupt:
    print("Stopped.")