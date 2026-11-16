import os
import re
import json
import time
import webbrowser

# ----------------------------------------------------
# 1. إعداد المسارات الأساسية للمشروع
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kholagy_dir = os.path.join(BASE_DIR, "kholagy")
hymns_dir = os.path.join(BASE_DIR, "hymns")

kolaga_txt_path = os.path.join(BASE_DIR, "kolaga.txt")
kholagy_out_path = os.path.join(kholagy_dir, "الخولاجي.txt")

# إنشاء المجلدات إن لم تكن موجودة
os.makedirs(kholagy_dir, exist_ok=True)
os.makedirs(hymns_dir, exist_ok=True)

AUDIO_EXTENSIONS = (".mp3", ".m4a", ".ogg", ".wav", ".aac")


# ----------------------------------------------------
# 2. دوال مساعدة لقراءة النصوص والترتيب
# ----------------------------------------------------
def read_text_safe(file_path):
    """قراءة آمنة للملفات النصية مع دعم الترميزات المختلفة للعربية"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8", "utf-16", "cp1256"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def natural_sort_key(name):
    """ترتيب طبيعي للملفات مراعياً الأرقام"""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


# ----------------------------------------------------
# 3. دمج kolaga.txt داخل مجلد kholagy
# ----------------------------------------------------
def sync_kolaga():
    if os.path.exists(kolaga_txt_path):
        kolaga_content = read_text_safe(kolaga_txt_path).strip()
        if kolaga_content:
            with open(kholagy_out_path, "w", encoding="utf-8") as f:
                f.write(kolaga_content + "\n")
            print("✔ تمت إضافة/تحديث محتوى kolaga.txt داخل مجلد kholagy (الخولاجي.txt).")


# ----------------------------------------------------
# 4. بناء ملفات البيانات (kholagy-data.js و hymns-list.js)
# ----------------------------------------------------
def build_books():
    sync_kolaga()
    data = {}
    if os.path.exists(kholagy_dir):
        for f in sorted(os.listdir(kholagy_dir)):
            if f.lower().endswith(".txt"):
                path = os.path.join(kholagy_dir, f)
                book_name = f[:-4]  # اسم الملف بدون .txt
                data[book_name] = read_text_safe(path)
    
    # تم تعديل اسم ملف البيانات الناتج هنا ليكون kholagy-data.js
    output_js = os.path.join(BASE_DIR, "kholagy-data.js")
    with open(output_js, "w", encoding="utf-8") as out:
        out.write("const KHOLAGY = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print(f"✔ تم تحديث 'kholagy-data.js' بنجاح (عدد الملفات: {len(data)}).")
    return len(data)


def build_hymns():
    items = []
    if os.path.exists(hymns_dir):
        for f in sorted(os.listdir(hymns_dir), key=natural_sort_key):
            if f.lower().endswith(AUDIO_EXTENSIONS):
                stem = os.path.splitext(f)[0]
                title = re.sub(r"^\d+[\s._-]+", "", stem).strip() or stem
                items.append({"file": f, "title": title})
                
    output_js = os.path.join(BASE_DIR, "hymns-list.js")
    with open(output_js, "w", encoding="utf-8") as out:
        out.write("const HYMNS = " + json.dumps(items, ensure_ascii=False, indent=2) + ";")
    return len(items)


def get_snapshot():
    snap = []
    for d, exts in ((kholagy_dir, (".txt",)), (hymns_dir, AUDIO_EXTENSIONS)):
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(exts):
                    p = os.path.join(d, f)
                    snap.append((d, f, os.path.getmtime(p), os.path.getsize(p)))
    if os.path.exists(kolaga_txt_path):
        snap.append((BASE_DIR, "kolaga.txt", os.path.getmtime(kolaga_txt_path), os.path.getsize(kolaga_txt_path)))
    return sorted(snap)


def report():
    b_count = build_books()
    h_count = build_hymns()
    print(f"Kholagy Files: {b_count} | Hymns: {h_count}")


# ----------------------------------------------------
# 5. التشغيل والمراقبة
# ----------------------------------------------------
if __name__ == "__main__":
    report()
    
    target_html = "kolaga.html" if os.path.exists(os.path.join(BASE_DIR, "kolaga.html")) else "index.html"
    webbrowser.open("file:///" + os.path.join(BASE_DIR, target_html).replace("\\", "/"))
    print(f"Watching 'kholagy' and 'hymns' folders. Add/edit files, then refresh the page. Ctrl+C to stop.")

    last = get_snapshot()
    try:
        while True:
            time.sleep(1)
            now = get_snapshot()
            if now != last:
                last = now
                print("Updated!", end=" ")
                report()
    except KeyboardInterrupt:
        print("\nStopped.")