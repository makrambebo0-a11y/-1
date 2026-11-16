#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build6.py — بيجمّع ملفات القطمارس من فولدر katmars في ملف katmars-data.js اللي صفحة katameros.html بتقراه.

كل يوم قبطي ملف txt اسمه  الشهر-اليوم.txt :
    1-1.txt     = 1 توت            4-29.txt   = 29 كيهك (الميلاد)
    13-5.txt    = 5 النسيء         (النسيء 13-6 للسنة الكبيسة بس)
أرقام الشهور: 1 توت، 2 بابه، 3 هاتور، 4 كيهك، 5 طوبه، 6 أمشير، 7 برمهات،
              8 برمودة، 9 بشنس، 10 بؤونه، 11 أبيب، 12 مسري، 13 النسيء

صيغة الملف (زي باقي الكتب):
    # عنوان الكارت (مثلًا: القداس)
    ## اسم القراءة (مثلًا: البولس)
    النص أو مرجع القراءة
    ** توجيه أو ملاحظة (بتظهر بشكل مميز)

الاستخدام:
    python build6.py            يراقب الفولدر ويعيد البناء أول ما تحفظ أي ملف (Ctrl+C للإيقاف)
    python build6.py --once     بناء مرة واحدة وخلاص
    python build6.py --missing  يطبع الأيام الناقصة
الملفات اللي اسمها بيبدأ بـ _ بتتجاهل (زي _مثال.txt).
"""
import os
import re
import sys
import json
import time
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(HERE, "katmars")
OUT = os.path.join(HERE, "katmars-data.js")
NAME = re.compile(r"^(\d{1,2})-(\d{1,2})\.txt$", re.I)
MONTHS = ["", "توت", "بابه", "هاتور", "كيهك", "طوبه", "أمشير", "برمهات", "برمودة", "بشنس", "بؤونه", "أبيب", "مسري", "النسيء"]
EXAMPLE = """# القداس
## البولس
(اكتب هنا مرجع القراءة أو نصها)
## الإنجيل
(اكتب هنا)
** ده توجيه أو ملاحظة بتظهر بشكل مميز

# عشية
## المزمور
(اكتب هنا)
"""


def say(ar, en=None):
    try:
        ar.encode(sys.stdout.encoding or "utf-8")
        print(ar)
    except Exception:                                   # noqa: BLE001
        print(en if en is not None else ar.encode("ascii", "replace").decode())


def valid(m, d):
    return 1 <= m <= 13 and 1 <= d <= (6 if m == 13 else 30)


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-16", "cp1256"):
        try:
            return raw.decode(enc).replace("\r\n", "\n").replace("\r", "\n").strip()
        except Exception:                               # noqa: BLE001
            continue
    return raw.decode("utf-8", errors="replace").strip()


def signature():
    if not os.path.isdir(FOLDER):
        return ()
    out = []
    for f in sorted(os.listdir(FOLDER)):
        p = os.path.join(FOLDER, f)
        if f.lower().endswith(".txt") and os.path.isfile(p):
            st = os.stat(p)
            out.append((f, st.st_mtime_ns, st.st_size))
    return tuple(out)


def ensure_folder():
    if not os.path.isdir(FOLDER):
        os.makedirs(FOLDER)
        say("اتعمل فولدر katmars", "Created katmars folder")
    ex = os.path.join(FOLDER, "_مثال.txt")
    if not os.path.exists(ex):
        with open(ex, "w", encoding="utf-8", newline="\n") as f:
            f.write(EXAMPLE)


def build(show_missing=False):
    ensure_folder()
    days, bad, dup = {}, [], []
    for f in sorted(os.listdir(FOLDER)):
        if f.startswith(("_", ".")) or not f.lower().endswith(".txt"):
            continue
        m = NAME.match(f)
        if not m or not valid(int(m.group(1)), int(m.group(2))):
            bad.append(f)
            continue
        key = "%d-%d" % (int(m.group(1)), int(m.group(2)))
        txt = read_text(os.path.join(FOLDER, f))
        if key in days:
            dup.append(f)
        if txt:
            days[key] = txt

    js = ("// ملف مولَّد تلقائيًا من build6.py — متعدّلوش بإيدك\n"
          "window.KATMARS = " + json.dumps(days, ensure_ascii=False, sort_keys=True)
          .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
          + ";\nwindow.KATMARS_BUILT = " + json.dumps(time.strftime("%Y-%m-%d %H:%M")) + ";\n")
    old = None
    if os.path.exists(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            old = f.read()
    body = lambda s: s.split("window.KATMARS_BUILT")[0]  # noqa: E731
    if old is None or body(old) != body(js):
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(js)
        say("تم! اتحدّث katmars-data.js — %d يوم" % len(days), "Built katmars-data.js - %d days" % len(days))
    else:
        say("مفيش تغيير (%d يوم)" % len(days), "No changes (%d days)" % len(days))

    total = sum(1 for m in range(1, 14) for d in range(1, (6 if m == 13 else 30) + 1) if not (m == 13 and d == 6))
    have = sum(1 for k in days if k != "13-6")
    say("   مغطّى %d من %d يوم" % (have, total), "   covered %d of %d days" % (have, total))
    for f in bad:
        say("   تنبيه: اسم الملف مش مظبوط واتجاهل: " + f + "  (المفروض زي 4-29.txt)", "   bad filename ignored: " + f)
    for f in dup:
        say("   تنبيه: ملف مكرر لنفس اليوم: " + f, "   duplicate day file: " + f)
    if show_missing:
        miss = ["%d-%d" % (m, d) for m in range(1, 14) for d in range(1, (6 if m == 13 else 30) + 1)
                if not (m == 13 and d == 6) and "%d-%d" % (m, d) not in days]
        say("الأيام الناقصة (%d):" % len(miss), "Missing days:")
        say("   " + "  ".join(miss) if miss else "   مفيش — كله موجود!", "   " + " ".join(miss))


def main():
    ap = argparse.ArgumentParser(description="بناء katmars-data.js من فولدر katmars")
    ap.add_argument("--once", action="store_true", help="بناء مرة واحدة وخروج")
    ap.add_argument("--missing", action="store_true", help="اطبع الأيام الناقصة")
    a = ap.parse_args()
    build(a.missing)
    if a.once or a.missing:
        return
    say("براقب فولدر katmars ... (Ctrl+C للإيقاف)", "Watching katmars folder ... (Ctrl+C to stop)")
    last = signature()
    try:
        while True:
            time.sleep(2)
            cur = signature()
            if cur != last:
                last = cur
                build()
    except KeyboardInterrupt:
        say("اتوقف.", "Stopped.")


if __name__ == "__main__":
    main()
