"""
「唯一」· 内容同步脚本 v2
从 5 个平台抓取语录 → POST 到 weiyi.onrender.com 审核队列
Hermes cronjob 每天定时执行
"""
import os, random, json, urllib.request, urllib.error

RENDER_URL = os.environ.get("WEIYI_URL", "https://weiyi.onrender.com")
API_KEY = os.environ.get("WEIYI_API_KEY", "weiyi-internal-2026")


def _post(path, body):
    req = urllib.request.Request(
        f"{RENDER_URL}{path}",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
            "User-Agent": "Weiyi-Sync/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:200]
        print(f"[sync] HTTP {e.code}: {msg}")
        return None
    except Exception as e:
        print(f"[sync] 网络错误: {e}")
        return None


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
            if text and 10 <= len(text) <= 200:
                return {"content": text, "author": author, "src": "一言", "image": match_image(text)}
    except Exception as e:
        print(f"  [hitokoto] {e}")
    return None


# ── 2. 每日一文 ─────────────────────────────────────

def fetch_meiriyiwen():
    try:
        req = urllib.request.Request("https://meiriyiwen.com/api/random", headers={"User-Agent": "Weiyi/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            content = (data.get("content") or "").replace("<p>", "").replace("</p>", "\n").strip()
            title = data.get("title") or ""
            author_raw = data.get("author") or "每日一文"
            author = f"{author_raw}《{title}》" if title else author_raw
            if len(content) > 180:
                idx = content[:180].rfind("。")
                content = content[:idx+1] if idx > 0 else content[:180]
            if len(content) >= 20:
                return {"content": content, "author": author, "src": "每日一文", "image": match_image(content)}
    except Exception as e:
        print(f"  [meiriyiwen] {e}")
    return None


# ── 3-5. 本地精选 ───────────────────────────────────

LOCAL_QUOTES = [
    {"content": "整个春天，直至夏天，都是生命力独享风流的季节。长风沛雨，艳阳明月。", "author": "史铁生", "src": "本地·文学"},
    {"content": "唯有你也想见我的时候，我们的见面才有意义。", "author": "波伏娃", "src": "本地·小众"},
    {"content": "所谓理解，通常不过是误解的总和。", "author": "村上春树", "src": "本地·小众"},
    {"content": "人生最大的遗憾，是一个人无法同时拥有青春和对青春的感受。", "author": "海明威", "src": "本地·小众"},
    {"content": "有些人能感受雨，而其他人只是被淋湿。", "author": "鲍勃·迪伦", "src": "本地·小众"},
    {"content": "真实的自我意味着：不必为自己的感受道歉。", "author": "卡尔·罗杰斯", "src": "本地·小众"},
    {"content": "我步入丛林，因为我希望生活得有意义。", "author": "梭罗", "src": "本地·文学"},
    {"content": "整个城市都睡了，只有你和你的心事不能寐。", "author": "佚名", "src": "本地·文学"},
    {"content": "谁曾经声音穿透你最深的灵魂，谁又最终用沉默回答你的沉默。", "author": "里尔克", "src": "本地·小众"},
    {"content": "在隆冬，我终于知道，我身上有一个不可战胜的夏天。", "author": "加缪", "src": "本地·文学"},
    {"content": "忘记是自由的一种形式。", "author": "纪伯伦", "src": "本地·小众"},
    {"content": "所谓浪漫，就是没有后来。", "author": "八月长安", "src": "本地·影视"},
    {"content": "生活最佳状态：冷冷清清的风风火火。", "author": "木心", "src": "本地·文学"},
    {"content": "天堂应该是图书馆的模样。", "author": "博尔赫斯", "src": "本地·文学"},
    {"content": "我恨自己别无选择，只能冒险爱你。", "author": "阿兰·德波顿", "src": "本地·小众"},
    {"content": "人生不过午后到黄昏的距离，茶凉言尽，月上柳梢。", "author": "徐志摩", "src": "本地·文学"},
    {"content": "你是我做过最美的梦，可惜天总会亮。", "author": "佚名", "src": "本地·小众"},
    {"content": "不管怎样，明天又是新的一天。", "author": "《乱世佳人》", "src": "本地·影视"},
    {"content": "这样看你，用所有眼睛和所有距离。就像风住了，风又起。", "author": "冯唐", "src": "本地·文学"},
    {"content": "花开如火，也如寂寞。", "author": "顾城", "src": "本地·文学"},
]


def fetch_local():
    q = random.choice(LOCAL_QUOTES)
    q["image"] = match_image(q["content"])
    return q


# ── 质量控制 ──────────────────────────────────────────

BLACKLIST = ["广告", "推广", "扫码", "加微信", "加我QQ", "关注公众号",
             "点击下载", "赚钱", "兼职", "理财", "贷款", "加群", "转发"]


def is_quality(text):
    if not text or len(text) < 12 or len(text) > 220:
        return False
    for w in BLACKLIST:
        if w in text:
            return False
    cliches = ["加油你是最棒的", "阳光总在风雨后", "只要努力就能成功"]
    if sum(1 for c in cliches if c in text) >= 2:
        return False
    return True


# ── 主流程 ─────────────────────────────────────────────

def main():
    candidates = []

    # 平台 1: 一言 (4 次)
    for _ in range(5):
        item = fetch_hitokoto()
        if item:
            candidates.append(item)

    # 平台 2: 每日一文 (2 次)
    for _ in range(3):
        item = fetch_meiriyiwen()
        if item:
            candidates.append(item)

    # 平台 3-5: 本地精选 (6 条去重)
    seen = set()
    for _ in range(7):
        item = fetch_local()
        k = item["content"][:30]
        if k not in seen:
            seen.add(k)
            candidates.append(item)

    # 过滤
    filtered = [c for c in candidates if is_quality(c["content"])]
    print(f"[sync] 抓取 {len(candidates)} 条, 质量过滤后 {len(filtered)} 条")

    if not filtered:
        print("[sync] 无内容可推送")
        return

    # POST 到 Render
    result = _post("/api/review/queue", {"items": filtered})
    if result and result.get("success"):
        print(f"[sync] 成功：{result.get('added', 0)} 条已加入审核队列")
    else:
        print(f"[sync] 推送失败：{result}")


if __name__ == "__main__":
    main()
