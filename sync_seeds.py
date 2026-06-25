"""
「唯一」· 内容同步脚本 v2
从 5 个平台抓取语录 → 写入 data/weiyi.db review_queue → 等待人工审核
Hermes cronjob 每天执行
"""
import os, sys, random, json, sqlite3, urllib.request, urllib.error
from datetime import datetime

# ── Paths ───────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "data", "weiyi.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ── 精选图片库 ──────────────────────────────────────────
IMAGE_POOL = {
    "星空": ["https://images.unsplash.com/photo-1470813740244-df37b8c1edcb?w=800&q=80",
             "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=800&q=80"],
    "孤独": ["https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
             "https://images.unsplash.com/photo-1518834107812-67b0b7c15434?w=800&q=80"],
    "自由": ["https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
             "https://images.unsplash.com/photo-1494500764479-0c8f2919a3d8?w=800&q=80"],
    "黄昏": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
             "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80"],
    "夜晚": ["https://images.unsplash.com/photo-1532767153582-b1a0e5145009?w=800&q=80",
             "https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=800&q=80"],
    "海洋": ["https://images.unsplash.com/photo-1504898770365-14faca6a7320?w=800&q=80",
             "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80"],
    "森林": ["https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80",
             "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80"],
    "温暖": ["https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=800&q=80",
             "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80"],
}
ALL_IMAGES = [url for urls in IMAGE_POOL.values() for url in urls]


def match_image(text):
    for kw, urls in IMAGE_POOL.items():
        if kw in text:
            return random.choice(urls)
    return random.choice(ALL_IMAGES)


# ── 1. 一言 API ──────────────────────────────────────

def fetch_hitokoto():
    cats = random.choice(["d", "a", "h", "k", "i"])
    url = f"https://v1.hitokoto.cn/?c={cats}&encode=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Weiyi/2.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
            text = (data.get("hitokoto") or "").strip()
            source = data.get("from") or ""
            who = data.get("from_who") or ""
            if source and who:
                author = f"{who}《{source}》"
            elif who:
                author = who
            elif source:
                author = source
            else:
                author = "一言"
            if text and len(text) >= 10:
                return {"text": text, "author": author, "src": "一言"}
    except Exception as e:
        print(f"  [hitokoto] {e}")
    return None


# ── 2. 每日一文 ─────────────────────────────────────

