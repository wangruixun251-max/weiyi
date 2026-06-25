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


# ═══════ HTML 模板（从文件加载） ═══════
_HTML_CACHE = None
def _load_html():
    global _HTML_CACHE
    if _HTML_CACHE is None:
        import codecs
        with codecs.open(os.path.join(BASE_DIR, 'templates', 'index.html'), 'r', 'utf-8') as f:
            _HTML_CACHE = f.read()
    return _HTML_CACHE

@app.route('/')
def index():
    return _load_html()

# ═══════ 启动 ═══════
if __name__=='__main__':
    port=int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port,debug=True)
