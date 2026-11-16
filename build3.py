import os, re, json, time, webbrowser

base = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(base, "books")
hymns_dir = os.path.join(base, "hymns")
os.makedirs(books_dir, exist_ok=True)
os.makedirs(hymns_dir, exist_ok=True)

AUDIO = (".mp3", ".m4a", ".ogg", ".wav", ".aac")


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


def snapshot():
    snap = []
    for d, exts in ((books_dir, (".txt",)), (hymns_dir, AUDIO)):
        for f in os.listdir(d):
            if f.lower().endswith(exts):
                p = os.path.join(d, f)
                snap.append((d, f, os.path.getmtime(p), os.path.getsize(p)))
    return sorted(snap)


def report():
    print("Books:", build_books(), "| Hymns:", build_hymns())


report()
webbrowser.open("file:///" + os.path.join(base, "index.html").replace("\\", "/"))
print("Watching 'books' and 'hymns' folders. Add/edit files, then refresh the page. Ctrl+C to stop.")

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
    import os
import re
import json
import time
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(HERE, "books")
kolaga_txt_path = os.path.join(HERE, "kolaga.txt")
kholagy_out_path = os.path.join(books_dir, "الخولاجي.txt")

os.makedirs(books_dir, exist_ok=True)

# 1. دمج محتوى kolaga.txt داخل الخولاجي.txt في مجلد books
if os.path.exists(kolaga_txt_path):
    with open(kolaga_txt_path, "r", encoding="utf-8", errors="ignore") as f:
        kolaga_content = f.read()

    # فتح أو إنشاء ملف الخولاجي وإلحاق المحتوى به
    with open(kholagy_out_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + kolaga_content.strip() + "\n")
    
    print("تمت إضافة محتوى kolaga.txt إلى الخولاجي.txt بنجاح.")

# 2. بناء ملف books-data.js
def build_books():
    data = {}
    for f in sorted(os.listdir(books_dir)):
        if f.lower().endswith(".txt"):
            path = os.path.join(books_dir, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                data[f[:-4]] = file.read()
    
    with open(os.path.join(HERE, "books-data.js"), "w", encoding="utf-8") as out:
        out.write("const BOOKS = " + json.dumps(data, ensure_ascii=False) + ";")
    print(f"تم تحديث كتب الصفحة ({len(data)} كتاب).")

if __name__ == "__main__":
    build_books()