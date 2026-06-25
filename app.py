"""
「唯一」— 高质量文艺社区
Flask 后端：SQLite 数据库 + 内容策展 + 漂流瓶 + 每日星语
"""
import os
import sqlite3
import json
import random
import datetime
from functools import wraps
from flask import Flask, g, request, jsonify, render_template, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'data', 'weiyi.db')

# 确保 data 目录存在
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# ═══════════════════ 数据库 ═══════════════════

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            image TEXT DEFAULT '',
            mood TEXT DEFAULT '其他',
            mood_emoji TEXT DEFAULT '✨',
            mood_color TEXT DEFAULT '#c8963e',
            nickname TEXT DEFAULT '匿名星尘',
            fingerprint TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            like_count INTEGER DEFAULT 0,
            hug_count INTEGER DEFAULT 0,
            is_curated INTEGER DEFAULT 0,
            category TEXT DEFAULT '',
            source TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            fingerprint TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(post_id, fingerprint, type),
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS daily_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            author TEXT DEFAULT '',
            source TEXT DEFAULT '',
            used_count INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_posts_curated ON posts(is_curated);
        CREATE INDEX IF NOT EXISTS idx_interactions_post ON interactions(post_id);
    """)
    db.commit()
    db.close()

def seed_content():
    """种子数据：高质量文艺内容"""
    db = sqlite3.connect(DATABASE)

    curated_posts = [
        # 诗歌
        {
            "content": "我想和你一起生活\n在某个小镇，\n共享无尽的黄昏\n和绵绵不绝的钟声。\n—— 茨维塔耶娃《我想和你一起生活》",
            "mood": "其他", "mood_emoji": "✨", "mood_color": "#c8963e",
            "nickname": "诗歌星尘", "is_curated": 1, "category": "诗歌",
            "source": "茨维塔耶娃"
        },
        {
            "content": "我给你瘦落的街道、绝望的落日、荒郊的月亮。\n我给你一个久久地望着孤月的人的悲哀。\n—— 博尔赫斯《我用什么才能留住你》",
            "mood": "难过", "mood_emoji": "😢", "mood_color": "#7b9ec7",
            "nickname": "诗歌星尘", "is_curated": 1, "category": "诗歌",
            "source": "博尔赫斯"
        },
        {
            "content": "从前的日色变得慢\n车，马，邮件都慢\n一生只够爱一个人\n—— 木心《从前慢》",
            "mood": "感恩", "mood_emoji": "🙏", "mood_color": "#e0b088",
            "nickname": "诗歌星尘", "is_curated": 1, "category": "诗歌",
            "source": "木心"
        },
        {
            "content": "你一会看我\n一会看云\n我觉得\n你看我时很远\n你看云时很近\n—— 顾城《远和近》",
            "mood": "迷茫", "mood_emoji": "🤔", "mood_color": "#8ba5a5",
            "nickname": "诗歌星尘", "is_curated": 1, "category": "诗歌",
            "source": "顾城"
        },
        # 语录
        {
            "content": "我们读诗写诗，并不是因为它们好玩，而是因为我们是人类的一分子，而人类是充满激情的。\n医药、法律、商业、工程，这些都是高贵的理想，并且是维生的必需条件。\n但是诗、美、浪漫、爱，这些才是我们生存的原因。\n—— 《死亡诗社》",
            "mood": "其他", "mood_emoji": "✨", "mood_color": "#c8963e",
            "nickname": "光影星尘", "is_curated": 1, "category": "语录",
            "source": "《死亡诗社》"
        },
        {
            "content": "世界上只有一种真正的英雄主义，那就是在认清生活真相之后依然热爱生活。\n—— 罗曼·罗兰",
            "mood": "感恩", "mood_emoji": "🙏", "mood_color": "#e0b088",
            "nickname": "哲思星尘", "is_curated": 1, "category": "语录",
            "source": "罗曼·罗兰"
        },
        {
            "content": "我步入丛林，因为我希望生活得有意义。\n我希望活得深刻，吸取生命中所有的精华。\n把非生命的一切都击溃，以免当我生命终结时，发现自己从没有活过。\n—— 梭罗《瓦尔登湖》",
            "mood": "迷茫", "mood_emoji": "🤔", "mood_color": "#8ba5a5",
            "nickname": "哲思星尘", "is_curated": 1, "category": "语录",
            "source": "梭罗"
        },
        {
            "content": "活着本身就很美妙，如果连这道理都不懂，怎么去探索更深的东西？\n—— 《三体》",
            "mood": "其他", "mood_emoji": "✨", "mood_color": "#c8963e",
            "nickname": "光影星尘", "is_curated": 1, "category": "语录",
            "source": "刘慈欣"
        },
        # 随笔
        {
            "content": "每个人心里都有一团火，路过的人只看到烟。\n但是总有一个人，总有那么一个人能看到这团火，然后走过来，陪我一起。\n—— 梵高",
            "mood": "难过", "mood_emoji": "😢", "mood_color": "#7b9ec7",
            "nickname": "艺文星尘", "is_curated": 1, "category": "随笔",
            "source": "梵高书信"
        },
        {
            "content": "你要搞清楚自己人生的剧本——不是你父母的续集，不是你子女的前传，更不是你朋友的外篇。\n—— 尼采",
            "mood": "愤怒", "mood_emoji": "😡", "mood_color": "#c47a6e",
            "nickname": "哲思星尘", "is_curated": 1, "category": "语录",
            "source": "尼采"
        },
        # 音乐相关
        {
            "content": "音乐是灵魂的避难所。\n当你无法用语言表达时，音乐替你说话。\n—— 贝多芬",
            "mood": "其他", "mood_emoji": "✨", "mood_color": "#c8963e",
            "nickname": "音符星尘", "is_curated": 1, "category": "音乐",
            "source": "古典乐"
        },
        {
            "content": "我曾见过你们人类无法置信的事情：\n战舰在猎户座的边缘起火燃烧；\nC射线在星门附近的黑暗中闪耀……\n所有这些瞬间终将在时光中湮没，\n一如雨中的泪水。\n—— 《银翼杀手》",
            "mood": "迷茫", "mood_emoji": "🤔", "mood_color": "#8ba5a5",
            "nickname": "光影星尘", "is_curated": 1, "category": "语录",
            "source": "《银翼杀手》"
        },
        {
            "content": "凌晨四点钟，我看见海棠花未眠。\n总觉得这时，你应该在我身边。\n—— 川端康成《花未眠》",
            "mood": "难过", "mood_emoji": "😢", "mood_color": "#7b9ec7",
            "nickname": "文学星尘", "is_curated": 1, "category": "随笔",
            "source": "川端康成"
        },
        {
            "content": "我所有的自负都来自我的自卑，所有的英雄气概都来自于我内心的软弱，所有的振振有词都因为心中满是怀疑。\n我假装无情，其实是痛恨自己的深情。\n—— 马良《坦白书》",
            "mood": "焦虑", "mood_emoji": "😰", "mood_color": "#9b8ec4",
            "nickname": "文学星尘", "is_curated": 1, "category": "随笔",
            "source": "马良"
        },
        {
            "content": "如果有来生，要做一棵树，\n站成永恒，没有悲欢的姿势。\n一半在尘土里安详，一半在风里飞扬，\n一半洒落阴凉，一半沐浴阳光。\n—— 三毛",
            "mood": "其他", "mood_emoji": "✨", "mood_color": "#c8963e",
            "nickname": "诗歌星尘", "is_curated": 1, "category": "诗歌",
            "source": "三毛"
        },
    ]

    daily_msgs = [
        {"message": "你不需要完美，你只需要真实。", "author": "", "source": ""},
        {"message": "今晚的月色真美。", "author": "夏目漱石", "source": ""},
        {"message": "万物皆有裂痕，那是光照进来的地方。", "author": "莱昂纳德·科恩", "source": ""},
        {"message": "不管前方的路有多苦，只要走的方向正确，都比站在原地更接近幸福。", "author": "宫崎骏", "source": "《千与千寻》"},
        {"message": "人生就像一盒巧克力，你永远不知道下一颗是什么味道。", "author": "", "source": "《阿甘正传》"},
        {"message": "我们仰望同一片星空，却看着不同的地方。", "author": "新海诚", "source": "《秒速五厘米》"},
        {"message": "重要的不是治愈，而是带着病痛活下去。", "author": "加缪", "source": ""},
        {"message": "每一个不曾起舞的日子，都是对生命的辜负。", "author": "尼采", "source": ""},
        {"message": "我来到这个世界，为了看看太阳和蓝色的地平线。", "author": "巴尔蒙特", "source": ""},
        {"message": "爱是唯一可以超越时间与空间的事物。", "author": "", "source": "《星际穿越》"},
        {"message": "真正的高贵不是优于别人，而是优于过去的自己。", "author": "海明威", "source": ""},
        {"message": "没有一个冬天不可逾越，没有一个春天不会来临。", "author": "", "source": ""},
        {"message": "世界以痛吻我，要我报之以歌。", "author": "泰戈尔", "source": ""},
        {"message": "人的一切痛苦，本质上都是对自己无能的愤怒。", "author": "王小波", "source": ""},
        {"message": "人生若无悔，那该多无趣啊。", "author": "", "source": "《一代宗师》"},
        {"message": "念念不忘，必有回响。", "author": "", "source": "《一代宗师》"},
        {"message": "当你年轻时，以为什么都离自己很近，但当你长大后才发现，其实一切都很遥远。", "author": "", "source": "《请回答1988》"},
        {"message": "愿你走出半生，归来仍是少年。", "author": "", "source": ""},
        {"message": "生活明朗，万物可爱。人间值得，未来可期。", "author": "", "source": ""},
        {"message": "且将新火试新茶，诗酒趁年华。", "author": "苏轼", "source": "《望江南》"},
    ]

    fp = "curated_000"
    for p in curated_posts:
        db.execute(
            """INSERT OR IGNORE INTO posts
            (content, mood, mood_emoji, mood_color, nickname, fingerprint, is_curated, category, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, datetime('now', '-' || abs(random() % 72) || ' hours'))""",
            (p['content'], p['mood'], p['mood_emoji'], p['mood_color'], p['nickname'], fp, p['category'], p['source'])
        )

    for m in daily_msgs:
        db.execute(
            "INSERT OR IGNORE INTO daily_messages (message, author, source) VALUES (?, ?, ?)",
            (m['message'], m['author'], m['source'])
        )

    db.commit()
    db.close()

# ═══════════════════ 初始化 ═══════════════════

with app.app_context():
    init_db()
    # 检查是否需要种子
    db = sqlite3.connect(DATABASE)
    c = db.execute("SELECT COUNT(*) FROM posts").fetchone()
    if c[0] == 0:
        db.close()
        seed_content()
    else:
        db.close()

# ═══════════════════ API 路由 ═══════════════════

MOOD_MAP = {
    '开心': {'emoji': '😊', 'color': '#e8c76a'},
    '难过': {'emoji': '😢', 'color': '#7b9ec7'},
    '愤怒': {'emoji': '😡', 'color': '#c47a6e'},
    '焦虑': {'emoji': '😰', 'color': '#9b8ec4'},
    '迷茫': {'emoji': '🤔', 'color': '#8ba5a5'},
    '感恩': {'emoji': '🙏', 'color': '#e0b088'},
    '其他': {'emoji': '✨', 'color': '#c8963e'},
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    fingerprint = request.args.get('fingerprint', '')
    per_page = 15

    db = get_db()
    offset = (page - 1) * per_page

    posts = db.execute("""
        SELECT p.*,
               (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like') > 0 as liked_by_me,
               (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug') > 0 as hugged_by_me
        FROM posts p
        ORDER BY p.is_curated DESC, p.created_at DESC
        LIMIT ? OFFSET ?
    """, (fingerprint, fingerprint, per_page + 1, offset)).fetchall()

    has_more = len(posts) > per_page
    posts = posts[:per_page]

    return jsonify({
        'posts': [dict(p) for p in posts],
        'has_more': has_more,
        'page': page
    })


@app.route('/api/posts/curated')
def get_curated():
    """获取策展内容按分类"""
    db = get_db()
    fingerprint = request.args.get('fingerprint', '')

    categories = db.execute(
        "SELECT DISTINCT category FROM posts WHERE is_curated=1 AND category != ''"
    ).fetchall()

    result = {}
    for cat in categories:
        posts = db.execute("""
            SELECT p.*,
                   (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like') > 0 as liked_by_me,
                   (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug') > 0 as hugged_by_me
            FROM posts p
            WHERE p.is_curated=1 AND p.category=?
            ORDER BY p.created_at DESC
            LIMIT 6
        """, (fingerprint, fingerprint, cat['category'])).fetchall()
        result[cat['category']] = [dict(p) for p in posts]

    return jsonify({'categories': result})


@app.route('/api/posts/random')
def random_post():
    fingerprint = request.args.get('fingerprint', '')
    db = get_db()

    post = db.execute("""
        SELECT p.*,
               (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like') > 0 as liked_by_me,
               (SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug') > 0 as hugged_by_me
        FROM posts p
        ORDER BY RANDOM()
        LIMIT 1
    """, (fingerprint, fingerprint)).fetchone()

    if not post:
        return jsonify({'error': '海洋太安静了，还没有漂流瓶……'}), 404

    return jsonify(dict(post))


@app.route('/api/daily-message')
def daily_message():
    db = get_db()
    today = datetime.date.today()
    seed = today.year * 10000 + today.month * 100 + today.day

    messages = db.execute("SELECT * FROM daily_messages").fetchall()
    if not messages:
        return jsonify({'message': '享受今晚。'})

    idx = seed % len(messages)
    msg = messages[idx]

    db.execute("UPDATE daily_messages SET used_count = used_count + 1 WHERE id = ?", (msg['id'],))
    db.commit()

    return jsonify({
        'message': msg['message'],
        'author': msg['author'],
        'source': msg['source']
    })


@app.route('/api/post', methods=['POST'])
def create_post():
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'error': '请写点什么吧'}), 400
    if len(content) > 1000:
        return jsonify({'success': False, 'error': '内容过长，限1000字'}), 400

    mood = data.get('mood', '其他')
    mood_info = MOOD_MAP.get(mood, MOOD_MAP['其他'])
    nickname = data.get('nickname', '').strip() or '匿名星尘'
    image = data.get('image', '')
    fingerprint = data.get('fingerprint', '')

    db = get_db()
    cur = db.execute("""
        INSERT INTO posts (content, image, mood, mood_emoji, mood_color, nickname, fingerprint)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (content, image, mood, mood_info['emoji'], mood_info['color'], nickname, fingerprint))
    db.commit()

    post = db.execute("SELECT * FROM posts WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify({'success': True, 'post': dict(post)})


@app.route('/api/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    data = request.get_json()
    fingerprint = data.get('fingerprint', '')

    db = get_db()
    existing = db.execute(
        "SELECT id FROM interactions WHERE post_id=? AND fingerprint=? AND type='like'",
        (post_id, fingerprint)
    ).fetchone()

    if existing:
        db.execute("DELETE FROM interactions WHERE id=?", (existing['id'],))
        db.execute("UPDATE posts SET like_count = like_count - 1 WHERE id=?", (post_id,))
        action = 'unliked'
    else:
        db.execute(
            "INSERT INTO interactions (post_id, fingerprint, type) VALUES (?, ?, 'like')",
            (post_id, fingerprint)
        )
        db.execute("UPDATE posts SET like_count = like_count + 1 WHERE id=?", (post_id,))
        action = 'liked'

    db.commit()
    post = db.execute("SELECT like_count FROM posts WHERE id=?", (post_id,)).fetchone()
    return jsonify({'action': action, 'like_count': post['like_count']})


@app.route('/api/post/<int:post_id>/hug', methods=['POST'])
def hug_post(post_id):
    data = request.get_json()
    fingerprint = data.get('fingerprint', '')

    db = get_db()
    existing = db.execute(
        "SELECT id FROM interactions WHERE post_id=? AND fingerprint=? AND type='hug'",
        (post_id, fingerprint)
    ).fetchone()

    if existing:
        db.execute("DELETE FROM interactions WHERE id=?", (existing['id'],))
        db.execute("UPDATE posts SET hug_count = hug_count - 1 WHERE id=?", (post_id,))
        action = 'unhugged'
    else:
        db.execute(
            "INSERT INTO interactions (post_id, fingerprint, type) VALUES (?, ?, 'hug')",
            (post_id, fingerprint)
        )
        db.execute("UPDATE posts SET hug_count = hug_count + 1 WHERE id=?", (post_id,))
        action = 'hugged'

    db.commit()
    post = db.execute("SELECT hug_count FROM posts WHERE id=?", (post_id,)).fetchone()
    return jsonify({'action': action, 'hug_count': post['hug_count']})


@app.route('/api/post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = request.get_json()
    fingerprint = data.get('fingerprint', '')

    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=? AND fingerprint=?", (post_id, fingerprint)).fetchone()
    if not post:
        return jsonify({'success': False, 'error': '无权删除此星尘'}), 403

    db.execute("DELETE FROM interactions WHERE post_id=?", (post_id,))
    db.execute("DELETE FROM posts WHERE id=?", (post_id,))
    db.commit()

    return jsonify({'success': True})


@app.route('/api/my-posts')
def my_posts():
    fingerprint = request.args.get('fingerprint', '')
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts WHERE fingerprint=? ORDER BY created_at DESC LIMIT 50",
        (fingerprint,)
    ).fetchall()
    return jsonify({'posts': [dict(p) for p in posts]})


# ═══════════════════ 启动 ═══════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