def fetch_meiriyiwen():
    try:
        req = urllib.request.Request(
            "https://meiriyiwen.com/api/random",
            headers={"User-Agent": "Weiyi/2.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            content = (data.get("content") or "").replace("<p>", "").replace("</p>", "\n").strip()
            title = data.get("title") or ""
            author = data.get("author") or "每日一文"
            if title:
                author = f"{author}《{title}》"
            if len(content) > 180:
                # 截断到最后一个句号
                idx = content[:180].rfind("。")
                content = content[:idx+1] if idx > 0 else content[:180]
            if len(content) >= 20:
                return {"text": content, "author": author, "src": "每日一文"}
    except Exception as e:
        print(f"  [meiriyiwen] {e}")
    return None


# ── 3-5. 本地精选 ───────────────────────────────────

LOCAL_QUOTES = [
    {"t": "整个春天，直至夏天，都是生命力独享风流的季节。长风沛雨，艳阳明月。", "a": "史铁生", "s": "本地·文学"},
    {"t": "唯有你也想见我的时候，我们的见面才有意义。", "a": "波伏娃", "s": "本地·小众"},
    {"t": "所谓理解，通常不过是误解的总和。", "a": "村上春树", "s": "本地·小众"},
    {"t": "人生最大的遗憾，是一个人无法同时拥有青春和对青春的感受。", "a": "海明威", "s": "本地·小众"},
    {"t": "有些人能感受雨，而其他人只是被淋湿。", "a": "鲍勃·迪伦", "s": "本地·小众"},
    {"t": "真实的自我意味着：不必为自己的感受道歉。", "a": "卡尔·罗杰斯", "s": "本地·小众"},
    {"t": "我步入丛林，因为我希望生活得有意义。", "a": "梭罗", "s": "本地·文学"},
    {"t": "整个城市都睡了，只有你和你的心事不能寐。", "a": "佚名", "s": "本地·文学"},
    {"t": "谁曾经声音穿透你最深的灵魂，谁又最终用沉默回答你的沉默。", "a": "里尔克", "s": "本地·小众"},
    {"t": "我爱这哭不出来的浪漫。", "a": "严明", "s": "本地·小众"},
    {"t": "在隆冬，我终于知道，我身上有一个不可战胜的夏天。", "a": "加缪", "s": "本地·文学"},
    {"t": "忘记是自由的一种形式。", "a": "纪伯伦", "s": "本地·小众"},
    {"t": "所谓浪漫，就是没有后来。", "a": "八月长安", "s": "本地·影视"},
    {"t": "不管怎样，明天又是新的一天。", "a": "《乱世佳人》", "s": "本地·影视"},
    {"t": "你是我做过最美的梦，可惜天总会亮。", "a": "佚名", "s": "本地·小众"},
    {"t": "生活最佳状态：冷冷清清的风风火火。", "a": "木心", "s": "本地·文学"},
    {"t": "天堂应该是图书馆的模样。", "a": "博尔赫斯", "s": "本地·文学"},
    {"t": "对于世界而言，你是一个人；但对于某个人，你是他的整个世界。", "a": "狄更斯", "s": "本地·文学"},
    {"t": "我恨自己别无选择，只能冒险爱你。", "a": "阿兰·德波顿", "s": "本地·小众"},
    {"t": "人生不过午后到黄昏的距离，茶凉言尽，月上柳梢。", "a": "徐志摩", "s": "本地·文学"},
]


def fetch_local():
    q = random.choice(LOCAL_QUOTES)
    return {"text": q["t"], "author": q["a"], "src": q["s"]}


# ── 去重 + 质量控制 ──────────────────────────────────

BLACKLIST = ["广告", "推广", "扫码", "加微信", "加我QQ", "关注公众号",
             "点击下载", "赚钱", "兼职", "理财", "贷款", "加群", "转发"]


def is_quality(text):
    if not text or len(text) < 12 or len(text) > 220:
        return False
    for w in BLACKLIST:
        if w in text:
            return False
    # 去鸡汤
    cliches = ["加油你是最棒的", "阳光总在风雨后", "只要努力就能成功"]
    if sum(1 for c in cliches if c in text) >= 2:
        return False
    return True


def is_dup(db, text):
    # 检查 posts 表最近 200 条
    rows = db.execute("SELECT content FROM posts ORDER BY created_at DESC LIMIT 200").fetchall()
    for r in rows:
        existing = r["content"] or ""
        if text[:30] in existing or existing[:30] in text:
            return True
        s1 = set(text); s2 = set(existing)
        if min(len(s1), len(s2)) > 5 and len(s1 & s2) / max(len(s1), len(s2)) > 0.85:
            return True
    # 检查 review_queue
    rows2 = db.execute("SELECT content FROM review_queue WHERE reviewed=0 LIMIT 30").fetchall()
    for r in rows2:
        existing = r["content"] or ""
        if text[:30] in existing or existing[:30] in text:
            return True
    return False


# ── 主流程 ─────────────────────────────────────────────

def main():
    db = get_db()

    # 确保表存在
    db.executescript("""
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL, image TEXT DEFAULT '',
            mood TEXT DEFAULT '其他', source TEXT DEFAULT '',
            nickname TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now')),
            reviewed INTEGER DEFAULT 0
        );
    """)
    db.commit()

    candidates = []

    # 平台 1: 一言 (4 次)
    for _ in range(4):
        item = fetch_hitokoto()
        if item:
            candidates.append(item)

    # 平台 2: 每日一文 (2 次)
    for _ in range(3):
        item = fetch_meiriyiwen()
        if item:
            candidates.append(item)

    # 平台 3-5: 本地精选 (5 条，去重)
    seen = set()
    for _ in range(6):
        item = fetch_local()
        k = item["text"][:30]
        if k not in seen:
            seen.add(k)
            candidates.append(item)

    # 去重 + 写入
    inserted = 0
    for item in candidates:
        text = item["text"].strip()
        if not is_quality(text):
            continue
        if is_dup(db, text):
            continue
        author = item.get("author", "")
        source = item.get("src", "")
        image = match_image(text)

        db.execute(
            "INSERT INTO review_queue (content, image, source, nickname, created_at) VALUES (?,?,?,?,?)",
            (text, image, source, author, datetime.utcnow().isoformat()),
        )
        inserted += 1

    db.commit()
    db.close()
    print(f"[sync] 候选 {len(candidates)} → 去重+过滤后 {inserted} 条入库")


if __name__ == "__main__":
    main()
