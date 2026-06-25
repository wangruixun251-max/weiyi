import urllib.request, json, base64, os

TOKEN = "***"
...= "wangruixun251-max"
REPO = "weiyi"
BASE = r"C:\tmp\weiyi"

def upload(path, msg):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8') as f:
        content = f.read()
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    })
    sha = None
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            sha = json.loads(r.read()).get("sha")
    except:
        pass
    payload = {"message": msg, "content": encoded, "branch": "main"}
    if sha:
        payload["sha"] = sha
    req2 = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req2, timeout=30) as r:
        d = json.loads(r.read())
        print(f"{path}: commit {d['commit']['sha'][:7]}, size={d['content']['size']}")

upload("app.py", "v3.2: 单文件部署 - 内联模板加载")
upload("templates/index.html", "v3.2: 内联CSS/JS模板（60KB）")
print("ALL DONE")
