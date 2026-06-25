"""
唯一 — 高质量文艺社区 v3.1
Flask 单文件部署：HTML/CSS/JS 全部内联
"""
import os
import sqlite3
import datetime
import asyncio
import hashlib
import io
import time
from flask import Flask, g, request, jsonify, render_template, Response

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
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL, image TEXT DEFAULT '',
            mood TEXT DEFAULT '其他', source TEXT DEFAULT '',
            nickname TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now')),
            reviewed INTEGER DEFAULT 0
        );
    """)
    db.commit(); db.close()

def seed():
    db = sqlite3.connect(DATABASE)
    curated = [
    ("我想和你一起生活\n在某个小镇，\n共享无尽的黄昏\n和绵绵不绝的钟声。\n—— 茨维塔耶娃《我想和你一起生活》","其他","✨","#c8963e","诗歌星尘","诗歌","茨维塔耶娃","https://picsum.photos/id/10/800/500"),
    ("我给你瘦落的街道、绝望的落日、荒郊的月亮。\n我给你一个久久地望着孤月的人的悲哀。\n—— 博尔赫斯《我用什么才能留住你》","难过","😢","#7b9ec7","诗歌星尘","诗歌","博尔赫斯","https://picsum.photos/id/11/800/500"),
    ("从前的日色变得慢\n车，马，邮件都慢\n一生只够爱一个人\n—— 木心《从前慢》","感恩","🙏","#e0b088","诗歌星尘","诗歌","木心","https://picsum.photos/id/12/800/500"),
    ("你一会看我\n一会看云\n我觉得\n你看我时很远\n你看云时很近\n—— 顾城《远和近》","迷茫","🤔","#8ba5a5","诗歌星尘","诗歌","顾城","https://picsum.photos/id/13/800/500"),
    ("如果有来生，要做一棵树，\n站成永恒，没有悲欢的姿势。\n一半在尘土里安详，一半在风里飞扬，\n一半洒落阴凉，一半沐浴阳光。\n—— 三毛","其他","✨","#c8963e","诗歌星尘","诗歌","三毛","https://picsum.photos/id/14/800/500"),
    ("多少人爱你青春欢畅的时辰，\n爱慕你的美丽，假意或真心。\n只有一个人爱你那朝圣者的灵魂，\n爱你衰老了的脸上痛苦的皱纹。\n—— 叶芝《当你老了》","感恩","🙏","#e0b088","诗歌星尘","诗歌","叶芝","https://picsum.photos/id/15/800/500"),
    ("你不必站在风里，\n不必站在雨里，\n你可以走进我的诗里。","其他","✨","#c8963e","诗歌星尘","诗歌","佚名","https://picsum.photos/id/16/800/500"),
    ("草在结它的种子，风在摇它的叶子。\n我们站着，不说话，就十分美好。\n—— 顾城《门前》","开心","😊","#e8c76a","诗歌星尘","诗歌","顾城","https://picsum.photos/id/17/800/500"),
    ("愿你有好运气，如果没有，愿你在不幸中学会慈悲。\n愿你被很多人爱，如果没有，愿你在寂寞中学会宽容。\n—— 刘瑜","感恩","🙏","#e0b088","诗歌星尘","诗歌","刘瑜","https://picsum.photos/id/18/800/500"),
    ("我无法搬动岁月，你披着一身的月光，停泊在秋天里。\n—— 叶芝","其他","✨","#c8963e","诗歌星尘","诗歌","叶芝","https://picsum.photos/id/19/800/500"),
    ("一个人需要隐藏多少秘密\n才能巧妙地度过一生\n—— 仓央嘉措","迷茫","🤔","#8ba5a5","诗歌星尘","诗歌","仓央嘉措","https://picsum.photos/id/20/800/500"),
    ("每想你一次，天上飘落一粒沙，从此形成了撒哈拉。\n—— 三毛","其他","✨","#c8963e","诗歌星尘","诗歌","三毛","https://picsum.photos/id/21/800/500"),
    ("在石榴花丛中，那里有光，有酒，有石榴花。\n你不来的话，这一切都了无意义。\n—— 鲁米","其他","✨","#c8963e","诗歌星尘","诗歌","鲁米","https://picsum.photos/id/22/800/500"),
    ("我们读诗写诗，并不是因为它们好玩，而是因为我们是人类的一分子。\n医药、法律、商业、工程，这些都是高贵的理想。\n但是诗、美、浪漫、爱，这些才是我们生存的原因。\n—— 《死亡诗社》","其他","✨","#c8963e","光影星尘","语录","《死亡诗社》","https://picsum.photos/id/23/800/500"),
    ("世界上只有一种真正的英雄主义，那就是在认清生活真相之后依然热爱生活。\n—— 罗曼·罗兰","感恩","🙏","#e0b088","哲思星尘","语录","罗曼·罗兰","https://picsum.photos/id/24/800/500"),
    ("我步入丛林，因为我希望生活得有意义。\n我希望活得深刻，吸取生命中所有的精华。\n把非生命的一切都击溃，以免当我生命终结时，发现自己从没有活过。\n—— 梭罗《瓦尔登湖》","迷茫","🤔","#8ba5a5","哲思星尘","语录","梭罗","https://picsum.photos/id/25/800/500"),
    ("活着本身就很美妙，如果连这道理都不懂，怎么去探索更深的东西？\n—— 《三体》","其他","✨","#c8963e","光影星尘","语录","刘慈欣","https://picsum.photos/id/26/800/500"),
    ("每个人心里都有一团火，路过的人只看到烟。\n但是总有一个人，总有那么一个人能看到这团火，然后走过来，陪我一起。\n—— 梵高","难过","😢","#7b9ec7","艺文星尘","语录","梵高书信","https://picsum.photos/id/27/800/500"),
    ("你要搞清楚自己人生的剧本——不是你父母的续集，不是你子女的前传，更不是你朋友的外篇。\n—— 尼采","愤怒","😡","#c47a6e","哲思星尘","语录","尼采","https://picsum.photos/id/28/800/500"),
    ("我曾见过你们人类无法置信的事情：\n战舰在猎户座的边缘起火燃烧；\nC射线在星门附近的黑暗中闪耀……\n所有这些瞬间终将在时光中湮没，一如雨中的泪水。\n—— 《银翼杀手》","迷茫","🤔","#8ba5a5","光影星尘","语录","《银翼杀手》","https://picsum.photos/id/29/800/500"),
    ("我们终此一生，就是要摆脱他人的期待，找到真正的自己。\n—— 《无声告白》","焦虑","😰","#9b8ec4","文学星尘","语录","伍绮诗","https://picsum.photos/id/30/800/500"),
    ("为你，千千万万遍。\n—— 《追风筝的人》","感恩","🙏","#e0b088","文学星尘","语录","卡勒德·胡赛尼","https://picsum.photos/id/31/800/500"),
    ("胆小鬼连幸福都会害怕，碰到棉花都会受伤。\n—— 《人间失格》","难过","😢","#7b9ec7","文学星尘","语录","太宰治","https://picsum.photos/id/32/800/500"),
    ("你才25岁，你可以成为任何你想成为的人。\n—— 是枝裕和《步履不停》","迷茫","🤔","#8ba5a5","光影星尘","语录","是枝裕和","https://picsum.photos/id/33/800/500"),
    ("去爱，去失去，要不负相遇。\n—— 《想见你》","难过","😢","#7b9ec7","光影星尘","语录","《想见你》","https://picsum.photos/id/34/800/500"),
    ("人永远不知道，谁哪次不经意的跟你说了再见之后，就真的不会再见了。\n—— 《千与千寻》","难过","😢","#7b9ec7","光影星尘","语录","宫崎骏","https://picsum.photos/id/35/800/500"),
    ("凌晨四点钟，我看见海棠花未眠。\n总觉得这时，你应该在我身边。\n—— 川端康成","难过","😢","#7b9ec7","文学星尘","随笔","川端康成","https://picsum.photos/id/36/800/500"),
    ("我所有的自负都来自我的自卑，所有的英雄气概都来自于我内心的软弱。\n我假装无情，其实是痛恨自己的深情。\n—— 马良《坦白书》","焦虑","😰","#9b8ec4","文学星尘","随笔","马良","https://picsum.photos/id/37/800/500"),
    ("你对我的百般注解和识读，并不构成万分之一的我，却是一览无遗的你自己。\n—— 三毛","愤怒","😡","#c47a6e","文学星尘","随笔","三毛","https://picsum.photos/id/38/800/500"),
    ("一个人有两个我，一个在黑暗中醒着，一个在光明中睡着。\n—— 纪伯伦","迷茫","🤔","#8ba5a5","哲思星尘","随笔","纪伯伦","https://picsum.photos/id/39/800/500"),
    ("我其实并不孤僻，甚至可以说开朗活泼。但大多时候我很懒，懒得经营一个关系。\n—— 刘瑜","其他","✨","#c8963e","文学星尘","随笔","刘瑜","https://picsum.photos/id/40/800/500"),
    ("任何瞬间的心动都不容易，不要怠慢了它。\n—— 毛姆","开心","😊","#e8c76a","文学星尘","随笔","毛姆","https://picsum.photos/id/41/800/500"),
    ("有些人不属于你，但遇见了也挺好。","难过","😢","#7b9ec7","文学星尘","随笔","佚名","https://picsum.photos/id/42/800/500"),
    ("我年轻过，落魄过，幸福过，我对生活一往情深。\n—— 马尔克斯","感恩","🙏","#e0b088","文学星尘","随笔","马尔克斯","https://picsum.photos/id/43/800/500"),
    ("你说你喜欢雨，但是你在下雨的时候打伞。\n你说你喜欢太阳，但是你在阳光明媚的时候躲在阴凉的地方。\n—— 莎士比亚","其他","✨","#c8963e","文学星尘","随笔","莎士比亚","https://picsum.photos/id/44/800/500"),
    ("我一生中最幸运的两件事：一件是时间终于将我对你的爱消耗殆尽；一件是很久很久以前有一天，我遇见你。\n—— 顾漫","难过","😢","#7b9ec7","文学星尘","随笔","顾漫","https://picsum.photos/id/45/800/500"),
    ("活着就是，一个个无可替代的日子的累积。\n—— 坂元裕二","其他","✨","#c8963e","文学星尘","随笔","坂元裕二","https://picsum.photos/id/46/800/500"),
    ("音乐是灵魂的避难所。\n当你无法用语言表达时，音乐替你说话。\n—— 贝多芬","其他","✨","#c8963e","音符星尘","音乐","贝多芬","https://picsum.photos/id/47/800/500"),
    ("人们必须用内心的耳朵去听，那才是真正听见。\n—— 德彪西","其他","✨","#c8963e","音符星尘","音乐","德彪西","https://picsum.photos/id/48/800/500"),
    ("没有音乐，生命将是一个错误。\n—— 尼采","其他","✨","#c8963e","音符星尘","音乐","尼采","https://picsum.photos/id/49/800/500"),
    ("有些歌，前奏一响你就知道，它一定会进入你的年度歌单。","开心","😊","#e8c76a","音符星尘","音乐","佚名","https://picsum.photos/id/50/800/500"),
    ("在那些失眠的夜晚，巴赫的G弦之歌比任何安眠药都管用。\n—— 村上春树","焦虑","😰","#9b8ec4","音符星尘","音乐","村上春树","https://picsum.photos/id/51/800/500"),
    ("歌单是一座孤岛。那些不敢说出口的话，都藏在了你反复循环的歌里。","难过","😢","#7b9ec7","音符星尘","音乐","佚名","https://picsum.photos/id/52/800/500"),
    ("爵士乐是从不兑现的诺言。\n—— 米兰·昆德拉","其他","✨","#c8963e","音符星尘","音乐","米兰·昆德拉","https://picsum.photos/id/53/800/500"),
    ("人生不能像做菜，把所有的料都准备好了才下锅。\n—— 《饮食男女》","其他","✨","#c8963e","光影星尘","光影","李安","https://picsum.photos/id/54/800/500"),
    ("我不知道将去何方，但我已在路上。\n—— 《千与千寻》","迷茫","🤔","#8ba5a5","光影星尘","光影","宫崎骏","https://picsum.photos/id/55/800/500"),
    ("说好了是一辈子，差一年，差一个月，差一个时辰，都不是一辈子。\n—— 《霸王别姬》","难过","😢","#7b9ec7","光影星尘","光影","《霸王别姬》","https://picsum.photos/id/56/800/500"),
    ("我们一路奋战，不是为了改变世界，而是为了不让世界改变我们。\n—— 《熔炉》","愤怒","😡","#c47a6e","光影星尘","光影","《熔炉》","https://picsum.photos/id/57/800/500"),
    ("幸福不是故事，不幸才是。\n—— 《后来的我们》","难过","😢","#7b9ec7","光影星尘","光影","《后来的我们》","https://picsum.photos/id/58/800/500"),
    ("做人如果没有梦想，那和咸鱼有什么区别？\n—— 《少林足球》","开心","😊","#e8c76a","光影星尘","光影","周星驰","https://picsum.photos/id/59/800/500"),
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
        ("爱是唯一可以超越时间与空间的事物。","","《星际穿越》"),
        ("没有一个冬天不可逾越，没有一个春天不会来临。","",""),
        ("世界以痛吻我，要我报之以歌。","泰戈尔",""),
        ("人的一切痛苦，本质上都是对自己无能的愤怒。","王小波",""),
        ("人生若无悔，那该多无趣啊。","","《一代宗师》"),
        ("念念不忘，必有回响。","",""),
        ("愿你走出半生，归来仍是少年。","",""),
    ]
    fp="curated_000"
    db.execute("DELETE FROM posts WHERE is_curated=1 AND fingerprint=?", (fp,))
    for c,m,me,mc,nick,cat,src,img in curated:
        db.execute("INSERT OR IGNORE INTO posts(content,image,mood,mood_emoji,mood_color,nickname,fingerprint,is_curated,category,source,created_at) VALUES(?,?,?,?,?,?,?,1,?,?,datetime('now','-'||abs(random()%72)||' hours'))",(c,img,m,me,mc,nick,fp,cat,src))
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


# ═══════ Edge TTS 听书 ═══════
# 运行时缓存：生成一次，重放无需再生（/tmp 在 Render 容器生命周期内持久）
import json as _json
_tts_cache_dir = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'weiyi_tts')
os.makedirs(_tts_cache_dir, exist_ok=True)
_tts_lock = {}  # 简单的进程内锁，避免重复生成


@app.route('/api/tts/<int:book_id>', methods=['POST'])
def api_tts(book_id):
    """接收前端文本，用 Edge TTS 合成 MP3，首次缓存后即时响应。
    
    前端 POST {'text': '...'}
    返回 audio/mpeg 流。首次请求可能需数秒合成，之后直接从缓存响应。
    """
    data = request.get_json(force=True) or {}
    text = (data.get('text') or '').strip()
    if not text or len(text) < 50:
        return jsonify({'error': 'text too short'}), 400

    cache_key = hashlib.md5(text.encode()).hexdigest()[:16]
    cache_path = os.path.join(_tts_cache_dir, f'tts_{book_id}_{cache_key}.mp3')

    # 已有缓存 → 直接返回
    if os.path.exists(cache_path):
        def stream_cached():
            with open(cache_path, 'rb') as f:
                while chunk := f.read(65536):
                    yield chunk
        return Response(stream_cached(), mimetype='audio/mpeg',
                        headers={'Cache-Control': 'public, max-age=86400'})

    # Edge TTS 合成 — 女声「晓晓」，极自然，微软神经网络语音
    async def _generate():
        import edge_tts
        communicate = edge_tts.Communicate(
            text,
            'zh-CN-XiaoxiaoNeural',
            rate='-5%',
            pitch='-2Hz'
        )
        with open(cache_path + '.tmp', 'wb') as f:
            async for chunk in communicate.stream():
                if chunk['type'] == 'audio':
                    f.write(chunk['data'])
        os.rename(cache_path + '.tmp', cache_path)
        return cache_path

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_generate())
    finally:
        loop.close()

    def stream():
        with open(cache_path, 'rb') as f:
            while chunk := f.read(65536):
                yield chunk

    return Response(stream(), mimetype='audio/mpeg',
                    headers={'Cache-Control': 'public, max-age=86400'})


# ═══════ 审核系统 ═══════
REVIEW_PASSWORD = "weiyi2024"


@app.route('/review')
def review_page():
    return render_template('review.html')


@app.route('/api/review/auth', methods=['POST'])
def review_auth():
    pw = (request.get_json(force=True).get('password') or '').strip()
    if pw == REVIEW_PASSWORD:
        return jsonify({'ok': True, 'token': 'weiyi_session_2026'})
    return jsonify({'ok': False, 'error': '密码错误'}), 403


@app.route('/api/review/queue')
def review_queue():
    db = get_db()
    rows = db.execute(
        "SELECT id, content, image, source, nickname, created_at FROM review_queue WHERE reviewed=0 ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    return jsonify({'items': [dict(r) for r in rows]})


@app.route('/api/review/queue', methods=['POST'])
def review_queue_add():
    """同步脚本推送候选内容到审核队列"""
    API_KEY = os.environ.get("REVIEW_API_KEY", "weiyi-internal-2026")
    headers = request.headers
    if headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "items required"}), 400

    db = get_db()
    added = 0
    for item in items:
        content = (item.get("content") or "").strip()
        if not content or len(content) < 10:
            continue
        # 去重检查
        existing = db.execute(
            "SELECT id FROM review_queue WHERE content=? AND reviewed=0", (content,)
        ).fetchone()
        if existing:
            continue
        existing2 = db.execute(
            "SELECT id FROM posts WHERE content=?", (content,)
        ).fetchone()
        if existing2:
            continue

        image = item.get("image") or ""
        source = item.get("source") or item.get("src") or ""
        nickname = item.get("nickname") or item.get("author") or ""
        db.execute(
            "INSERT INTO review_queue (content, image, source, nickname) VALUES (?,?,?,?)",
            (content, image, source, nickname),
        )
        added += 1

    db.commit()
    return jsonify({"success": True, "added": added})


@app.route('/api/review/approve', methods=['POST'])
def review_approve():
    data = request.get_json(force=True)
    rid = data.get('id')
    if not rid:
        return jsonify({'error': '缺少 id'}), 400
    db = get_db()
    row = db.execute("SELECT content, image, nickname, created_at FROM review_queue WHERE id=? AND reviewed=0", (rid,)).fetchone()
    if not row:
        return jsonify({'error': '未找到'}), 404
    db.execute(
        "INSERT INTO posts (content, image, mood, mood_emoji, mood_color, nickname, fingerprint, is_curated, category, source) VALUES (?,?,?,?,?,?,?,1,'语录',?)",
        (row['content'], row['image'] or '', '其他', '✨', '#c8963e', row['nickname'] or '', 'seed_唯一_'+str(rid), row['nickname'] or '')
    )
    db.execute("UPDATE review_queue SET reviewed=1 WHERE id=?", (rid,))
    db.commit()
    return jsonify({'success': True})


@app.route('/api/review/reject', methods=['POST'])
def review_reject():
    data = request.get_json(force=True)
    rid = data.get('id')
    if not rid:
        return jsonify({'error': '缺少 id'}), 400
    db = get_db()
    db.execute("UPDATE review_queue SET reviewed=1 WHERE id=?", (rid,))
    db.commit()
    return jsonify({'success': True})


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

/* ═══════════════════ Cards Premium Magazine System ═══════════════════ */

/* ── 基础卡片 ── */
.post-card {
  break-inside: avoid;
  margin-bottom: var(--space-lg);
  background: var(--surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--radius);
  border: 1px solid var(--glass-border);
  padding: 0;
  transition: all 0.45s var(--ease-smooth);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-card);
  animation: cardAppear 0.6s var(--ease-out) both;
}
.post-card:hover {
  background: var(--surface-hover);
  border-color: rgba(201, 160, 69, 0.2);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg), 0 0 70px rgba(201, 160, 69, 0.04);
}
@keyframes cardAppear {
  from { opacity: 0; transform: translateY(36px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 分类左色条 */
.post-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px; opacity: 0.45;
  transition: width 0.35s var(--ease-smooth), opacity 0.35s;
}
.post-card:hover::before { width: 4px; opacity: 0.8; }

/* ── Featured 大卡片 ── */
.post-card.featured {
  column-span: all;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 0;
  min-height: 320px;
  border: 1px solid rgba(201, 160, 69, 0.15);
}
.post-card.featured .post-card-image {
  grid-row: 1 / -1;
  margin: 0; border-radius: 0;
  height: 100%;
}
.post-card.featured .post-card-image img {
  height: 100%; max-height: none;
  object-fit: cover;
}
.post-card.featured .post-card-inner {
  padding: 32px 28px;
  display: flex; flex-direction: column; justify-content: center;
}
.post-card.featured::after {
  content: '✦ 精选';
  position: absolute; top: 14px; right: 18px;
  font-size: 10px; color: var(--gold-light);
  letter-spacing: 0.12em; opacity: 0.6; z-index: 2;
}
@media (max-width: 640px) {
  .post-card.featured {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  .post-card.featured .post-card-image { max-height: 220px; }
}

/* ── 卡片内部 ── */
.post-card-inner { padding: 26px 22px; }
.post-card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px;
}
.post-card-meta { display: flex; align-items: center; gap: 10px; }
.post-card-mood { font-size: 18px; line-height: 1; }
.post-card-author { font-size: 12.5px; font-weight: 500; color: var(--text-secondary); letter-spacing: 0.03em; }
.post-card-badge {
  font-size: 10px; padding: 2px 10px; border-radius: var(--radius-full);
  background: var(--gold-soft); color: var(--gold-light);
  font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
}
.post-card-badge.poetry { background: rgba(228,195,106,0.1); color: var(--cat-poetry); }
.post-card-badge.quote { background: rgba(123,184,212,0.1); color: var(--cat-quote); }
.post-card-badge.essay { background: rgba(155,142,196,0.1); color: var(--cat-essay); }
.post-card-badge.music { background: rgba(201,122,130,0.1); color: var(--cat-music); }
.post-card-badge.film { background: rgba(139,165,165,0.1); color: var(--cat-film); }
.post-card-time { font-size: 11px; color: var(--text-muted); letter-spacing: 0.02em; }

.post-card-body {
  font-size: 15px; line-height: 1.9; color: var(--text-primary);
  white-space: pre-wrap; word-break: break-word;
  font-weight: 400; letter-spacing: 0.02em;
}

.post-card-image {
  margin: 14px -22px -26px;
  overflow: hidden;
}
.post-card-image img {
  width: 100%; max-height: 360px; object-fit: cover; display: block;
  transition: transform 0.6s ease;
}
.post-card:hover .post-card-image img { transform: scale(1.04); }

.post-card-source {
  margin-top: 10px; font-size: 11px; color: var(--text-muted);
  font-style: italic; opacity: 0.5; text-align: right;
}

.post-card-actions {
  display: flex; gap: 14px; margin-top: 14px;
  padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.03);
}
.post-action {
  display: flex; align-items: center; gap: 5px;
  background: none; border: none; color: var(--text-tertiary);
  font-size: 13px; font-weight: 500; cursor: pointer;
  padding: 5px 8px; border-radius: 6px;
  transition: all var(--duration-fast); font-family: inherit;
}
.post-action:hover { background: rgba(255,255,255,0.04); color: var(--text-secondary); }
.post-action:active { transform: scale(0.94); }
.post-action.liked { color: var(--rose); background: var(--rose-soft); }
.post-action.hugged { color: var(--gold-light); background: var(--gold-soft); }
.post-action.just-liked { animation: heartBurst 0.4s var(--ease-spring); }
.post-action-count { font-size: 12px; min-width: 16px; text-align: center; font-variant-numeric: tabular-nums; }
@keyframes heartBurst {
  0% { transform: scale(1); } 30% { transform: scale(1.3); }
  60% { transform: scale(0.95); } 100% { transform: scale(1); }
}

/* ═══ 5 分类 5 种视觉身份 ═══ */

/* ── 诗歌 Poetry ── */
.post-card.cat-poetry { padding: 36px 32px; text-align: center; }
.post-card.cat-poetry .post-card-inner { padding: 0; }
.post-card.cat-poetry .post-card-body {
  font-family: var(--font-serif);
  font-size: 15px; line-height: 2.2; letter-spacing: 0.05em;
}
.post-card.cat-poetry .post-card-source { text-align: center; margin-top: 18px; font-style: italic; font-size: 12px; }
.post-card.cat-poetry::before { background: var(--cat-poetry); opacity: 0.35; }

/* ── 语录 Quote ── */
.post-card.cat-quote { padding: 30px 26px 26px; }
.post-card.cat-quote .post-card-inner { padding: 0; }
.post-card.cat-quote .post-card-body {
  font-size: 16px; font-weight: 500; line-height: 2.0;
  letter-spacing: 0.03em; position: relative; padding-left: 28px;
}
.post-card.cat-quote .post-card-body::before {
  content: '「'; position: absolute; left: -6px; top: -6px;
  font-size: 48px; font-family: var(--font-serif);
  color: var(--cat-quote); opacity: 0.3; line-height: 1;
}
.post-card.cat-quote::before { background: var(--cat-quote); opacity: 0.35; }

/* ── 随笔 Essay ── */
.post-card.cat-essay { padding: 28px 26px; background: rgba(14, 20, 38, 0.72); }
.post-card.cat-essay .post-card-inner { padding: 0; }
.post-card.cat-essay .post-card-body {
  font-size: 14.5px; line-height: 2.05; letter-spacing: 0.03em; color: #d6d2c6;
}
.post-card.cat-essay .post-card-source { text-align: right; font-style: italic; opacity: 0.4; }
.post-card.cat-essay::before { background: var(--cat-essay); opacity: 0.3; }

/* ── 音乐 Music ── */
.post-card.cat-music { padding: 22px 20px 20px; }
.post-card.cat-music .post-card-inner { padding: 0; }
.post-card.cat-music .post-card-body { font-size: 14px; line-height: 1.85; }
.post-card.cat-music::after {
  content: '♪'; position: absolute; top: 8px; right: 14px;
  font-size: 15px; color: var(--cat-music); opacity: 0.15;
}
.post-card.cat-music::before { background: var(--cat-music); opacity: 0.3; }

/* ── 光影 Film ── */
.post-card.cat-film { padding: 0; overflow: hidden; }
.post-card.cat-film .post-card-image { margin: 0; border-radius: 0; aspect-ratio: 16/9; }
.post-card.cat-film .post-card-image img { max-height: none; height: 100%; }
.post-card.cat-film .post-card-inner { padding: 18px 24px 20px; }
.post-card.cat-film .post-card-body { font-size: 15px; line-height: 1.85; }
.post-card.cat-film .post-card-source { text-align: right; font-style: italic; opacity: 0.35; font-size: 11px; }
.post-card.cat-film::before { display: none; }

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

/* 情绪图标 */
.post-card-mood-icon {
  position: absolute;
  top: 22px;
  right: 20px;
  width: 26px;
  height: 26px;
  opacity: 0.45;
  z-index: 2;
  filter: drop-shadow(0 0 8px rgba(201,160,69,0.25));
  transition: opacity 0.3s ease;
  pointer-events: none;
}
.post-card:hover .post-card-mood-icon { opacity: 0.65; }

/* 图片放大 lightbox */
.image-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.88);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: zoom-out;
  animation: fadeIn 0.25s ease;
}
.image-overlay img {
  max-width: 92%;
  max-height: 88vh;
  border-radius: var(--radius-sm);
  box-shadow: 0 24px 64px rgba(0,0,0,0.55);
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

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

// 情绪SVG微光图标
const MOOD_ICONS = {
  '开心': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(232,199,106,0.8)" stroke-width="1.5"><circle cx="12" cy="12" r="4" fill="rgba(232,199,106,0.2)"/><path d="M12 1v2M12 21v2M1 12h2M21 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
  '难过': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(123,158,199,0.7)" stroke-width="1.5"><path d="M12 3l2 5h5l-4 3 1.5 5L12 18l-4.5 2L9 11 5 8h5z" fill="rgba(123,158,199,0.15)"/></svg>',
  '愤怒': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(196,122,110,0.7)" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M8 15c1.5 2 4 2 4 2s2.5 0 4-2"/><circle cx="8.5" cy="9" r="1.5" fill="rgba(196,122,110,0.5)"/><circle cx="15.5" cy="9" r="1.5" fill="rgba(196,122,110,0.5)"/></svg>',
  '焦虑': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(155,142,196,0.7)" stroke-width="1.5"><path d="M12 3l2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z" fill="rgba(155,142,196,0.12)"/></svg>',
  '迷茫': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(139,165,165,0.7)" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5" fill="rgba(139,165,165,0.3)"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3"/></svg>',
  '感恩': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(224,176,136,0.7)" stroke-width="1.5"><path d="M12 4l2 5h5l-4 3 1.5 5L12 14l-4.5 3L9 12l-4-3h5z" fill="rgba(224,176,136,0.15)"/></svg>',
  '其他': '<svg viewBox="0 0 24 24" fill="none" stroke="rgba(200,150,62,0.7)" stroke-width="1.5"><circle cx="12" cy="12" r="3" fill="rgba(200,150,62,0.2)"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>',
};

// 图片点击放大
function zoomImage(e, src) {
  e.stopPropagation();
  const overlay = document.createElement('div');
  overlay.className = 'image-overlay';
  overlay.innerHTML = `<img src="${src}" alt="放大预览">`;
  overlay.addEventListener('click', () => overlay.remove());
  document.body.appendChild(overlay);
}

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
    const count = Math.floor((canvas.width * canvas.height) / 3800);
    stars = [];
    for (let i = 0; i < count; i++) {
      const r = Math.random() * 1.3 + 0.2;
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: r,
        baseR: r,
        vx: (Math.random() - 0.5) * 0.08,
        vy: (Math.random() - 0.5) * 0.08,
        twinkleSpeed: Math.random() * 0.012 + 0.005,
        twinkleOffset: Math.random() * Math.PI * 2,
        hue: Math.random() < 0.20 ? 38 + Math.random() * 18 : 0,
        alpha: Math.random() * 0.55 + 0.25,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const t = Date.now() * 0.001;

    for (const s of stars) {
      // 缓慢漂移
      s.x += s.vx; s.y += s.vy;
      if (s.x < 0 || s.x > canvas.width) s.vx *= -1;
      if (s.y < 0 || s.y > canvas.height) s.vy *= -1;

      const alpha = s.alpha + Math.sin(t * s.twinkleSpeed * 60 + s.twinkleOffset) * 0.35;
      const clampedAlpha = Math.max(0.08, Math.min(0.9, alpha));
      const pulseR = s.baseR * (1 + Math.sin(t * s.twinkleSpeed * 60 + s.twinkleOffset) * 0.3);

      if (s.hue > 0) {
        ctx.fillStyle = `hsla(${s.hue}, 60%, 75%, ${clampedAlpha})`;
      } else {
        ctx.fillStyle = `rgba(220,220,235,${clampedAlpha})`;
      }

      ctx.beginPath();
      ctx.arc(s.x, s.y, pulseR, 0, Math.PI * 2);
      ctx.fill();

      // 偶尔加辉光
      if (clampedAlpha > 0.6) {
        ctx.fillStyle = s.hue > 0
          ? `hsla(${s.hue}, 60%, 75%, ${clampedAlpha * 0.15})`
          : `rgba(220,220,235,${clampedAlpha * 0.12})`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, pulseR * 3, 0, Math.PI * 2);
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
    if (d.source) {
      const src = d.source;
      const hasBrackets = src.startsWith('《') && src.endsWith('》');
      parts.push(hasBrackets ? src : '《' + src + '》');
    }
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
        // 分配卡片变体：每6张1张featured
        if (i === 0 || (i > 0 && i % 6 === 0)) p.variant = 'featured';
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
  const catClassMap = { '诗歌': 'cat-poetry', '语录': 'cat-quote', '随笔': 'cat-essay', '音乐': 'cat-music', '光影': 'cat-film' };
  const catClass = catClassMap[p.category] || '';
  const hasImg = p.image ? ' has-image' : '';
  const shortTxt = p.content && p.content.length < 50 ? ' short-text' : '';
  card.className = 'post-card' + (p.is_curated ? ' curated' : '') + (catClass ? ' ' + catClass : '') + hasImg + shortTxt + (p.variant ? ' ' + p.variant : '');

  // Badge 类名映射
  const badgeClassMap = { '诗歌': 'poetry', '语录': 'quote', '随笔': 'essay', '音乐': 'music', '光影': 'film' };
  const badgeClass = badgeClassMap[p.category] || '';

  // 情绪图标
  const moodIcon = MOOD_ICONS[p.mood] || MOOD_ICONS['其他'];

  card.innerHTML = `
    ${p.image ? `<div class="post-card-image"><img src="${p.image.replace(/'/g, "\\'")}" alt="" loading="lazy"></div>` : ''}
    <div class="post-card-inner">
      <div class="post-card-header">
        <div class="post-card-meta">
          <span class="post-card-mood">${p.mood_emoji}</span>
          <span class="post-card-author">${escHtml(p.nickname)}</span>
          ${p.is_curated && p.category ? `<span class="post-card-badge ${badgeClass}">${p.category}</span>` : ''}
        </div>
        <span class="post-card-time">${timeAgo(p.created_at)}</span>
      </div>
      <div class="post-card-body">${escHtml(p.content)}</div>
      ${p.source ? `<div class="post-card-source">—— ${escHtml(p.source)}</div>` : ''}
      <div class="post-card-actions">
        <button class="post-action like-btn${p.liked_by_me ? ' liked' : ''}" data-id="${p.id}">
          ❤️ <span class="post-action-count">${p.like_count || 0}</span>
        </button>
        <button class="post-action hug-btn${p.hugged_by_me ? ' hugged' : ''}" data-id="${p.id}">
          🫂 <span class="post-action-count">${p.hug_count || 0}</span>
        </button>
      </div>
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
      posts.forEach((p, i) => {
        if (i === 0) p.variant = 'featured';
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
    return render_template('index.html')

# ═══════ 启动 ═══════
if __name__=='__main__':
    port=int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port,debug=True)
