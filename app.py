"""
唯一 — 高质量文艺社区 v3.1
Flask 单文件部署：HTML/CSS/JS 全部内联
"""
import os
import sqlite3
import datetime
from flask import Flask, g, request, jsonify

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'data', 'weiyi.db')
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# ═══════ DB ═══════
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL, image TEXT DEFAULT '',
            mood TEXT DEFAULT '其他', mood_emoji TEXT DEFAULT '✨', mood_color TEXT DEFAULT '#c8963e',
            nickname TEXT DEFAULT '匿名星尘', fingerprint TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            like_count INTEGER DEFAULT 0, hug_count INTEGER DEFAULT 0,
            is_curated INTEGER DEFAULT 0, category TEXT DEFAULT '', source TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL, fingerprint TEXT NOT NULL, type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(post_id, fingerprint, type),
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS daily_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL, author TEXT DEFAULT '', source TEXT DEFAULT '', used_count INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_posts_curated ON posts(is_curated);
        CREATE INDEX IF NOT EXISTS idx_interactions_post ON interactions(post_id);
    """)
    db.commit(); db.close()

def seed():
    db = sqlite3.connect(DATABASE)
    curated = [
        ("我想和你一起生活\n在某个小镇，\n共享无尽的黄昏\n和绵绵不绝的钟声。\n—— 茨维塔耶娃《我想和你一起生活》","其他","✨","#c8963e","诗歌星尘","诗歌","茨维塔耶娃"),
        ("我给你瘦落的街道、绝望的落日、荒郊的月亮。\n我给你一个久久地望着孤月的人的悲哀。\n—— 博尔赫斯《我用什么才能留住你》","难过","😢","#7b9ec7","诗歌星尘","诗歌","博尔赫斯"),
        ("从前的日色变得慢\n车，马，邮件都慢\n一生只够爱一个人\n—— 木心《从前慢》","感恩","🙏","#e0b088","诗歌星尘","诗歌","木心"),
        ("你一会看我\n一会看云\n我觉得\n你看我时很远\n你看云时很近\n—— 顾城《远和近》","迷茫","🤔","#8ba5a5","诗歌星尘","诗歌","顾城"),
        ("我们读诗写诗，并不是因为它们好玩，而是因为我们是人类的一分子。\n医药、法律、商业、工程，这些都是高贵的理想。\n但是诗、美、浪漫、爱，这些才是我们生存的原因。\n—— 《死亡诗社》","其他","✨","#c8963e","光影星尘","语录","《死亡诗社》"),
        ("世界上只有一种真正的英雄主义，那就是在认清生活真相之后依然热爱生活。\n—— 罗曼·罗兰","感恩","🙏","#e0b088","哲思星尘","语录","罗曼·罗兰"),
        ("我步入丛林，因为我希望生活得有意义。\n我希望活得深刻，吸取生命中所有的精华。\n把非生命的一切都击溃，以免当我生命终结时，发现自己从没有活过。\n—— 梭罗《瓦尔登湖》","迷茫","🤔","#8ba5a5","哲思星尘","语录","梭罗"),
        ("活着本身就很美妙，如果连这道理都不懂，怎么去探索更深的东西？\n—— 《三体》","其他","✨","#c8963e","光影星尘","语录","刘慈欣"),
        ("每个人心里都有一团火，路过的人只看到烟。\n但是总有一个人，总有那么一个人能看到这团火，然后走过来，陪我一起。\n—— 梵高","难过","😢","#7b9ec7","艺文星尘","随笔","梵高书信"),
        ("你要搞清楚自己人生的剧本——不是你父母的续集，不是你子女的前传，更不是你朋友的外篇。\n—— 尼采","愤怒","😡","#c47a6e","哲思星尘","语录","尼采"),
        ("音乐是灵魂的避难所。\n当你无法用语言表达时，音乐替你说话。\n—— 贝多芬","其他","✨","#c8963e","音符星尘","音乐","古典乐"),
        ("我曾见过你们人类无法置信的事情：\n战舰在猎户座的边缘起火燃烧；\nC射线在星门附近的黑暗中闪耀……\n所有这些瞬间终将在时光中湮没，\n一如雨中的泪水。\n—— 《银翼杀手》","迷茫","🤔","#8ba5a5","光影星尘","语录","《银翼杀手》"),
        ("凌晨四点钟，我看见海棠花未眠。\n总觉得这时，你应该在我身边。\n—— 川端康成《花未眠》","难过","😢","#7b9ec7","文学星尘","随笔","川端康成"),
        ("我所有的自负都来自我的自卑，所有的英雄气概都来自于我内心的软弱，所有的振振有词都因为心中满是怀疑。\n我假装无情，其实是痛恨自己的深情。\n—— 马良《坦白书》","焦虑","😰","#9b8ec4","文学星尘","随笔","马良"),
        ("如果有来生，要做一棵树，\n站成永恒，没有悲欢的姿势。\n一半在尘土里安详，一半在风里飞扬，\n一半洒落阴凉，一半沐浴阳光。\n—— 三毛","其他","✨","#c8963e","诗歌星尘","诗歌","三毛"),
    ]
    daily = [
        ("你不需要完美，你只需要真实。","",""),
        ("今晚的月色真美。","夏目漱石",""),
        ("万物皆有裂痕，那是光照进来的地方。","莱昂纳德·科恩",""),
        ("不管前方的路有多苦，只要走的方向正确，都比站在原地更接近幸福。","宫崎骏","《千与千寻》"),
        ("人生就像一盒巧克力，你永远不知道下一颗是什么味道。","","《阿甘正传》"),
        ("我们仰望同一片星空，却看着不同的地方。","新海诚","《秒速五厘米》"),
        ("重要的不是治愈，而是带着病痛活下去。","加缪",""),
        ("每一个不曾起舞的日子，都是对生命的辜负。","尼采",""),
        ("我来到这个世界，为了看看太阳和蓝色的地平线。","巴尔蒙特",""),
        ("爱是唯一可以超越时间与空间的事物。","","《星际穿越》"),
        ("真正的高贵不是优于别人，而是优于过去的自己。","海明威",""),
        ("没有一个冬天不可逾越，没有一个春天不会来临。","",""),
        ("世界以痛吻我，要我报之以歌。","泰戈尔",""),
        ("人的一切痛苦，本质上都是对自己无能的愤怒。","王小波",""),
        ("人生若无悔，那该多无趣啊。","","《一代宗师》"),
        ("念念不忘，必有回响。","","《一代宗师》"),
        ("愿你走出半生，归来仍是少年。","",""),
    ]
    fp="curated_000"
    for c,m,me,mc,nick,cat,src in curated:
        db.execute("INSERT OR IGNORE INTO posts(content,mood,mood_emoji,mood_color,nickname,fingerprint,is_curated,category,source,created_at) VALUES(?,?,?,?,?,?,1,?,?,datetime('now','-'||abs(random()%72)||' hours'))",(c,m,me,mc,nick,fp,cat,src))
    for m,a,s in daily:
        db.execute("INSERT OR IGNORE INTO daily_messages(message,author,source) VALUES(?,?,?)",(m,a,s))
    db.commit(); db.close()

with app.app_context():
    init_db()
    db=sqlite3.connect(DATABASE)
    n=db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    db.close()
    if n==0: seed()

# ═══════ API ═══════
MM={'开心':{'emoji':'😊','color':'#e8c76a'},'难过':{'emoji':'😢','color':'#7b9ec7'},'愤怒':{'emoji':'😡','color':'#c47a6e'},'焦虑':{'emoji':'😰','color':'#9b8ec4'},'迷茫':{'emoji':'🤔','color':'#8ba5a5'},'感恩':{'emoji':'🙏','color':'#e0b088'},'其他':{'emoji':'✨','color':'#c8963e'}}

@app.route('/api/posts')
def api_posts():
    p=request.args.get('page',1,type=int); fp=request.args.get('fingerprint',''); pp=15
    db=get_db(); off=(p-1)*pp
    ps=db.execute("SELECT p.*,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like')>0 as l,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug')>0 as h FROM posts p ORDER BY p.is_curated DESC,p.created_at DESC LIMIT ? OFFSET ?",(fp,fp,pp+1,off)).fetchall()
    hm=len(ps)>pp; ps=ps[:pp]
    return jsonify({'posts':[dict(x) for x in ps],'has_more':hm,'page':p})

@app.route('/api/posts/curated')
def api_curated():
    fp=request.args.get('fingerprint',''); db=get_db()
    cats=db.execute("SELECT DISTINCT category FROM posts WHERE is_curated=1 AND category!=''").fetchall()
    r={}
    for c in cats:
        ps=db.execute("SELECT p.*,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like')>0 as l,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug')>0 as h FROM posts p WHERE p.is_curated=1 AND p.category=? ORDER BY p.created_at DESC LIMIT 6",(fp,fp,c['category'])).fetchall()
        r[c['category']]=[dict(x) for x in ps]
    return jsonify({'categories':r})

@app.route('/api/posts/random')
def api_random():
    fp=request.args.get('fingerprint',''); db=get_db()
    p=db.execute("SELECT p.*,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='like')>0 as l,(SELECT COUNT(*) FROM interactions WHERE post_id=p.id AND fingerprint=? AND type='hug')>0 as h FROM posts p ORDER BY RANDOM() LIMIT 1",(fp,fp)).fetchone()
    if not p: return jsonify({'error':'海洋太安静了，还没有漂流瓶……'}),404
    return jsonify(dict(p))

@app.route('/api/daily-message')
def api_daily():
    db=get_db(); td=datetime.date.today(); s=td.year*10000+td.month*100+td.day
    ms=db.execute("SELECT * FROM daily_messages").fetchall()
    if not ms: return jsonify({'message':'享受今晚。'})
    m=ms[s%len(ms)]; db.execute("UPDATE daily_messages SET used_count=used_count+1 WHERE id=?",(m['id'],)); db.commit()
    return jsonify({'message':m['message'],'author':m['author'],'source':m['source']})

@app.route('/api/post',methods=['POST'])
def api_create():
    d=request.get_json(); c=d.get('content','').strip()
    if not c: return jsonify({'success':False,'error':'请写点什么吧'}),400
    if len(c)>1000: return jsonify({'success':False,'error':'内容过长'}),400
    mi=MM.get(d.get('mood','其他'),MM['其他']); nn=d.get('nickname','').strip() or '匿名星尘'; fp=d.get('fingerprint',''); img=d.get('image','')
    db=get_db(); cur=db.execute("INSERT INTO posts(content,image,mood,mood_emoji,mood_color,nickname,fingerprint) VALUES(?,?,?,?,?,?,?)",(c,img,d.get('mood','其他'),mi['emoji'],mi['color'],nn,fp)); db.commit()
    return jsonify({'success':True,'post':dict(db.execute("SELECT * FROM posts WHERE id=?",(cur.lastrowid,)).fetchone())})

@app.route('/api/post/<int:pid>/like',methods=['POST'])
def api_like(pid):
    fp=request.get_json().get('fingerprint',''); db=get_db()
    ex=db.execute("SELECT id FROM interactions WHERE post_id=? AND fingerprint=? AND type='like'",(pid,fp)).fetchone()
    if ex: db.execute("DELETE FROM interactions WHERE id=?",(ex['id'],)); db.execute("UPDATE posts SET like_count=like_count-1 WHERE id=?",(pid,)); act='unliked'
    else: db.execute("INSERT INTO interactions(post_id,fingerprint,type) VALUES(?,?,'like')",(pid,fp)); db.execute("UPDATE posts SET like_count=like_count+1 WHERE id=?",(pid,)); act='liked'
    db.commit(); return jsonify({'action':act,'like_count':db.execute("SELECT like_count FROM posts WHERE id=?",(pid,)).fetchone()['like_count']})

@app.route('/api/post/<int:pid>/hug',methods=['POST'])
def api_hug(pid):
    fp=request.get_json().get('fingerprint',''); db=get_db()
    ex=db.execute("SELECT id FROM interactions WHERE post_id=? AND fingerprint=? AND type='hug'",(pid,fp)).fetchone()
    if ex: db.execute("DELETE FROM interactions WHERE id=?",(ex['id'],)); db.execute("UPDATE posts SET hug_count=hug_count-1 WHERE id=?",(pid,)); act='unhugged'
    else: db.execute("INSERT INTO interactions(post_id,fingerprint,type) VALUES(?,?,'hug')",(pid,fp)); db.execute("UPDATE posts SET hug_count=hug_count+1 WHERE id=?",(pid,)); act='hugged'
    db.commit(); return jsonify({'action':act,'hug_count':db.execute("SELECT hug_count FROM posts WHERE id=?",(pid,)).fetchone()['hug_count']})

@app.route('/api/post/<int:pid>',methods=['DELETE'])
def api_delete(pid):
    fp=request.get_json().get('fingerprint',''); db=get_db()
    if not db.execute("SELECT * FROM posts WHERE id=? AND fingerprint=?",(pid,fp)).fetchone(): return jsonify({'success':False,'error':'无权删除'}),403
    db.execute("DELETE FROM interactions WHERE post_id=?",(pid,)); db.execute("DELETE FROM posts WHERE id=?",(pid,)); db.commit()
    return jsonify({'success':True})

@app.route('/api/my-posts')
def api_mine():
    fp=request.args.get('fingerprint',''); db=get_db()
    return jsonify({'posts':[dict(x) for x in db.execute("SELECT * FROM posts WHERE fingerprint=? ORDER BY created_at DESC LIMIT 50",(fp,)).fetchall()]})


# ═══════ HTML 模板（内联） ═══════
_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#080c1a">
<title>唯一 — 享受今晚</title>

<!-- Fonts: 系统字体栈，无需外部加载 -->
<style>
/* ═══════════════════════════════════════════════════════
   「唯一」 Design System v4 — Premium
   核心隐喻：星尘·宇宙·漂流
   ═══════════════════════════════════════════════════════ */

/* ═══ Design Tokens ═══ */
:root {
  /* 暗色宇宙调色板 */
  --space-deep: #010308;
  --space: #060b18;
  --space-light: #0d1530;
  --surface: rgba(9, 16, 40, 0.65);
  --surface-hover: rgba(18, 28, 58, 0.82);
  --glass: rgba(12, 18, 40, 0.75);
  --glass-border: rgba(212, 168, 83, 0.08);

  /* 文字层级 */
  --text-primary: #ece6d5;
  --text-secondary: #a4a6b8;
  --text-tertiary: #72758a;
  --text-muted: #4e5164;

  /* 强调色 */
  --gold: #c9a045;
  --gold-light: #e4c36a;
  --gold-soft: rgba(201, 160, 69, 0.08);
  --rose: #c97a82;
  --rose-soft: rgba(201, 122, 130, 0.06);
  --rose-deep: #a65c64;

  /* 分类色 */
  --cat-poetry: #e4c36a;
  --cat-quote: #7bb8d4;
  --cat-essay: #9b8ec4;
  --cat-music: #c97a82;
  --cat-film: #8ba5a5;

  /* 间距与圆角 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 20px;
  --space-lg: 32px;
  --space-xl: 48px;
  --space-2xl: 72px;
  --radius-sm: 10px;
  --radius: 18px;
  --radius-lg: 26px;
  --radius-xl: 36px;
  --radius-full: 9999px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 24px rgba(0,0,0,0.35);
  --shadow-lg: 0 8px 48px rgba(0,0,0,0.45);
  --shadow-gold: 0 0 80px rgba(201, 160, 69, 0.05);
  --shadow-card: 0 2px 8px rgba(0,0,0,0.3), 0 8px 32px rgba(0,0,0,0.2);

  /* 动效 */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --duration-fast: 180ms;
  --duration-normal: 400ms;
  --duration-slow: 700ms;

  /* 字体 */
  --font-serif: 'SimSun', 'STSong', 'Noto Serif SC', serif;
  --font-sans: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
}

/* ═══ Reset ═══ */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  background: var(--space-deep);
  color: var(--text-primary);
  min-height: 100vh;
  min-height: 100dvh;
  -webkit-tap-highlight-color: transparent;
  overflow-x: hidden;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

::selection {
  background: rgba(212, 168, 83, 0.2);
  color: var(--text-primary);
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(212, 168, 83, 0.12); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(212, 168, 83, 0.25); }

/* ═══ Canvas 星空 ═══ */
.stars-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
#starCanvas { width: 100%; height: 100%; }

/* ═══ App 容器 ═══ */
.app {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ═══════════════════ Hero ═══════════════════ */
.hero {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-xl);
  text-align: center;
  overflow: hidden;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0; right: 0;
  height: 180px;
  background: linear-gradient(transparent, var(--space-deep));
  z-index: 3;
  pointer-events: none;
}

.hero-constellation {
  position: absolute;
  inset: 0;
  opacity: 0.6;
}
.hero-constellation canvas { width: 100%; height: 100%; }

.hero-content {
  position: relative;
  z-index: 2;
  animation: heroReveal 1.4s var(--ease-out) both;
}

@keyframes heroReveal {
  from { opacity: 0; transform: translateY(48px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(56px, 10vw, 96px);
  font-weight: 700;
  letter-spacing: 0.2em;
  display: flex;
  gap: 0.2em;
  justify-content: center;
  margin-bottom: var(--space-lg);
  text-shadow: 0 0 80px rgba(201,160,69,0.25);
}

.hero-char {
  display: inline-block;
  background: linear-gradient(180deg, #f0d78c 0%, var(--gold) 35%, #8a5c1e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: charFloat 4s ease-in-out infinite;
}
.hero-char:nth-child(1) { animation-delay: 0s; }
.hero-char:nth-child(2) { animation-delay: 0.2s; }

@keyframes charFloat {
  0%, 100% { transform: translateY(0); filter: brightness(1); }
  50% { transform: translateY(-8px); filter: brightness(1.2); }
}

.hero-subtitle {
  font-family: var(--font-serif);
  font-size: clamp(16px, 2.8vw, 22px);
  color: var(--text-secondary);
  font-weight: 400;
  letter-spacing: 0.18em;
  margin-bottom: var(--space-2xl);
  opacity: 0;
  animation: subtitleReveal 1.2s 0.6s var(--ease-out) forwards;
}

@keyframes subtitleReveal {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 0.7; transform: translateY(0); }
}

.hero-daily {
  display: inline-block;
  font-family: var(--font-serif);
  font-size: 15px;
  font-style: italic;
  color: var(--gold-light);
  opacity: 0.65;
  letter-spacing: 0.08em;
  line-height: 1.8;
  max-width: 420px;
  padding: var(--space-md) var(--space-lg);
  background: var(--gold-soft);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(212, 168, 83, 0.08);
  animation: dailyPulse 4s ease-in-out infinite;
}

@keyframes dailyPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.hero-scroll {
  position: absolute;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--text-tertiary);
  cursor: pointer;
  animation: scrollBounce 2s ease-in-out infinite;
  opacity: 0.5;
  transition: opacity var(--duration-fast);
}
.hero-scroll:hover { opacity: 1; }

@keyframes scrollBounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(8px); }
}

/* ═══════════════════ Navigation ═══════════════════ */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px var(--space-lg);
  background: rgba(6, 9, 20, 0.78);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(212, 168, 83, 0.06);
  transition: all var(--duration-normal);
}

.nav.scrolled {
  box-shadow: 0 1px 20px rgba(0,0,0,0.3);
}

.nav-brand {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.2em;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  cursor: pointer;
  user-select: none;
}

.nav-tabs {
  display: flex;
  gap: 2px;
  background: rgba(255,255,255,0.02);
  border-radius: var(--radius-full);
  padding: 3px;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: inherit;
  transition: all var(--duration-normal);
  white-space: nowrap;
}
.nav-tab:hover { color: var(--text-secondary); }
.nav-tab:active { transform: scale(0.96); }
.nav-tab.active {
  color: var(--gold-light);
  background: var(--gold-soft);
  font-weight: 600;
}
.nav-tab-icon { font-size: 15px; line-height: 1; }
.nav-tab-label { letter-spacing: 0.04em; }

.nav-bottle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(212, 132, 140, 0.08);
  border: 1px solid rgba(212, 132, 140, 0.15);
  color: var(--rose);
  font-size: 18px;
  cursor: pointer;
  transition: all var(--duration-normal);
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-bottle:hover {
  background: rgba(212, 132, 140, 0.15);
  transform: scale(1.08);
}
.nav-bottle:active { transform: scale(0.92); }

/* ═══════════════════ Main Content ═══════════════════ */
.main {
  flex: 1;
  padding: var(--space-md) var(--space-lg) 120px;
  position: relative;
  z-index: 1;
}

.tab-content {
  display: none;
  animation: tabEnter 0.45s var(--ease-out);
}
.tab-content.active { display: block; }

@keyframes tabEnter {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════ Category Bar ═══════════════════ */
.category-bar {
  display: flex;
  gap: var(--space-sm);
  padding: var(--space-sm) 0 var(--space-lg);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  mask: linear-gradient(90deg, transparent, #000 3%, #000 97%, transparent);
  -webkit-mask: linear-gradient(90deg, transparent, #000 3%, #000 97%, transparent);
}
.category-bar::-webkit-scrollbar { display: none; }

.category-chip {
  flex-shrink: 0;
  padding: 7px 18px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255,255,255,0.06);
  background: var(--surface);
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--duration-normal);
  white-space: nowrap;
}
.category-chip:hover {
  border-color: rgba(212, 168, 83, 0.2);
  color: var(--text-secondary);
}
.category-chip.active {
  background: var(--gold-soft);
  border-color: var(--gold);
  color: var(--gold-light);
  font-weight: 600;
}

/* ═══════════════════ Masonry Grid ═══════════════════ */
.masonry {
  columns: 1;
  column-gap: var(--space-lg);
}
@media (min-width: 640px) { .masonry { columns: 2; } }
@media (min-width: 1024px) { .masonry { columns: 3; column-gap: var(--space-xl); } }

/* ═══ Post Card ═══ */
.post-card {
  break-inside: avoid;
  margin-bottom: var(--space-lg);
  background: var(--surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--radius);
  border: 1px solid var(--glass-border);
  padding: 28px 24px;
  transition: all 0.45s var(--ease-smooth);
  position: relative;
  overflow: hidden;
  cursor: default;
  box-shadow: var(--shadow-card);
  animation: cardAppear 0.6s var(--ease-out) both;
}

@keyframes cardAppear {
  from { opacity: 0; transform: translateY(32px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.post-card:hover {
  background: var(--surface-hover);
  border-color: rgba(201, 160, 69, 0.22);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg), 0 0 60px rgba(201, 160, 69, 0.06);
}

.post-card.curated {
  border-left: 3px solid var(--gold);
}

/* 卡片的左侧彩色条 */
.post-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  border-radius: 2px 0 0 2px;
  transition: width 0.3s var(--ease-smooth);
  opacity: 0.5;
}
.post-card:hover::before { width: 3px; opacity: 0.8; }

.post-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.post-card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}
.post-card-mood {
  font-size: 18px;
  line-height: 1;
}
.post-card-author {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.03em;
}
.post-card-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--gold-soft);
  color: var(--gold-light);
  font-weight: 500;
  letter-spacing: 0.05em;
}
.post-card-badge.poetry { background: rgba(232,199,106,0.1); color: var(--cat-poetry); }
.post-card-badge.quote { background: rgba(123,184,212,0.1); color: var(--cat-quote); }
.post-card-badge.essay { background: rgba(155,142,196,0.1); color: var(--cat-essay); }
.post-card-badge.music { background: rgba(212,132,140,0.1); color: var(--cat-music); }

.post-card-time {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

.post-card-body {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  font-weight: 400;
  letter-spacing: 0.02em;
}

.post-card-image {
  margin-top: 12px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.04);
}
.post-card-image img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}
.post-card:hover .post-card-image img {
  transform: scale(1.03);
}

.post-card-source {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
  text-align: right;
  opacity: 0.6;
}

.post-card-actions {
  display: flex;
  gap: 14px;
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.03);
}

.post-action {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 6px;
  transition: all var(--duration-fast);
  font-family: inherit;
}
.post-action:hover {
  background: rgba(255,255,255,0.04);
  color: var(--text-secondary);
}
.post-action:active { transform: scale(0.94); }
.post-action.liked { color: var(--rose); background: var(--rose-soft); }
.post-action.hugged { color: var(--gold-light); background: var(--gold-soft); }
.post-action-count {
  font-size: 12px;
  min-width: 16px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

/* Like 动画 */
@keyframes heartBurst {
  0% { transform: scale(1); }
  30% { transform: scale(1.3); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
.post-action.just-liked { animation: heartBurst 0.4s var(--ease-spring); }

/* ═══════════════════ Curated Page ═══════════════════ */
.curated-intro {
  text-align: center;
  padding: var(--space-xl) var(--space-lg) var(--space-2xl);
}
.curated-title {
  font-family: var(--font-serif);
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 0.1em;
  margin-bottom: var(--space-sm);
}
.curated-desc {
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 420px;
  margin: 0 auto;
  line-height: 1.7;
  opacity: 0.7;
}

.curated-section {
  margin-bottom: var(--space-2xl);
}
.curated-section-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.curated-section-icon { font-size: 20px; }
.curated-section-title {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.06em;
}
.curated-section-count {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.curated-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
}
@media (min-width: 640px) { .curated-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .curated-grid { grid-template-columns: repeat(3, 1fr); } }

/* ═══════════════════ Write Panel ═══════════════════ */
.write-panel {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--space-lg) 0;
}

.write-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}
.write-header h2 {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 0.08em;
  margin-bottom: var(--space-xs);
}
.write-header p {
  font-size: 13px;
  color: var(--text-tertiary);
}

.write-panel textarea {
  width: 100%;
  min-height: 200px;
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  color: var(--text-primary);
  padding: 18px 20px;
  font-size: 15px;
  line-height: 1.9;
  resize: vertical;
  font-family: inherit;
  transition: all var(--duration-normal);
  letter-spacing: 0.02em;
}
.write-panel textarea:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px var(--gold-soft);
}
.write-panel textarea::placeholder {
  color: var(--text-muted);
  opacity: 0.4;
  font-style: italic;
}

.write-char-count {
  text-align: right;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: var(--space-xs);
  padding-right: 4px;
}

.write-image-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin: var(--space-md) 0;
}
.write-image-name {
  font-size: 12px;
  color: var(--text-tertiary);
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.write-image-preview {
  display: block;
  max-width: 100%;
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-md);
  border: 1px solid rgba(255,255,255,0.06);
}

/* Mood Picker */
.mood-picker {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}
.mood-chip {
  padding: 8px 16px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255,255,255,0.06);
  background: var(--surface);
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--duration-normal);
  display: flex;
  align-items: center;
  gap: 5px;
}
.mood-chip:hover {
  border-color: rgba(212, 168, 83, 0.25);
  color: var(--text-secondary);
}
.mood-chip:active { transform: scale(0.95); }
.mood-chip.selected {
  border-color: var(--gold);
  color: var(--gold-light);
  background: var(--gold-soft);
  font-weight: 600;
}

.input-nickname {
  width: 100%;
  background: var(--surface);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 12px 16px;
  font-size: 14px;
  margin-bottom: var(--space-lg);
  font-family: inherit;
  transition: all var(--duration-normal);
}
.input-nickname:focus {
  outline: none;
  border-color: rgba(212, 168, 83, 0.3);
}

/* Buttons */
.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 1px dashed rgba(212, 168, 83, 0.2);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--duration-fast);
}
.btn-ghost:hover {
  border-color: var(--gold);
  color: var(--gold-light);
  background: rgba(212, 168, 83, 0.06);
}
.btn-ghost:active { transform: scale(0.97); }
.btn-ghost-danger { border-color: rgba(212,132,140,0.2); color: var(--rose); }
.btn-ghost-danger:hover { border-color: var(--rose); background: var(--rose-soft); }

.btn-send {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, var(--gold), #b88530);
  border: none;
  border-radius: var(--radius);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.1em;
  font-family: inherit;
  transition: all var(--duration-normal);
  box-shadow: 0 4px 24px rgba(212, 168, 83, 0.18);
  position: relative;
  overflow: hidden;
}
.btn-send::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent, rgba(255,255,255,0.1), transparent);
  opacity: 0;
  transition: opacity var(--duration-fast);
}
.btn-send:hover::after { opacity: 1; }
.btn-send:hover { box-shadow: 0 6px 32px rgba(212, 168, 83, 0.3); }
.btn-send:active { transform: scale(0.97); }
.btn-send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

/* ═══════════════════ Modal ═══════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(4, 8, 18, 0.94);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  background: var(--glass);
  backdrop-filter: blur(32px);
  -webkit-backdrop-filter: blur(32px);
  border-radius: var(--radius-xl);
  padding: var(--space-xl) var(--space-lg);
  max-width: 440px;
  width: 100%;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-lg);
  animation: modalEnter 0.45s var(--ease-spring);
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
}
@keyframes modalEnter {
  from { opacity: 0; transform: translateY(48px) scale(0.94); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: rgba(255,255,255,0.04);
  border: none;
  color: var(--text-tertiary);
  font-size: 16px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast);
}
.modal-close:hover { background: rgba(255,255,255,0.1); color: var(--text-primary); }

/* ═══════════════════ Toast ═══════════════════ */
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 400;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}
.toast-item {
  background: rgba(212, 168, 83, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #0a0f24;
  padding: 10px 24px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(212, 168, 83, 0.25);
  animation: toastIn 0.3s var(--ease-spring),
             toastOut 0.25s 2s ease forwards;
  letter-spacing: 0.04em;
}
@keyframes toastIn {
  from { opacity: 0; transform: translateY(-12px) scale(0.9); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes toastOut {
  from { opacity: 1; }
  to { opacity: 0; transform: translateY(-8px); }
}

/* ═══════════════════ Load More ═══════════════════ */
.load-more {
  text-align: center;
  padding: var(--space-lg);
}
.load-more-btn {
  background: none;
  border: 1px solid rgba(212, 168, 83, 0.15);
  border-radius: var(--radius-full);
  color: var(--text-tertiary);
  padding: 10px 28px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  letter-spacing: 0.06em;
  transition: all var(--duration-fast);
}
.load-more-btn:hover {
  border-color: var(--gold);
  color: var(--gold-light);
  background: var(--gold-soft);
}

/* ═══════════════════ Empty State ═══════════════════ */
.empty-state {
  text-align: center;
  padding: 80px var(--space-lg);
}
.empty-state-icon { font-size: 52px; margin-bottom: var(--space-lg); opacity: 0.6; }
.empty-state-text {
  font-family: var(--font-serif);
  font-size: 15px;
  color: var(--text-tertiary);
  line-height: 1.8;
  letter-spacing: 0.04em;
}

/* ═══════════════════ Loading ═══════════════════ */
.loading-state {
  text-align: center;
  padding: 48px;
  color: var(--text-tertiary);
  font-size: 13px;
  letter-spacing: 0.04em;
}
.loading-dots {
  display: inline-flex;
  gap: 6px;
  margin-bottom: 12px;
}
.loading-dots span {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--gold);
  animation: dotBounce 1.2s infinite ease-in-out;
}
.loading-dots span:nth-child(2) { animation-delay: 0.15s; }
.loading-dots span:nth-child(3) { animation-delay: 0.3s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.5); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

/* ═══════════════════ End Marker ═══════════════════ */
.end-marker {
  text-align: center;
  padding: var(--space-lg);
  color: var(--text-muted);
  font-size: 12px;
  opacity: 0.4;
  letter-spacing: 0.06em;
}

/* ═══════════════════ Responsive ═══════════════════ */
@media (max-width: 360px) {
  .nav { padding: 10px 12px; }
  .nav-tab { padding: 6px 10px; font-size: 12px; }
  .nav-tab-label { display: none; }
  .hero-title { font-size: 36px; }
  .post-card { padding: 16px 14px; }
  .post-card-body { font-size: 13.5px; }
}

@media (min-width: 640px) {
  .nav { padding: 14px var(--space-xl); }
  .nav-tab { font-size: 14px; padding: 9px 20px; }
  .post-card { padding: 22px 20px; }
  .post-card-body { font-size: 15px; }
}

@media (min-width: 1024px) {
  .nav { padding: 16px var(--space-2xl); }
  .post-card { padding: 26px 22px; }
  .post-card:hover { transform: translateY(-4px); }
  .post-card-body { font-size: 15px; line-height: 1.9; }
  .write-panel textarea { min-height: 240px; font-size: 16px; }
}

/* 暗色模式下表单自动填充 */
input:-webkit-autofill,
textarea:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 30px var(--space) inset !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}

</style>
</head>
<body>

<!-- ═══ 星空背景 ═══ -->
<div class="stars-bg">
  <canvas id="starCanvas"></canvas>
</div>

<!-- ═══ 全局容器 ═══ -->
<div class="app">

  <!-- ═══ Hero 区 ═══ -->
  <header class="hero" id="hero">
    <div class="hero-constellation" id="heroConstellation"></div>
    <div class="hero-content">
      <h1 class="hero-title">
        <span class="hero-char">唯</span><span class="hero-char">一</span>
      </h1>
      <p class="hero-subtitle">每一粒星尘，都是一个宇宙</p>
      <div class="hero-daily" id="heroDaily">...</div>
    </div>
    <div class="hero-scroll" onclick="document.getElementById('mainContent').scrollIntoView({behavior:'smooth'})">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M7 10l5 5 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    </div>
  </header>

  <!-- ═══ 主导航 ═══ -->
  <nav class="nav" id="mainNav">
    <div class="nav-brand" onclick="window.scrollTo({top:0,behavior:'smooth'})">唯一</div>
    <div class="nav-tabs">
      <button class="nav-tab active" data-tab="stardust">
        <span class="nav-tab-icon">🌌</span>
        <span class="nav-tab-label">星尘</span>
      </button>
      <button class="nav-tab" data-tab="curated">
        <span class="nav-tab-icon">📖</span>
        <span class="nav-tab-label">策展</span>
      </button>
      <button class="nav-tab" data-tab="write">
        <span class="nav-tab-icon">✨</span>
        <span class="nav-tab-label">书写</span>
      </button>
      <button class="nav-tab" data-tab="mine">
        <span class="nav-tab-icon">📜</span>
        <span class="nav-tab-label">我的</span>
      </button>
    </div>
    <button class="nav-bottle" id="navBottle" title="漂流瓶">🏺</button>
  </nav>

  <!-- ═══ 主内容区 ═══ -->
  <main class="main" id="mainContent">

    <!-- ═══ 星尘广场 Tab ═══ -->
    <section class="tab-content active" id="tab-stardust">
      <!-- 分类标签 -->
      <div class="category-bar" id="categoryBar">
        <button class="category-chip active" data-cat="all">全部</button>
        <button class="category-chip" data-cat="诗歌">诗歌</button>
        <button class="category-chip" data-cat="语录">语录</button>
        <button class="category-chip" data-cat="随笔">随笔</button>
        <button class="category-chip" data-cat="音乐">音乐</button>
      </div>
      <!-- 瀑布流 -->
      <div class="masonry" id="masonryGrid"></div>
      <div class="load-more" id="loadMore"></div>
    </section>

    <!-- ═══ 策展 Tab ═══ -->
    <section class="tab-content" id="tab-curated">
      <div class="curated-intro">
        <h2 class="curated-title">星尘策展</h2>
        <p class="curated-desc">由编辑精心挑选的文艺内容，诗歌、语录、随笔、音乐……让好文字遇见你。</p>
      </div>
      <div id="curatedContent"></div>
    </section>

    <!-- ═══ 书写 Tab ═══ -->
    <section class="tab-content" id="tab-write">
      <div class="write-panel">
        <div class="write-header">
          <h2>化作星尘</h2>
          <p>把你的心事写下来。不完美也没关系。</p>
        </div>
        <textarea id="writeContent" placeholder="写下你的心事、一首诗、一句话……每一粒星尘都值得被看见" maxlength="1000"></textarea>
        <div class="write-char-count"><span id="charCount">0</span>/1000</div>
        <div class="write-image-row">
          <input type="file" id="imageInput" accept="image/*" hidden>
          <button class="btn-ghost" id="imageBtn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
            添加图片
          </button>
          <span class="write-image-name" id="imageName"></span>
          <button class="btn-ghost btn-ghost-danger" id="imageClear" style="display:none">✕ 清除</button>
        </div>
        <img id="imagePreview" class="write-image-preview" style="display:none">
        <div class="mood-picker" id="moodPicker"></div>
        <input class="input-nickname" id="writeNickname" placeholder="署名（不填则为「匿名星尘」）" maxlength="20">
        <button class="btn-send" id="sendBtn">
          <span>✨ 化作星尘</span>
        </button>
      </div>
    </section>

    <!-- ═══ 我的 Tab ═══ -->
    <section class="tab-content" id="tab-mine">
      <div id="myPostsContainer"></div>
    </section>

  </main>

</div>

<!-- ═══ 漂流瓶弹窗 ═══ -->
<div class="modal-overlay" id="bottleModal" style="display:none">
  <div class="modal-card" id="bottleContent"></div>
</div>

<!-- ═══ Toast ═══ -->
<div class="toast-container" id="toastContainer"></div>

<script>
/**
 * 「唯一」— 前端应用逻辑
 * 星空画布 · 瀑布流 · 策展交互 · 漂流瓶
 */

// ═══ Constants ═══
const API = '';
const MOODS = {
  '开心': { emoji: '😊', color: '#e8c76a' },
  '难过': { emoji: '😢', color: '#7b9ec7' },
  '愤怒': { emoji: '😡', color: '#c47a6e' },
  '焦虑': { emoji: '😰', color: '#9b8ec4' },
  '迷茫': { emoji: '🤔', color: '#8ba5a5' },
  '感恩': { emoji: '🙏', color: '#e0b088' },
  '其他': { emoji: '✨', color: '#c8963e' },
};

// ═══ State ═══
const state = {
  fp: getFingerprint(),
  currentTab: 'stardust',
  currentCategory: 'all',
  stardustPage: 1,
  hasMoreStardust: true,
  isLoading: false,
  cardCounter: 0,
  selectedMood: '其他',
  uploadImageData: '',
};

// ═══ Fingerprint ═══
function getFingerprint() {
  let fp = localStorage.getItem('weiyi_fp');
  if (!fp) {
    fp = 'fp_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
    localStorage.setItem('weiyi_fp', fp);
  }
  return fp;
}

// ═══ Init ═══
document.addEventListener('DOMContentLoaded', () => {
  initStarCanvas();
  initHeroConstellation();
  initNav();
  initTabs();
  initCategoryBar();
  initDailyMessage();
  initMoodPicker();
  initImageUpload();
  initWriteForm();
  initBottle();
  initScrollEffects();
  loadStardustPosts(true);
});

// ═══════════════════ Star Canvas ═══════════════════
function initStarCanvas() {
  const canvas = document.getElementById('starCanvas');
  const ctx = canvas.getContext('2d');
  let stars = [];
  let animFrame;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function createStars() {
    const count = Math.floor((canvas.width * canvas.height) / 3500);
    stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.4 + 0.3,
        twinkleSpeed: Math.random() * 0.008 + 0.003,
        twinkleOffset: Math.random() * Math.PI * 2,
        hue: Math.random() < 0.15 ? 42 + Math.random() * 15 : 0, // 15% 金色星
        alpha: Math.random() * 0.5 + 0.3,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const t = Date.now() * 0.001;

    for (const s of stars) {
      const alpha = s.alpha + Math.sin(t * s.twinkleSpeed * 60 + s.twinkleOffset) * 0.25;
      const clampedAlpha = Math.max(0.1, Math.min(0.85, alpha));

      if (s.hue > 0) {
        ctx.fillStyle = `hsla(${s.hue}, 60%, 75%, ${clampedAlpha})`;
      } else {
        ctx.fillStyle = `rgba(220,220,235,${clampedAlpha})`;
      }

      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();

      // 偶尔加辉光
      if (clampedAlpha > 0.6) {
        ctx.fillStyle = s.hue > 0
          ? `hsla(${s.hue}, 60%, 75%, ${clampedAlpha * 0.15})`
          : `rgba(220,220,235,${clampedAlpha * 0.12})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    animFrame = requestAnimationFrame(draw);
  }

  resize();
  createStars();
  draw();
  window.addEventListener('resize', () => { resize(); createStars(); });
}

// ═══════════════════ Hero Constellation ═══════════════════
function initHeroConstellation() {
  const container = document.getElementById('heroConstellation');
  const canvas = document.createElement('canvas');
  container.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  let points = [];
  const CONNECT_DIST = 120;

  function resize() {
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
  }

  function createPoints() {
    const count = 25;
    points = [];
    for (let i = 0; i < count; i++) {
      points.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.5 + 0.2,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 连线
    for (let i = 0; i < points.length; i++) {
      for (let j = i + 1; j < points.length; j++) {
        const dx = points[i].x - points[j].x;
        const dy = points[i].y - points[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CONNECT_DIST) {
          const alpha = (1 - dist / CONNECT_DIST) * 0.12;
          ctx.strokeStyle = `rgba(212,168,83,${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(points[i].x, points[i].y);
          ctx.lineTo(points[j].x, points[j].y);
          ctx.stroke();
        }
      }
    }

    // 点
    for (const p of points) {
      ctx.fillStyle = `rgba(232,199,106,${p.alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();

      // 移动
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    }

    requestAnimationFrame(draw);
  }

  resize();
  createPoints();
  draw();
  window.addEventListener('resize', () => { resize(); createPoints(); });
}

// ═══════════════════ Navigation ═══════════════════
function initNav() {
  const nav = document.getElementById('mainNav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
}

function initTabs() {
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.dataset.tab;
      switchTab(tabName);
    });
  });
}

function switchTab(name) {
  state.currentTab = name;
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.tab-content').forEach(tc => tc.classList.toggle('active', tc.id === `tab-${name}`));

  // 重新触发动画
  const activeTC = document.getElementById(`tab-${name}`);
  if (activeTC) {
    activeTC.style.animation = 'none';
    activeTC.offsetHeight;
    activeTC.style.animation = '';
  }

  if (name === 'stardust' && document.getElementById('masonryGrid').children.length === 0) {
    loadStardustPosts(true);
  }
  if (name === 'curated') loadCuratedContent();
  if (name === 'mine') loadMyPosts();
}

// ═══════════════════ Category Filter ═══════════════════
function initCategoryBar() {
  document.querySelectorAll('.category-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      state.currentCategory = chip.dataset.cat;
      document.querySelectorAll('.category-chip').forEach(c => c.classList.toggle('active', c === chip));
      loadStardustPosts(true);
    });
  });
}

// ═══════════════════ Daily Message ═══════════════════
async function initDailyMessage() {
  try {
    const r = await fetch(API + '/api/daily-message');
    const d = await r.json();
    const el = document.getElementById('heroDaily');
    const parts = [];
    parts.push('「' + d.message + '」');
    if (d.author) parts.push('—— ' + d.author);
    if (d.source) parts.push('《' + d.source + '》');
    el.textContent = parts.join('\n');
  } catch (e) {
    document.getElementById('heroDaily').textContent = '「享受今晚。」';
  }
}

// ═══════════════════ Stardust Posts ═══════════════════
async function loadStardustPosts(reset = false) {
  if (state.isLoading) return;
  if (reset) {
    state.stardustPage = 1;
    state.hasMoreStardust = true;
    state.cardCounter = 0;
    document.getElementById('masonryGrid').innerHTML = '';
    document.getElementById('loadMore').innerHTML = '';
  }
  if (!state.hasMoreStardust) return;

  state.isLoading = true;
  const grid = document.getElementById('masonryGrid');

  try {
    const r = await fetch(API + '/api/posts?page=' + state.stardustPage + '&fingerprint=' + encodeURIComponent(state.fp));
    const d = await r.json();

    let posts = d.posts;
    // 分类过滤（前端）
    if (state.currentCategory !== 'all') {
      posts = posts.filter(p => p.category === state.currentCategory || p.mood === state.currentCategory);
    }

    if (posts.length === 0 && reset) {
      grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🌌</div><p class="empty-state-text">这个分类还没有星尘<br>去写点什么吧</p></div>';
    } else {
      posts.forEach((p, i) => {
        const card = createPostCard(p);
        card.style.animationDelay = (state.cardCounter * 0.05) + 's';
        state.cardCounter++;
        grid.appendChild(card);
      });
    }

    state.hasMoreStardust = d.has_more;
    state.stardustPage++;

    const loadMore = document.getElementById('loadMore');
    if (state.hasMoreStardust) {
      loadMore.innerHTML = '<div class="load-more"><button class="load-more-btn" id="loadMoreBtn">✨ 更多星尘</button></div>';
      document.getElementById('loadMoreBtn')?.addEventListener('click', () => loadStardustPosts());
    } else {
      loadMore.innerHTML = Array.from(grid.children).length > 0
        ? '<div class="end-marker">— 已经到底啦 —</div>'
        : '';
    }
  } catch (e) {
    if (reset) grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🛰️</div><p class="empty-state-text">连接星尘失败<br>请检查网络</p></div>';
  }

  state.isLoading = false;
}

function createPostCard(p) {
  const card = document.createElement('div');
  card.className = 'post-card' + (p.is_curated ? ' curated' : '');

  // 左侧色条
  card.style.setProperty('--mood-color', p.mood_color);

  // Badge 类名映射
  const badgeClassMap = { '诗歌': 'poetry', '语录': 'quote', '随笔': 'essay', '音乐': 'music', '光影': 'film' };
  const badgeClass = badgeClassMap[p.category] || '';

  card.innerHTML = `
    <div class="post-card-header">
      <div class="post-card-meta">
        <span class="post-card-mood">${p.mood_emoji}</span>
        <span class="post-card-author">${escHtml(p.nickname)}</span>
        ${p.is_curated && p.category ? `<span class="post-card-badge ${badgeClass}">${p.category}</span>` : ''}
      </div>
      <span class="post-card-time">${timeAgo(p.created_at)}</span>
    </div>
    <div class="post-card-body">${escHtml(p.content)}</div>
    ${p.image ? `<div class="post-card-image"><img src="${p.image}" alt="星尘图片" loading="lazy"></div>` : ''}
    ${p.source ? `<div class="post-card-source">—— ${escHtml(p.source)}</div>` : ''}
    <div class="post-card-actions">
      <button class="post-action like-btn${p.liked_by_me ? ' liked' : ''}" data-id="${p.id}">
        ❤️ <span class="post-action-count">${p.like_count || 0}</span>
      </button>
      <button class="post-action hug-btn${p.hugged_by_me ? ' hugged' : ''}" data-id="${p.id}">
        🫂 <span class="post-action-count">${p.hug_count || 0}</span>
      </button>
    </div>
  `;

  // Like
  card.querySelector('.like-btn')?.addEventListener('click', async function(e) {
    e.stopPropagation();
    const id = this.dataset.id;
    this.classList.add('just-liked');
    setTimeout(() => this.classList.remove('just-liked'), 400);
    try {
      const r = await fetch(API + '/api/post/' + id + '/like', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fingerprint: state.fp })
      });
      const d = await r.json();
      this.classList.toggle('liked', d.action === 'liked');
      this.querySelector('.post-action-count').textContent = d.like_count;
    } catch (e) {}
  });

  // Hug
  card.querySelector('.hug-btn')?.addEventListener('click', async function(e) {
    e.stopPropagation();
    const id = this.dataset.id;
    try {
      const r = await fetch(API + '/api/post/' + id + '/hug', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fingerprint: state.fp })
      });
      const d = await r.json();
      this.classList.toggle('hugged', d.action === 'hugged');
      this.querySelector('.post-action-count').textContent = d.hug_count;
    } catch (e) {}
  });

  return card;
}

// ═══════════════════ Curated Content ═══════════════════
async function loadCuratedContent() {
  const container = document.getElementById('curatedContent');
  if (container.children.length > 0) return; // 已加载

  container.innerHTML = '<div class="loading-state"><div class="loading-dots"><span></span><span></span><span></span></div><div>正在策展星尘……</div></div>';

  try {
    const r = await fetch(API + '/api/posts/curated?fingerprint=' + encodeURIComponent(state.fp));
    const d = await r.json();
    container.innerHTML = '';

    const categoryIcons = {
      '诗歌': '🌸', '语录': '💡', '随笔': '📝', '音乐': '🎵', '光影': '🎬'
    };

    for (const [category, posts] of Object.entries(d.categories)) {
      if (posts.length === 0) continue;

      const section = document.createElement('div');
      section.className = 'curated-section';
      section.innerHTML = `
        <div class="curated-section-header">
          <span class="curated-section-icon">${categoryIcons[category] || '✨'}</span>
          <h3 class="curated-section-title">${category}</h3>
          <span class="curated-section-count">${posts.length} 篇</span>
        </div>
        <div class="curated-grid"></div>
      `;

      const grid = section.querySelector('.curated-grid');
      posts.forEach(p => {
        const card = createPostCard(p);
        grid.appendChild(card);
      });

      container.appendChild(section);
    }

    if (Object.keys(d.categories).length === 0) {
      container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📖</div><p class="empty-state-text">策展内容正在筹备中</p></div>';
    }
  } catch (e) {
    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🛰️</div><p class="empty-state-text">加载策展内容失败</p></div>';
  }
}

// ═══════════════════ Write Form ═══════════════════
function initMoodPicker() {
  const container = document.getElementById('moodPicker');
  container.innerHTML = Object.entries(MOODS).map(([k, v]) =>
    `<span class="mood-chip${k === state.selectedMood ? ' selected' : ''}" data-mood="${k}">${v.emoji} ${k}</span>`
  ).join('');

  container.querySelectorAll('.mood-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      state.selectedMood = chip.dataset.mood;
      container.querySelectorAll('.mood-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
    });
  });
}

function initImageUpload() {
  const input = document.getElementById('imageInput');
  const btn = document.getElementById('imageBtn');
  const nameEl = document.getElementById('imageName');
  const clearBtn = document.getElementById('imageClear');
  const preview = document.getElementById('imagePreview');

  btn.addEventListener('click', () => input.click());

  input.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) return;
    nameEl.textContent = file.name;
    clearBtn.style.display = 'inline-flex';

    const reader = new FileReader();
    reader.onload = function(e) {
      const img = new Image();
      img.onload = function() {
        const canvas = document.createElement('canvas');
        let w = img.width, h = img.height;
        const maxW = 800;
        if (w > maxW) { h = h * maxW / w; w = maxW; }
        canvas.width = w; canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        state.uploadImageData = canvas.toDataURL('image/jpeg', 0.65);
        preview.src = state.uploadImageData;
        preview.style.display = 'block';
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });

  clearBtn.addEventListener('click', () => {
    state.uploadImageData = '';
    input.value = '';
    nameEl.textContent = '';
    clearBtn.style.display = 'none';
    preview.style.display = 'none';
  });
}

function initWriteForm() {
  const textarea = document.getElementById('writeContent');
  const charCount = document.getElementById('charCount');

  textarea.addEventListener('input', () => {
    charCount.textContent = textarea.value.length;
    charCount.style.color = textarea.value.length > 900 ? 'var(--rose)' : 'var(--text-muted)';
  });

  document.getElementById('sendBtn').addEventListener('click', async () => {
    const content = textarea.value.trim();
    if (!content) { toast('写点什么吧 ✨'); return; }

    const btn = document.getElementById('sendBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>正在化作星尘……</span>';

    try {
      const r = await fetch(API + '/api/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          image: state.uploadImageData,
          mood: state.selectedMood,
          nickname: document.getElementById('writeNickname').value.trim(),
          fingerprint: state.fp,
        })
      });
      const d = await r.json();
      if (d.success) {
        textarea.value = '';
        document.getElementById('writeNickname').value = '';
        state.uploadImageData = '';
        document.getElementById('imageInput').value = '';
        document.getElementById('imageName').textContent = '';
        document.getElementById('imageClear').style.display = 'none';
        document.getElementById('imagePreview').style.display = 'none';
        charCount.textContent = '0';
        charCount.style.color = 'var(--text-muted)';
        toast('✨ 已化作星尘');
        // 切回星尘页面
        switchTab('stardust');
        state.currentCategory = 'all';
        document.querySelectorAll('.category-chip').forEach(c => c.classList.toggle('active', c.dataset.cat === 'all'));
        loadStardustPosts(true);
      } else {
        toast(d.error || '发送失败');
      }
    } catch (e) {
      toast('发送失败，请重试');
    }

    btn.disabled = false;
    btn.innerHTML = '<span>✨ 化作星尘</span>';
  });
}

// ═══════════════════ Drift Bottle ═══════════════════
function initBottle() {
  document.getElementById('navBottle').addEventListener('click', openBottle);
  document.getElementById('bottleModal').addEventListener('click', function(e) {
    if (e.target === this) closeBottle();
  });
}

async function openBottle() {
  const modal = document.getElementById('bottleModal');
  const content = document.getElementById('bottleContent');

  modal.style.display = 'flex';
  content.innerHTML = `
    <div style="text-align:center;padding:48px 0">
      <div style="font-size:52px;animation:bottleFloat 1.5s ease-in-out infinite alternate">🏺</div>
      <div style="margin-top:18px;color:var(--text-tertiary);font-size:14px">正在海面上搜寻漂流瓶……</div>
    </div>
  `;

  try {
    const r = await fetch(API + '/api/posts/random?fingerprint=' + encodeURIComponent(state.fp));
    if (r.status === 404) {
      content.innerHTML = `
        <button class="modal-close" onclick="closeBottle()">✕</button>
        <div style="text-align:center;padding:48px 0">
          <div style="font-size:40px;margin-bottom:16px">🏺</div>
          <div style="color:var(--text-tertiary);font-size:14px">${(await r.json()).error}</div>
          <button class="load-more-btn" style="margin-top:20px" onclick="openBottle()">🫧 再捞一个</button>
        </div>
      `;
      return;
    }
    const p = await r.json();

    content.innerHTML = `
      <button class="modal-close" onclick="closeBottle()">✕</button>
      <div style="text-align:center;margin-bottom:16px">
        <div style="font-size:36px">🏺</div>
        <div style="font-size:13px;color:var(--text-tertiary);margin-top:4px">你捡到了一个漂流瓶</div>
      </div>
      <div class="post-card" style="margin:0;box-shadow:none;background:rgba(255,255,255,0.02)">
        <div class="post-card-header">
          <div class="post-card-meta">
            <span class="post-card-mood">${p.mood_emoji}</span>
            <span class="post-card-author">${escHtml(p.nickname)}</span>
          </div>
          <span class="post-card-time">${timeAgo(p.created_at)}</span>
        </div>
        <div class="post-card-body">${escHtml(p.content)}</div>
        ${p.image ? `<div class="post-card-image"><img src="${p.image}" alt="漂流瓶图片" loading="lazy"></div>` : ''}
        <div style="text-align:center;margin-top:16px;color:var(--text-tertiary);font-size:13px">
          ❤️ ${p.like_count || 0} · 🫂 ${p.hug_count || 0}
        </div>
      </div>
      <div style="text-align:center;margin-top:20px">
        <button class="load-more-btn" onclick="openBottle()">🫧 再捞一个</button>
      </div>
    `;
  } catch (e) {
    content.innerHTML = `
      <button class="modal-close" onclick="closeBottle()">✕</button>
      <div style="text-align:center;padding:48px;color:var(--text-tertiary)">漂流瓶漂远了……再试一次吧</div>
    `;
  }
}

function closeBottle() {
  document.getElementById('bottleModal').style.display = 'none';
}

// ═══════════════════ My Posts ═══════════════════
async function loadMyPosts() {
  const container = document.getElementById('myPostsContainer');
  container.innerHTML = '<div class="loading-state"><div class="loading-dots"><span></span><span></span><span></span></div><div>寻找你的星尘……</div></div>';

  try {
    const r = await fetch(API + '/api/my-posts?fingerprint=' + encodeURIComponent(state.fp));
    const d = await r.json();
    container.innerHTML = '';

    if (d.posts.length === 0) {
      container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📜</div><p class="empty-state-text">你还没有写过星尘<br>每一段心事都值得被留下</p></div>';
    } else {
      d.posts.forEach(p => {
        const card = createPostCard(p);
        // 添加删除按钮
        const actions = card.querySelector('.post-card-actions');
        const delBtn = document.createElement('button');
        delBtn.className = 'post-action';
        delBtn.style.cssText = 'margin-left:auto;opacity:0.4;font-size:12px';
        delBtn.innerHTML = '🗑️ <span>删除</span>';
        delBtn.addEventListener('click', async (e) => {
          e.stopPropagation();
          if (!confirm('确定要删除这条星尘吗？')) return;
          try {
            const r = await fetch(API + '/api/post/' + p.id, {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ fingerprint: state.fp })
            });
            const d = await r.json();
            if (d.success) {
              card.style.transition = 'all 0.3s ease';
              card.style.opacity = '0';
              card.style.transform = 'scale(0.95)';
              setTimeout(() => { card.remove(); if (container.children.length === 0) loadMyPosts(); }, 300);
            } else {
              toast(d.error || '删除失败');
            }
          } catch (e) { toast('删除失败'); }
        });
        actions.appendChild(delBtn);
        container.appendChild(card);
      });
    }
  } catch (e) {
    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🛰️</div><p class="empty-state-text">连接失败</p></div>';
  }
}

// ═══════════════════ Infinite Scroll ═══════════════════
function initScrollEffects() {
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      if (state.currentTab === 'stardust' && !state.isLoading && state.hasMoreStardust) {
        const main = document.getElementById('mainContent');
        if (main) {
          const rect = main.getBoundingClientRect();
          if (rect.bottom - window.innerHeight < 400) {
            loadStardustPosts();
          }
        }
      }
      ticking = false;
    });
  }, { passive: true });
}

// ═══════════════════ Utilities ═══════════════════
function timeAgo(iso) {
  const then = new Date(iso + (iso.endsWith('Z') ? '' : 'Z'));
  const now = new Date();
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return '刚刚';
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前';
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前';
  if (diff < 604800) return Math.floor(diff / 86400) + '天前';
  return then.toLocaleDateString('zh-CN');
}

function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function toast(msg) {
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = 'toast-item';
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 2300);
}

// ═══ Bottle float animation ═══
const bottleFloatStyle = document.createElement('style');
bottleFloatStyle.textContent = `
  @keyframes bottleFloat {
    from { transform: translateY(0px) rotate(-3deg); }
    to { transform: translateY(-10px) rotate(3deg); }
  }
`;
document.head.appendChild(bottleFloatStyle);

</script>
</body>
</html>
'''

@app.route('/')
def index():
    return _HTML

# ═══════ 启动 ═══════
if __name__=='__main__':
    port=int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port,debug=True)
