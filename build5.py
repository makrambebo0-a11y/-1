import os
import re
import json
import time
import webbrowser

# ----------------------------------------------------
# 1. إعداد المسارات الأساسية للمشروع
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(BASE_DIR, "books")
HYMNS_DIR = os.path.join(BASE_DIR, "hymns")

KOLAGA_TXT_PATH = os.path.join(BASE_DIR, "kolaga.txt")
KHOLAGY_OUT_PATH = os.path.join(BOOKS_DIR, "الخولاجي.txt")

# إنشاء المجلدات في حال عدم وجودها
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(HYMNS_DIR, exist_ok=True)

# الصيغ الصوتية المدعومة
AUDIO_EXTENSIONS = (".mp3", ".m4a", ".ogg", ".wav", ".aac")


# ----------------------------------------------------
# 2. دوال مساعدة لتعامل مع النصوص والملفات
# ----------------------------------------------------
def read_text_safe(file_path):
    """قراءة محتوى الملفات النصية مع تجربة ترميزات مختلفة لضمان سلامة اللغة العربية"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        raw_data = f.read()
    
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1256"):
        try:
            return raw_data.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    return raw_data.decode("utf-8", errors="replace")


def natural_sort_key(filename):
    """ترتيب الملفات ترتيباً طبيعياً مراعياً للأرقام (مثال: 1, 2, 10 بدلاً من 1, 10, 2)"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", filename)]


# ----------------------------------------------------
# 3. دوال المعالجة والبناء
# ----------------------------------------------------
def sync_kolaga_to_kholagy():
    """دمج محتوى kolaga.txt في ملف الخولاجي.txt بشكل نظيف دون تكرار"""
    if os.path.exists(KOLAGA_TXT_PATH):
        content = read_text_safe(KOLAGA_TXT_PATH).strip()
        if content:
            with open(KHOLAGY_OUT_PATH, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            print("✔ تم تحديث ملف 'الخولاجي.txt' بمحتوى 'kolaga.txt' بنجاح.")


def build_books():
    """تجميع كل كتب مجلد books وتوليد ملف books-data.js"""
    sync_kolaga_to_kholagy()
    
    books_data = {}
    for filename in sorted(os.listdir(BOOKS_DIR)):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(BOOKS_DIR, filename)
            book_name = filename[:-4]  # حذف امتداد .txt للحصول على اسم الكتاب
            books_data[book_name] = read_text_safe(file_path)
            
    output_js = os.path.join(BASE_DIR, "books-data.js")
    with open(output_js, "w", encoding="utf-8") as f:
        f.write("const BOOKS = " + json.dumps(books_data, ensure_ascii=False, indent=2) + ";")
        
    print(f"✔ تم بناء 'books-data.js' بنجاح (عدد الكتب: {len(books_data)}).")
    return len(books_data)


def build_hymns():
    """تجميع الألحان والملفات الصوتية وتوليد ملف hymns-list.js"""
    hymns_list = []
    if os.path.exists(HYMNS_DIR):
        for filename in sorted(os.listdir(HYMNS_DIR), key=natural_sort_key):
            if filename.lower().endswith(AUDIO_EXTENSIONS):
                stem = os.path.splitext(filename)[0]
                # إزالة الأرقام والرموز من بداية اسم اللحن ليظهر كعنوان نظيف
                clean_title = re.sub(r"^\d+[\s._-]+", "", stem).strip() or stem
                hymns_list.append({"file": filename, "title": clean_title})
                
    output_js = os.path.join(BASE_DIR, "hymns-list.js")
    with open(output_js, "w", encoding="utf-8") as f:
        f.write("const HYMNS = " + json.dumps(hymns_list, ensure_ascii=False, indent=2) + ";")
        
    print(f"✔ تم بناء 'hymns-list.js' بنجاح (عدد الألحان: {len(hymns_list)}).")
    return len(hymns_list)


def get_snapshot():
    """أخذ لقطة لمواعيد وأحجام الملفات لمراقبة التغييرات"""
    snap = []
    for directory, exts in ((BOOKS_DIR, (".txt",)), (HYMNS_DIR, AUDIO_EXTENSIONS)):
        if os.path.exists(directory):
            for f in os.listdir(directory):
                if f.lower().endswith(exts):
                    p = os.path.join(directory, f)
                    snap.append((directory, f, os.path.getmtime(p), os.path.getsize(p)))
    if os.path.exists(KOLAGA_TXT_PATH):
        snap.append((BASE_DIR, "kolaga.txt", os.path.getmtime(KOLAGA_TXT_PATH), os.path.getsize(KOLAGA_TXT_PATH)))
    return sorted(snap)


def run_build():
    """تشغيل البناء الكامل والطباعة"""
    b_count = build_books()
    h_count = build_hymns()
    print(f"--- الإجمالي: {b_count} كتاب | {h_count} لحن ---")


# ----------------------------------------------------
# 4. نقطة الانطلاق والمراقبة (Main Loop)
# ----------------------------------------------------
if __name__ == "__main__":
    print("بدء عملية البناء...")
    run_build()

    # تحديد ملف الـ HTML المستهدف للفتح تلقائياً
    target_html = "kolaga.html" if os.path.exists(os.path.join(BASE_DIR, "kolaga.html")) else "index.html"
    html_file_path = os.path.join(BASE_DIR, target_html).replace("\\", "/")
    
    # فتح الصفحة في المتصفح
    webbrowser.open("file:///" + html_file_path)
    print(f"\nتم فتح الملف '{target_html}' في المتصفح.")
    print("السكريبت يعمل الآن في وضع المراقبة. قم بتعديل أو إضافة ملفات وسيتم تحديث البيانات تلقائياً. (اضغط Ctrl+C للإيقاف)")

    # دورة مراقبة التعديلات على الملفات
    last_state = get_snapshot()
    try:
        while True:
            time.sleep(1)
            current_state = get_snapshot()
            if current_state != last_state:
                last_state = current_state
                print("\n[تنبيه] تم كشف تغيير في الملفات! جاري إعادة البناء...")
                run_build()
    except KeyboardInterrupt:
        print("\nتم إيقاف التشغيل بنجاح.")