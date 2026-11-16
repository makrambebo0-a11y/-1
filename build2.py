import os, json, time, webbrowser

base = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(base, "bible")
os.makedirs(folder, exist_ok=True)


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp1256"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def build():
    data = {}
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".txt"):
            data[f[:-4]] = read_text(os.path.join(folder, f))
    with open(os.path.join(base, "bible-data.js"), "w", encoding="utf-8") as out:
        out.write("const BOOKS = " + json.dumps(data, ensure_ascii=False) + ";")
    return len(data)


def snapshot():
    return sorted(
        (f, os.path.getmtime(os.path.join(folder, f)))
        for f in os.listdir(folder) if f.lower().endswith(".txt")
    )


print("Books:", build())
webbrowser.open("file:///" + os.path.join(base, "index.html").replace("\\", "/"))
print("Watching 'books' folder. Edit a txt file, save, then refresh the page. Ctrl+C to stop.")

last = snapshot()
try:
    while True:
        time.sleep(1)
        now = snapshot()
        if now != last:
            last = now
            print("Updated! Books:", build())
except KeyboardInterrupt:
    print("Stopped.")