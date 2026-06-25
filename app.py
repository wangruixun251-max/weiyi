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
    ("我想和你一起生活\n在某个小镇，\n共享无尽的黄昏\n和绵绵不绝的钟声。\n—— 茨维塔耶娃《我想和你一起生活》","其他","✨","#c8963e","诗歌星尘","诗歌","茨维塔耶娃","https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80"),
    ("我给你瘦落的街道、绝望的落日、荒郊的月亮。\n我给你一个久久地望着孤月的人的悲哀。\n—— 博尔赫斯《我用什么才能留住你》","难过","😢","#7b9ec7","诗歌星尘","诗歌","博尔赫斯","https://images.unsplash.com/photo-1504898770365-14faca6a7320?w=800&q=80"),
    ("从前的日色变得慢\n车，马，邮件都慢\n一生只够爱一个人\n—— 木心《从前慢》","感恩","🙏","#e0b088","诗歌星尘","诗歌","木心","https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80"),
    ("你一会看我\n一会看云\n我觉得\n你看我时很远\n你看云时很近\n—— 顾城《远和近》","迷茫","🤔","#8ba5a5","诗歌星尘","诗歌","顾城","https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80"),
    ("如果有来生，要做一棵树，\n站成永恒，没有悲欢的姿势。\n一半在尘土里安详，一半在风里飞扬，\n一半洒落阴凉，一半沐浴阳光。\n—— 三毛","其他","✨","#c8963e","诗歌星尘","诗歌","三毛","https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=800&q=80"),
    ("多少人爱你青春欢畅的时辰，\n爱慕你的美丽，假意或真心。\n只有一个人爱你那朝圣者的灵魂，\n爱你衰老了的脸上痛苦的皱纹。\n—— 叶芝《当你老了》","感恩","🙏","#e0b088","诗歌星尘","诗歌","叶芝","https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=800&q=80"),
    ("你不必站在风里，\n不必站在雨里，\n你可以走进我的诗里。","其他","✨","#c8963e","诗歌星尘","诗歌","佚名","https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80"),
    ("草在结它的种子，风在摇它的叶子。\n我们站着，不说话，就十分美好。\n—— 顾城《门前》","开心","😊","#e8c76a","诗歌星尘","诗歌","顾城","https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?w=800&q=80"),
    ("愿你有好运气，如果没有，愿你在不幸中学会慈悲。\n愿你被很多人爱，如果没有，愿你在寂寞中学会宽容。\n—— 刘瑜","感恩","🙏","#e0b088","诗歌星尘","诗歌","刘瑜","https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80"),
    ("我无法搬动岁月，你披着一身的月光，停泊在秋天里。\n—— 叶芝","其他","✨","#c8963e","诗歌星尘","诗歌","叶芝","https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80"),
    ("一个人需要隐藏多少秘密\n才能巧妙地度过一生\n—— 仓央嘉措","迷茫","🤔","#8ba5a5","诗歌星尘","诗歌","仓央嘉措","https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80"),
    ("每想你一次，天上飘落一粒沙，从此形成了撒哈拉。\n—— 三毛","其他","✨","#c8963e","诗歌星尘","诗歌","三毛","https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80"),
    ("在石榴花丛中，那里有光，有酒，有石榴花。\n你不来的话，这一切都了无意义。\n—— 鲁米","其他","✨","#c8963e","诗歌星尘","诗歌","鲁米","https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?w=800&q=80"),
    ("我们读诗写诗，并不是因为它们好玩，而是因为我们是人类的一分子。\n医药、法律、商业、工程，这些都是高贵的理想。\n但是诗、美、浪漫、爱，这些才是我们生存的原因。\n—— 《死亡诗社》","其他","✨","#c8963e","光影星尘","语录","《死亡诗社》","https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80"),
    ("世界上只有一种真正的英雄主义，那就是在认清生活真相之后依然热爱生活。\n—— 罗曼·罗兰","感恩","🙏","#e0b088","哲思星尘","语录","罗曼·罗兰","https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80"),
    ("我步入丛林，因为我希望生活得有意义。\n我希望活得深刻，吸取生命中所有的精华。\n把非生命的一切都击溃，以免当我生命终结时，发现自己从没有活过。\n—— 梭罗《瓦尔登湖》","迷茫","🤔","#8ba5a5","哲思星尘","语录","梭罗","https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80"),
    ("活着本身就很美妙，如果连这道理都不懂，怎么去探索更深的东西？\n—— 《三体》","其他","✨","#c8963e","光影星尘","语录","刘慈欣","https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80"),
    ("每个人心里都有一团火，路过的人只看到烟。\n但是总有一个人，总有那么一个人能看到这团火，然后走过来，陪我一起。\n—— 梵高","难过","😢","#7b9ec7","艺文星尘","语录","梵高书信","https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800&q=80"),
    ("你要搞清楚自己人生的剧本——不是你父母的续集，不是你子女的前传，更不是你朋友的外篇。\n—— 尼采","愤怒","😡","#c47a6e","哲思星尘","语录","尼采","https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=800&q=80"),
    ("我曾见过你们人类无法置信的事情：\n战舰在猎户座的边缘起火燃烧；\nC射线在星门附近的黑暗中闪耀……\n所有这些瞬间终将在时光中湮没，一如雨中的泪水。\n—— 《银翼杀手》","迷茫","🤔","#8ba5a5","光影星尘","语录","《银翼杀手》","https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80"),
    ("我们终此一生，就是要摆脱他人的期待，找到真正的自己。\n—— 《无声告白》","焦虑","😰","#9b8ec4","文学星尘","语录","伍绮诗","https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800&q=80"),
    ("为你，千千万万遍。\n—— 《追风筝的人》","感恩","🙏","#e0b088","文学星尘","语录","卡勒德·胡赛尼","https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80"),
    ("胆小鬼连幸福都会害怕，碰到棉花都会受伤。\n—— 《人间失格》","难过","😢","#7b9ec7","文学星尘","语录","太宰治","https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800&q=80"),
    ("你才25岁，你可以成为任何你想成为的人。\n—— 是枝裕和《步履不停》","迷茫","🤔","#8ba5a5","光影星尘","语录","是枝裕和","https://images.unsplash.com/photo-1499346030926-9a72daac6c63?w=800&q=80"),
    ("去爱，去失去，要不负相遇。\n—— 《想见你》","难过","😢","#7b9ec7","光影星尘","语录","《想见你》","https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=800&q=80"),
    ("人永远不知道，谁哪次不经意的跟你说了再见之后，就真的不会再见了。\n—— 《千与千寻》","难过","😢","#7b9ec7","光影星尘","语录","宫崎骏","https://images.unsplash.com/photo-1533900298318-6b8da08a523e?w=800&q=80"),
    ("凌晨四点钟，我看见海棠花未眠。\n总觉得这时，你应该在我身边。\n—— 川端康成","难过","😢","#7b9ec7","文学星尘","随笔","川端康成","https://images.unsplash.com/photo-1494959764136-6be9eb3c261e?w=800&q=80"),
    ("我所有的自负都来自我的自卑，所有的英雄气概都来自于我内心的软弱。\n我假装无情，其实是痛恨自己的深情。\n—— 马良《坦白书》","焦虑","😰","#9b8ec4","文学星尘","随笔","马良","https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80"),
    ("你对我的百般注解和识读，并不构成万分之一的我，却是一览无遗的你自己。\n—— 三毛","愤怒","😡","#c47a6e","文学星尘","随笔","三毛","https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&q=80"),
    ("一个人有两个我，一个在黑暗中醒着，一个在光明中睡着。\n—— 纪伯伦","迷茫","🤔","#8ba5a5","哲思星尘","随笔","纪伯伦","https://images.unsplash.com/photo-1500964757637-c85e8a162699?w=800&q=80"),
    ("我其实并不孤僻，甚至可以说开朗活泼。但大多时候我很懒，懒得经营一个关系。\n—— 刘瑜","其他","✨","#c8963e","文学星尘","随笔","刘瑜","https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80"),
    ("任何瞬间的心动都不容易，不要怠慢了它。\n—— 毛姆","开心","😊","#e8c76a","文学星尘","随笔","毛姆","https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&q=80"),
    ("有些人不属于你，但遇见了也挺好。","难过","😢","#7b9ec7","文学星尘","随笔","佚名","https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800&q=80"),
    ("我年轻过，落魄过，幸福过，我对生活一往情深。\n—— 马尔克斯","感恩","🙏","#e0b088","文学星尘","随笔","马尔克斯","https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80"),
    ("你说你喜欢雨，但是你在下雨的时候打伞。\n你说你喜欢太阳，但是你在阳光明媚的时候躲在阴凉的地方。\n—— 莎士比亚","其他","✨","#c8963e","文学星尘","随笔","莎士比亚","https://images.unsplash.com/photo-1504898770365-14faca6a7320?w=800&q=80"),
    ("我一生中最幸运的两件事：一件是时间终于将我对你的爱消耗殆尽；一件是很久很久以前有一天，我遇见你。\n—— 顾漫","难过","😢","#7b9ec7","文学星尘","随笔","顾漫","https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80"),
    ("活着就是，一个个无可替代的日子的累积。\n—— 坂元裕二","其他","✨","#c8963e","文学星尘","随笔","坂元裕二","https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80"),
    ("音乐是灵魂的避难所。\n当你无法用语言表达时，音乐替你说话。\n—— 贝多芬","其他","✨","#c8963e","音符星尘","音乐","贝多芬","https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=800&q=80"),
    ("人们必须用内心的耳朵去听，那才是真正听见。\n—— 德彪西","其他","✨","#c8963e","音符星尘","音乐","德彪西","https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?w=800&q=80"),
    ("没有音乐，生命将是一个错误。\n—— 尼采","其他","✨","#c8963e","音符星尘","音乐","尼采","https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80"),
    ("有些歌，前奏一响你就知道，它一定会进入你的年度歌单。","开心","😊","#e8c76a","音符星尘","音乐","佚名","https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?w=800&q=80"),
    ("在那些失眠的夜晚，巴赫的G弦之歌比任何安眠药都管用。\n—— 村上春树","焦虑","😰","#9b8ec4","音符星尘","音乐","村上春树","https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80"),
    ("歌单是一座孤岛。那些不敢说出口的话，都藏在了你反复循环的歌里。","难过","😢","#7b9ec7","音符星尘","音乐","佚名","https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80"),
    ("爵士乐是从不兑现的诺言。\n—— 米兰·昆德拉","其他","✨","#c8963e","音符星尘","音乐","米兰·昆德拉","https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80"),
    ("人生不能像做菜，把所有的料都准备好了才下锅。\n—— 《饮食男女》","其他","✨","#c8963e","光影星尘","光影","李安","https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80"),
    ("我不知道将去何方，但我已在路上。\n—— 《千与千寻》","迷茫","🤔","#8ba5a5","光影星尘","光影","宫崎骏","https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?w=800&q=80"),
    ("说好了是一辈子，差一年，差一个月，差一个时辰，都不是一辈子。\n—— 《霸王别姬》","难过","😢","#7b9ec7","光影星尘","光影","《霸王别姬》","https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80"),
    ("我们一路奋战，不是为了改变世界，而是为了不让世界改变我们。\n—— 《熔炉》","愤怒","😡","#c47a6e","光影星尘","光影","《熔炉》","https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80"),
    ("幸福不是故事，不幸才是。\n—— 《后来的我们》","难过","😢","#7b9ec7","光影星尘","光影","《后来的我们》","https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80"),
    ("做人如果没有梦想，那和咸鱼有什么区别？\n—— 《少林足球》","开心","😊","#e8c76a","光影星尘","光影","周星驰","https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80"),
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


# ═══════ HTML 模板（内联） ═══════
_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="theme-color" content="#010308" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <title>唯一 · 星尘</title>
  <style>
/* ============================================================
   Stardust — 紫色系深空主题 · 移动端优先 480px
   设计令牌系统 · 所有值通过 var() 引用 · 零硬编码
   ============================================================ */

/* ═══════════════════════════════════════════════════════════
   0. 设计令牌系统
   ═══════════════════════════════════════════════════════════ */
:root {
  /* ── 背景层级 ── */
  --bg-void: #050714;
  --bg-deep: #0a0e23;
  --bg-card: rgba(255, 255, 255, 0.04);

  /* ── 文本层级 ── */
  --text-primary: rgba(255, 255, 255, 0.92);
  --text-secondary: rgba(255, 255, 255, 0.60);
  --text-tertiary: rgba(255, 255, 255, 0.35);

  /* ── 强调色 ── */
  --accent-purple: #a78bfa;
  --accent-blue: #60a5fa;

  /* ── 边框 ── */
  --border-subtle: rgba(255, 255, 255, 0.08);

  /* ── 间距 (基数 4px) ── */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* ── 圆角 ── */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;

  /* ── 字体 ── */
  --font-system: system-ui, -apple-system, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, "Noto Sans", sans-serif,
    "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol",
    "Noto Color Emoji";

  /* ── 字号 ── */
  --font-size-xs: 12px;
  --font-size-sm: 13px;
  --font-size-base: 15px;
  --font-size-lg: 18px;
  --font-size-xl: 22px;

  /* ── 行高 ── */
  --line-height-tight: 1.4;
  --line-height-normal: 1.7;
  --line-height-relaxed: 1.85;

  /* ── 动效 ── */
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --duration-fast: 0.2s;
  --duration-normal: 0.35s;
  --duration-slow: 0.5s;

  /* ── 组件尺寸 ── */
  --nav-height: 64px;
  --fab-size: 56px;
  --safe-area-inset-bottom: env(safe-area-inset-bottom, 0px);
  --safe-area-inset-top: env(safe-area-inset-top, 0px);
}

/* ═══════════════════════════════════════════════════════════
   1. 全局 Reset + Body 基础样式
   ═══════════════════════════════════════════════════════════ */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  -webkit-text-size-adjust: 100%;
  -webkit-tap-highlight-color: transparent;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-system);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background-color: var(--bg-void);
  min-height: 100vh;
  min-height: 100dvh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
  /* 底部导航占位 */
  padding-bottom: calc(var(--nav-height) + var(--safe-area-inset-bottom) + var(--space-md));
}

img,
svg,
video {
  display: block;
  max-width: 100%;
  height: auto;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
textarea,
select {
  font: inherit;
  color: inherit;
  border: none;
  background: none;
  outline: none;
}

button {
  cursor: pointer;
  -webkit-user-select: none;
  user-select: none;
}

ul, ol {
  list-style: none;
}

::selection {
  background: var(--accent-purple);
  color: var(--bg-void);
}

/* ── 主容器：移动端全宽，480px 居中 ── */
.app-container {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: var(--safe-area-inset-top) var(--space-md) 0;
  position: relative;
  min-height: 100dvh;
}

/* ═══════════════════════════════════════════════════════════
   2. 底部导航栏 (64px, 毛玻璃, 安全区)
   ═══════════════════════════════════════════════════════════ */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: var(--nav-height);
  padding-bottom: var(--safe-area-inset-bottom);
  background: rgba(10, 14, 35, 0.82);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  flex: 1;
  height: 100%;
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
  transition: color var(--duration-fast) var(--ease-out);
  position: relative;
}

.nav-item.active {
  color: var(--accent-purple);
}

.nav-item.active::before {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  border-radius: var(--radius-full);
  background: var(--accent-purple);
}

.nav-item .nav-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  line-height: 1;
}

/* ═══════════════════════════════════════════════════════════
   3. FAB 浮动按钮 (右下角, 紫色渐变, 旋转 hover)
   ═══════════════════════════════════════════════════════════ */
.fab {
  position: fixed;
  bottom: calc(var(--nav-height) + var(--safe-area-inset-bottom) + var(--space-lg));
  right: var(--space-lg);
  width: var(--fab-size);
  height: var(--fab-size);
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  box-shadow:
    0 var(--space-sm) var(--space-lg) rgba(167, 139, 250, 0.35),
    0 var(--space-xs) var(--space-sm) rgba(96, 165, 250, 0.20);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: var(--font-size-xl);
  z-index: 90;
  transition:
    transform var(--duration-normal) var(--ease-out),
    box-shadow var(--duration-normal) var(--ease-out);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.fab:hover {
  transform: rotate(90deg) scale(1.08);
  box-shadow:
    0 var(--space-md) var(--space-xl) rgba(167, 139, 250, 0.45),
    0 var(--space-sm) var(--space-lg) rgba(96, 165, 250, 0.30);
}

.fab:active {
  transform: rotate(90deg) scale(0.94);
  transition: transform var(--duration-fast) var(--ease-out);
}

/* ═══════════════════════════════════════════════════════════
   4. 星尘流布局 (单列卡片流)
   ═══════════════════════════════════════════════════════════ */
.stardust-feed {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-md) 0;
  padding-bottom: calc(var(--nav-height) + var(--safe-area-inset-bottom) + var(--space-xl));
}

.stardust-feed > .card {
  width: 100%;
}

/* 交错入场动画 */
.stardust-feed > .card {
  opacity: 0;
  transform: translateY(20px);
  animation: card-enter var(--duration-slow) var(--ease-out) forwards;
}

.stardust-feed > .card:nth-child(1) { animation-delay: 0.05s; }
.stardust-feed > .card:nth-child(2) { animation-delay: 0.10s; }
.stardust-feed > .card:nth-child(3) { animation-delay: 0.15s; }
.stardust-feed > .card:nth-child(4) { animation-delay: 0.20s; }
.stardust-feed > .card:nth-child(5) { animation-delay: 0.25s; }
.stardust-feed > .card:nth-child(6) { animation-delay: 0.30s; }
.stardust-feed > .card:nth-child(7) { animation-delay: 0.35s; }
.stardust-feed > .card:nth-child(8) { animation-delay: 0.40s; }
.stardust-feed > .card:nth-child(9) { animation-delay: 0.45s; }
.stardust-feed > .card:nth-child(10) { animation-delay: 0.50s; }

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ═══════════════════════════════════════════════════════════
   5. 策展页面布局
   ═══════════════════════════════════════════════════════════ */
.curation-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-md) 0;
}

/* 策展头部 */
.curation-header {
  padding: var(--space-lg) var(--space-md) var(--space-md);
  text-align: center;
}

.curation-header .curation-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  line-height: var(--line-height-tight);
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-xs);
}

.curation-header .curation-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  line-height: var(--line-height-normal);
}

/* 策展分区 */
.curation-section {
  padding: 0 var(--space-md);
}

.curation-section .section-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--space-sm);
  padding-left: var(--space-xs);
}

.curation-section .section-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

/* ═══════════════════════════════════════════════════════════
   6. 书写页布局 (输入区 + 工具栏 + 发布按钮)
   ═══════════════════════════════════════════════════════════ */
.write-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: var(--space-md);
  padding-bottom: calc(var(--nav-height) + var(--safe-area-inset-bottom) + var(--space-xl));
}

/* 输入区 */
.write-input {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.write-input textarea {
  flex: 1;
  min-height: 200px;
  padding: var(--space-md);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  resize: none;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.write-input textarea:focus {
  border-color: var(--accent-purple);
  box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.15);
}

.write-input textarea::placeholder {
  color: var(--text-tertiary);
}

/* 工具栏 */
.write-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.write-toolbar::-webkit-scrollbar {
  display: none;
}

.toolbar-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: var(--font-size-base);
  transition:
    background var(--duration-fast) var(--ease-out),
    color var(--duration-fast) var(--ease-out);
}

.toolbar-btn:hover,
.toolbar-btn:active {
  background: rgba(167, 139, 250, 0.12);
  color: var(--accent-purple);
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
  flex-shrink: 0;
  margin: 0 var(--space-xs);
}

/* 发布按钮 */
.publish-btn {
  margin-top: var(--space-lg);
  padding: var(--space-md) var(--space-xl);
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  border-radius: var(--radius-full);
  color: #fff;
  font-size: var(--font-size-base);
  font-weight: 600;
  text-align: center;
  transition:
    transform var(--duration-fast) var(--ease-out),
    box-shadow var(--duration-fast) var(--ease-out);
  box-shadow: 0 var(--space-sm) var(--space-lg) rgba(167, 139, 250, 0.30);
}

.publish-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 var(--space-md) var(--space-xl) rgba(167, 139, 250, 0.40);
}

.publish-btn:active {
  transform: translateY(0) scale(0.97);
}

/* ═══════════════════════════════════════════════════════════
   7. 我的页布局 (头像 + 统计 + 菜单)
   ═══════════════════════════════════════════════════════════ */
.profile-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-lg) var(--space-md);
  padding-bottom: calc(var(--nav-height) + var(--safe-area-inset-bottom) + var(--space-xl));
}

/* 头像区域 */
.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg) 0;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #fff;
  box-shadow: 0 var(--space-sm) var(--space-lg) rgba(167, 139, 250, 0.25);
}

.profile-name {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.profile-bio {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  text-align: center;
  max-width: 280px;
}

/* 统计区 */
.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: var(--space-md) 0;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--accent-purple);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* 菜单列表 */
.profile-menu {
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--duration-fast) var(--ease-out);
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover,
.menu-item:active {
  background: rgba(167, 139, 250, 0.06);
}

.menu-item .menu-icon {
  margin-right: var(--space-sm);
  color: var(--text-secondary);
  font-size: var(--font-size-base);
}

.menu-item .menu-arrow {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
}

/* ═══════════════════════════════════════════════════════════
   8. 卡片样式 — 情绪图标(右上) + 时间(左上) + 正文 + 图片 + 互动区
   ═══════════════════════════════════════════════════════════ */
.card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition:
    border-color var(--duration-normal) var(--ease-out),
    box-shadow var(--duration-normal) var(--ease-out),
    transform var(--duration-normal) var(--ease-out);
}

.card:hover {
  border-color: rgba(167, 139, 250, 0.25);
  box-shadow:
    0 var(--space-sm) var(--space-xl) rgba(167, 139, 250, 0.08),
    0 var(--space-md) var(--space-2xl) rgba(5, 7, 20, 0.40);
  transform: translateY(-2px);
}

.card:active {
  transform: scale(0.985);
  transition: transform var(--duration-fast) var(--ease-out);
}

/* ── 卡片头部：左上时间 + 右上情绪图标 ── */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-md) var(--space-md) 0;
}

.card-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  letter-spacing: 0.03em;
  line-height: var(--line-height-tight);
}

.card-mood {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: rgba(167, 139, 250, 0.10);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  line-height: 1;
  flex-shrink: 0;
}

/* ── 卡片正文 ── */
.card-body {
  padding: var(--space-sm) var(--space-md) var(--space-md);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  color: var(--text-primary);
  word-break: break-word;
}

.card-body p + p {
  margin-top: var(--space-sm);
}

/* ── 卡片图片 ── */
.card-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  background: var(--bg-deep);
  transition: transform var(--duration-slow) var(--ease-out);
}

.card:hover .card-image {
  transform: scale(1.03);
}

.card-image-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg,
    rgba(167, 139, 250, 0.05),
    rgba(96, 165, 250, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: var(--font-size-xl);
}

/* ── 卡片互动区 ── */
.card-actions {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-sm) var(--space-md) var(--space-md);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
  transition:
    color var(--duration-fast) var(--ease-out),
    transform var(--duration-fast) var(--ease-out);
}

.action-btn:hover {
  color: var(--accent-purple);
}

.action-btn:active {
  transform: scale(0.90);
}

.action-btn .action-icon {
  font-size: var(--font-size-base);
  line-height: 1;
}

.action-btn .action-count {
  font-size: var(--font-size-xs);
}

/* 点赞激活态 */
.action-btn.liked {
  color: var(--accent-purple);
}

.action-btn.liked .action-icon {
  animation: heart-pop var(--duration-normal) var(--ease-out);
}

@keyframes heart-pop {
  0%   { transform: scale(1); }
  30%  { transform: scale(1.35); }
  60%  { transform: scale(0.90); }
  100% { transform: scale(1); }
}

/* ═══════════════════════════════════════════════════════════
   9. 骨架屏动画
   ═══════════════════════════════════════════════════════════ */
.skeleton {
  pointer-events: none;
  user-select: none;
}

.skeleton .card-header,
.skeleton .card-body,
.skeleton .card-image,
.skeleton .card-actions {
  position: relative;
}

.skeleton .card-image {
  background: var(--bg-deep);
}

/* 骨架占位条 */
.skeleton-line {
  height: 14px;
  border-radius: var(--radius-full);
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.04) 25%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.04) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
  margin-bottom: var(--space-sm);
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-line.medium {
  width: 80%;
}

.skeleton-line.long {
  width: 100%;
}

.skeleton-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.04) 25%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.04) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 骨架卡片结构 */
.skeleton-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

.skeleton-card .skeleton-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.skeleton-card .skeleton-row:last-child {
  margin-bottom: 0;
}

/* ═══════════════════════════════════════════════════════════
   10. Toast 提示
   ═══════════════════════════════════════════════════════════ */
.toast-container {
  position: fixed;
  top: calc(var(--safe-area-inset-top) + var(--space-md));
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  pointer-events: none;
  width: calc(100% - var(--space-xl));
  max-width: 480px;
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: rgba(10, 14, 35, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  box-shadow:
    0 var(--space-sm) var(--space-xl) rgba(5, 7, 20, 0.50),
    0 var(--space-xs) var(--space-sm) rgba(0, 0, 0, 0.30);
  pointer-events: auto;
  animation: toast-in var(--duration-normal) var(--ease-out) forwards;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
}

.toast.toast-out {
  animation: toast-out var(--duration-normal) var(--ease-out) forwards;
}

.toast .toast-icon {
  flex-shrink: 0;
  font-size: var(--font-size-base);
  line-height: 1;
}

/* 变体 */
.toast-success .toast-icon { color: #34d399; }
.toast-error .toast-icon   { color: #f87171; }
.toast-info .toast-icon    { color: var(--accent-blue); }
.toast-warning .toast-icon { color: #fbbf24; }

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(-12px) scale(0.92);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-12px) scale(0.92);
  }
}

/* ═══════════════════════════════════════════════════════════
   11. 星空背景 (纯 CSS box-shadow 星点 + twinkle 动画)
   ═══════════════════════════════════════════════════════════ */
.starry-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
  overflow: hidden;
}

/* 星点层 — 用伪元素 + box-shadow 画星 */
.starry-bg::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 2px;
  height: 2px;
  border-radius: var(--radius-full);
  background: transparent;
  box-shadow:
    /* 第1组 — 慢闪烁 */
    15vw 8vh  0 0 rgba(255, 255, 255, 0.70),
    23vw 12vh 0 0 rgba(255, 255, 255, 0.55),
    31vw 5vh  0 0 rgba(255, 255, 255, 0.80),
    42vw 18vh 0 0 rgba(255, 255, 255, 0.45),
    55vw 9vh  0 0 rgba(255, 255, 255, 0.65),
    68vw 14vh 0 0 rgba(255, 255, 255, 0.50),
    77vw 6vh  0 0 rgba(255, 255, 255, 0.75),
    88vw 20vh 0 0 rgba(255, 255, 255, 0.40),
    8vw  28vh 0 0 rgba(255, 255, 255, 0.60),
    19vw 35vh 0 0 rgba(255, 255, 255, 0.35),
    33vw 42vh 0 0 rgba(255, 255, 255, 0.55),
    48vw 38vh 0 0 rgba(255, 255, 255, 0.70),
    62vw 30vh 0 0 rgba(255, 255, 255, 0.45),
    75vw 45vh 0 0 rgba(255, 255, 255, 0.50),
    85vw 33vh 0 0 rgba(255, 255, 255, 0.65),
    /* 第2组 */
    11vw 55vh 0 0 rgba(255, 255, 255, 0.40),
    25vw 62vh 0 0 rgba(255, 255, 255, 0.75),
    37vw 50vh 0 0 rgba(255, 255, 255, 0.60),
    50vw 68vh 0 0 rgba(255, 255, 255, 0.35),
    64vw 55vh 0 0 rgba(255, 255, 255, 0.55),
    79vw 72vh 0 0 rgba(255, 255, 255, 0.70),
    90vw 60vh 0 0 rgba(255, 255, 255, 0.45),
    5vw  78vh 0 0 rgba(255, 255, 255, 0.50),
    20vw 85vh 0 0 rgba(255, 255, 255, 0.65),
    40vw 80vh 0 0 rgba(255, 255, 255, 0.40),
    58vw 90vh 0 0 rgba(255, 255, 255, 0.55),
    72vw 82vh 0 0 rgba(255, 255, 255, 0.70),
    83vw 75vh 0 0 rgba(255, 255, 255, 0.35),
    95vw 88vh 0 0 rgba(255, 255, 255, 0.60);

  animation: twinkle-group1 3.6s ease-in-out infinite alternate;
}

/* 第2层星星 — 不同节奏 */
.starry-bg::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 1px;
  border-radius: var(--radius-full);
  background: transparent;
  box-shadow:
    6vw  3vh  0 0 rgba(167, 139, 250, 0.50),
    18vw 10vh 0 0 rgba(167, 139, 250, 0.35),
    28vw 2vh  0 0 rgba(96, 165, 250, 0.55),
    38vw 15vh 0 0 rgba(167, 139, 250, 0.40),
    52vw 7vh  0 0 rgba(96, 165, 250, 0.60),
    65vw 11vh 0 0 rgba(167, 139, 250, 0.30),
    73vw 4vh  0 0 rgba(96, 165, 250, 0.50),
    82vw 17vh 0 0 rgba(167, 139, 250, 0.45),
    92vw 8vh  0 0 rgba(96, 165, 250, 0.35),
    9vw  23vh 0 0 rgba(167, 139, 250, 0.55),
    22vw 32vh 0 0 rgba(96, 165, 250, 0.40),
    35vw 40vh 0 0 rgba(167, 139, 250, 0.30),
    47vw 35vh 0 0 rgba(96, 165, 250, 0.50),
    60vw 28vh 0 0 rgba(167, 139, 250, 0.45),
    76vw 42vh 0 0 rgba(96, 165, 250, 0.55),
    89vw 30vh 0 0 rgba(167, 139, 250, 0.35),
    14vw 52vh 0 0 rgba(96, 165, 250, 0.40),
    30vw 58vh 0 0 rgba(167, 139, 250, 0.60),
    44vw 65vh 0 0 rgba(96, 165, 250, 0.35),
    57vw 52vh 0 0 rgba(167, 139, 250, 0.50),
    69vw 70vh 0 0 rgba(96, 165, 250, 0.45),
    81vw 58vh 0 0 rgba(167, 139, 250, 0.30),
    94vw 65vh 0 0 rgba(96, 165, 250, 0.55),
    7vw  75vh 0 0 rgba(167, 139, 250, 0.40),
    24vw 82vh 0 0 rgba(96, 165, 250, 0.50),
    41vw 78vh 0 0 rgba(167, 139, 250, 0.35),
    55vw 88vh 0 0 rgba(96, 165, 250, 0.45),
    70vw 80vh 0 0 rgba(167, 139, 250, 0.55),
    86vw 72vh 0 0 rgba(96, 165, 250, 0.40);

  animation: twinkle-group2 2.8s ease-in-out infinite alternate;
}

@keyframes twinkle-group1 {
  0%, 100% { opacity: 0.55; }
  50%      { opacity: 1.0; }
}

@keyframes twinkle-group2 {
  0%, 100% { opacity: 0.35; }
  50%      { opacity: 0.85; }
}

/* ═══════════════════════════════════════════════════════════
   12. 涟漪效果
   ═══════════════════════════════════════════════════════════ */
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple-effect {
  position: absolute;
  border-radius: var(--radius-full);
  background: rgba(167, 139, 250, 0.30);
  transform: scale(0);
  animation: ripple-expand 0.7s var(--ease-out) forwards;
  pointer-events: none;
}

@keyframes ripple-expand {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* 兼容 prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .ripple-effect {
    animation: none;
  }
}

/* ═══════════════════════════════════════════════════════════
   13. 响应式布局
   ═══════════════════════════════════════════════════════════ */

/* ── 480px：居中容器 ── */
@media (min-width: 480px) {
  .app-container {
    padding-left: var(--space-lg);
    padding-right: var(--space-lg);
  }

  .stardust-feed {
    gap: var(--space-lg);
  }

  .write-page {
    padding-left: var(--space-lg);
    padding-right: var(--space-lg);
  }

  .profile-page {
    padding-left: var(--space-lg);
    padding-right: var(--space-lg);
  }
}

/* ── >769px：桌面端背景渐变 + 卡片双列 ── */
@media (min-width: 769px) {
  body {
    background:
      radial-gradient(ellipse 80% 60% at 50% -10%,
        rgba(167, 139, 250, 0.08) 0%,
        transparent 60%
      ),
      radial-gradient(ellipse 60% 50% at 80% 80%,
        rgba(96, 165, 250, 0.05) 0%,
        transparent 60%
      ),
      var(--bg-void);
  }

  .app-container {
    max-width: 720px;
    padding-left: var(--space-xl);
    padding-right: var(--space-xl);
  }

  /* 双列卡片流 */
  .stardust-feed {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-lg);
  }

  .stardust-feed > .card:first-child {
    grid-column: span 2;
  }

  /* 策展页双列 */
  .curation-section .section-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-md);
  }

  /* 调整 FAB 位置 */
  .fab {
    right: calc(50% - 360px + var(--space-lg));
    bottom: var(--space-2xl);
  }
}

/* ── >1024px：宽屏三列 ── */
@media (min-width: 1024px) {
  .app-container {
    max-width: 960px;
  }

  .stardust-feed {
    grid-template-columns: 1fr 1fr 1fr;
  }

  .stardust-feed > .card:first-child {
    grid-column: span 2;
  }

  .fab {
    right: calc(50% - 480px + var(--space-lg));
  }
}

/* ── 横屏适配 ── */
@media (orientation: landscape) and (max-height: 500px) {
  body {
    padding-bottom: 0;
  }

  .bottom-nav {
    position: static;
    height: auto;
    padding: var(--space-sm) 0;
    transform: none;
    left: auto;
    max-width: none;
    background: var(--bg-deep);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
  }

  .fab {
    bottom: var(--space-md);
    right: var(--space-md);
  }

  .app-container {
    max-width: 100%;
    padding-bottom: var(--space-md);
  }

  .stardust-feed {
    padding-bottom: var(--space-md);
  }

  /* 横屏书写页 */
  .write-input textarea {
    min-height: 120px;
  }
}

/* ── 大横屏优化 ── */
@media (orientation: landscape) and (min-width: 769px) {
  .stardust-feed {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-lg);
  }

  .write-page {
    flex-direction: row;
    gap: var(--space-lg);
    align-items: flex-start;
  }

  .write-page .write-input {
    flex: 1;
  }

  .write-page .publish-btn {
    flex-shrink: 0;
    margin-top: 0;
    align-self: flex-end;
  }
}

/* ═══════════════════════════════════════════════════════════
   14. 安全区适配
   ═══════════════════════════════════════════════════════════ */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .bottom-nav {
    padding-bottom: env(safe-area-inset-bottom);
  }

  body {
    padding-bottom: calc(var(--nav-height) + env(safe-area-inset-bottom) + var(--space-md));
  }

  .app-container {
    padding-top: env(safe-area-inset-top);
  }

  .toast-container {
    top: calc(env(safe-area-inset-top) + var(--space-md));
  }
}

/* ── 减少动画偏好 ── */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

</style>
</head>
<body class="theme-deep-space">

  <!-- ============================================================
       Layer 0: 星空背景 (纯CSS box-shadow星点)
       ============================================================ -->
  <div class="stars-container" aria-hidden="true">
    <div class="stars-layer stars-layer--1"></div>
    <div class="stars-layer stars-layer--2"></div>
    <div class="stars-layer stars-layer--3"></div>
  </div>

  <!-- ============================================================
       Layer 1: 主应用容器 (max-width: 480px, 居中)
       ============================================================ -->
  <div class="app-shell" id="appShell">

    <!-- ── Hero 区 (缩小版，非全屏) ── -->
    <header class="hero" id="heroSection">
      <div class="hero__brand">
        <h1 class="hero__title">
          <span class="hero__title-cn">唯一</span>
          <span class="hero__title-sub">The One</span>
        </h1>
      </div>
      <div class="hero__daily" id="dailyMessage">
        <div class="hero__daily-quote">
          <span class="hero__daily-icon">✦</span>
          <p class="hero__daily-text">正在接收今天的宇宙信号…</p>
        </div>
        <p class="hero__daily-attribution" id="dailyAttribution"></p>
      </div>
    </header>

    <!-- ════════════════════════════════════════════════════════
         Page Views (通过 data-view 控制显示/隐藏)
         ════════════════════════════════════════════════════════ -->

    <!-- ── View 1: 星尘流 ── -->
    <main class="page-view page-view--active" data-view="stardust" id="viewStardust">
      <!-- 顶部操作栏 -->
      <div class="view-header">
        <h2 class="view-header__title">星尘流</h2>
        <button class="btn-icon btn-icon--ghost drift-bottle-btn" id="driftBottleBtn" aria-label="漂流瓶 - 随机一篇" title="捞一颗星星">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3c-2.5 4-2.5 10 0 14 2.5-4 2.5-10 0-14Z"/>
            <path d="M12 3c2.5 4 2.5 10 0 14"/>
            <line x1="12" y1="3" x2="12" y2="17"/>
            <circle cx="12" cy="10" r="1.5"/>
            <path d="M5 10h14"/>
          </svg>
        </button>
      </div>

      <!-- 骨架屏 (加载状态) -->
      <div class="skeleton-list" id="skeletonStardust">
        <div class="skeleton-card">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-line skeleton-line--body"></div>
          <div class="skeleton-line skeleton-line--body skeleton-line--short"></div>
          <div class="skeleton-line skeleton-line--meta"></div>
        </div>
        <div class="skeleton-card">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-line skeleton-line--body"></div>
          <div class="skeleton-line skeleton-line--body skeleton-line--short"></div>
          <div class="skeleton-line skeleton-line--meta"></div>
        </div>
        <div class="skeleton-card">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-line skeleton-line--body"></div>
          <div class="skeleton-line skeleton-line--meta"></div>
        </div>
      </div>

      <!-- 帖子卡片列表 (真实数据填充区) -->
      <div class="post-feed" id="postFeedStardust">
        <!-- JS动态渲染 post-card -->
      </div>

      <!-- 空状态 -->
      <div class="empty-state" id="emptyStardust" style="display:none;">
        <div class="empty-state__icon">🌌</div>
        <p class="empty-state__text">星尘尚未洒落</p>
        <p class="empty-state__hint">成为第一个留下痕迹的人</p>
      </div>

      <!-- 加载更多指示器 -->
      <div class="load-more" id="loadMoreStardust" style="display:none;">
        <div class="load-more__spinner"></div>
        <span>正在捕捉更多星尘…</span>
      </div>
    </main>

    <!-- ── View 2: 策展 ── -->
    <main class="page-view" data-view="curated" id="viewCurated">
      <div class="view-header">
        <h2 class="view-header__title">策展</h2>
      </div>

      <!-- 骨架屏 -->
      <div class="skeleton-curated" id="skeletonCurated">
        <div class="skeleton-category">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-category__cards">
            <div class="skeleton-line skeleton-line--body"></div>
            <div class="skeleton-line skeleton-line--body skeleton-line--short"></div>
          </div>
        </div>
        <div class="skeleton-category">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-category__cards">
            <div class="skeleton-line skeleton-line--body"></div>
          </div>
        </div>
      </div>

      <!-- 分类区块容器 -->
      <div class="curated-sections" id="curatedSections">
        <!-- JS动态渲染分类区块 .curated-section -->
      </div>

      <!-- 空状态 -->
      <div class="empty-state" id="emptyCurated" style="display:none;">
        <div class="empty-state__icon">📜</div>
        <p class="empty-state__text">策展区暂无内容</p>
        <p class="empty-state__hint">策展人正在精心挑选</p>
      </div>
    </main>

    <!-- ── View 3: 书写 ── -->
    <main class="page-view" data-view="write" id="viewWrite">
      <div class="view-header">
        <h2 class="view-header__title">书写</h2>
      </div>

      <form class="write-form" id="writeForm" autocomplete="off">
        <!-- 文本输入区 -->
        <div class="write-form__body">
          <textarea
            class="write-form__textarea"
            id="writeContent"
            name="content"
            placeholder="此刻，你想留下什么…"
            maxlength="2000"
            rows="6"
          ></textarea>
          <div class="write-form__char-count">
            <span id="charCount">0</span><span>/2000</span>
          </div>
        </div>

        <!-- 情绪标签选择器 -->
        <div class="write-form__moods" id="moodSelector">
          <span class="write-form__label">此刻情绪</span>
          <div class="mood-chips">
            <button type="button" class="mood-chip" data-mood="calm" data-emoji="🌿" data-color="#7ca87c">🌿 平静</button>
            <button type="button" class="mood-chip" data-mood="happy" data-emoji="🌟" data-color="#e4c36a">🌟 喜悦</button>
            <button type="button" class="mood-chip" data-mood="melancholy" data-emoji="🌙" data-color="#7b8fce">🌙 忧郁</button>
            <button type="button" class="mood-chip" data-mood="passionate" data-emoji="🔥" data-color="#c97a82">🔥 热烈</button>
            <button type="button" class="mood-chip" data-mood="thoughtful" data-emoji="🪐" data-color="#a38cc9">🪐 沉思</button>
            <button type="button" class="mood-chip" data-mood="wistful" data-emoji="🍂" data-color="#c99f6a">🍂 怀念</button>
            <button type="button" class="mood-chip" data-mood="lonely" data-emoji="🕯️" data-color="#8a9bb5">🕯️ 孤独</button>
            <button type="button" class="mood-chip" data-mood="hopeful" data-emoji="✨" data-color="#c9a045">✨ 期待</button>
          </div>
        </div>

        <!-- 图片上传区 -->
        <div class="write-form__image" id="imageUpload">
          <span class="write-form__label">配图（可选）</span>
          <div class="image-upload-area" id="imageUploadArea">
            <input
              type="file"
              id="imageInput"
              name="image"
              accept="image/*"
              class="image-upload-area__input"
            />
            <div class="image-upload-area__placeholder" id="imagePlaceholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span>点击添加图片</span>
            </div>
            <div class="image-upload-area__preview" id="imagePreview" style="display:none;">
              <img id="previewImg" src="" alt="预览" />
              <button type="button" class="image-upload-area__remove" id="removeImage" aria-label="移除图片">&times;</button>
            </div>
          </div>
        </div>

        <!-- 分类选择 -->
        <div class="write-form__category" id="categorySelector">
          <span class="write-form__label">分类</span>
          <div class="category-select">
            <button type="button" class="category-option category-option--active" data-category="poem">诗歌</button>
            <button type="button" class="category-option" data-category="quote">语录</button>
            <button type="button" class="category-option" data-category="essay">随笔</button>
            <button type="button" class="category-option" data-category="letter">书信</button>
            <button type="button" class="category-option" data-category="moment">瞬间</button>
          </div>
        </div>

        <!-- 发布按钮 -->
        <button type="submit" class="btn-publish" id="publishBtn">
          <span class="btn-publish__icon">✦</span>
          <span class="btn-publish__text">撒向星尘</span>
        </button>
      </form>
    </main>

    <!-- ── View 4: 我的 ── -->
    <main class="page-view" data-view="profile" id="viewProfile">
      <div class="view-header">
        <h2 class="view-header__title">我的</h2>
      </div>

      <!-- 匿名头像区 (渐变圆形) -->
      <div class="profile-avatar-section">
        <div class="profile-avatar" id="profileAvatar">
          <div class="profile-avatar__gradient"></div>
          <span class="profile-avatar__initial">?</span>
        </div>
        <div class="profile-nickname" id="profileNickname">
          <span class="profile-nickname__text">匿名旅人</span>
          <button class="btn-icon btn-icon--small" id="editNicknameBtn" aria-label="编辑昵称">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 统计区 -->
      <div class="profile-stats" id="profileStats">
        <div class="stat-item">
          <span class="stat-item__value" id="statPosts">0</span>
          <span class="stat-item__label">星尘</span>
        </div>
        <div class="stat-item">
          <span class="stat-item__value" id="statLikes">0</span>
          <span class="stat-item__label">被喜欢</span>
        </div>
        <div class="stat-item">
          <span class="stat-item__value" id="statHugs">0</span>
          <span class="stat-item__label">被拥抱</span>
        </div>
      </div>

      <!-- 我的帖子列表 -->
      <div class="profile-posts" id="myPostsFeed">
        <!-- JS动态渲染 -->
      </div>

      <!-- 空状态 -->
      <div class="empty-state" id="emptyMyPosts" style="display:none;">
        <div class="empty-state__icon">📭</div>
        <p class="empty-state__text">还没有留下星尘</p>
        <p class="empty-state__hint">去书写你的第一颗星星吧</p>
      </div>

      <!-- 菜单区 -->
      <div class="profile-menu">
        <button class="menu-item" id="menuMyPosts">
          <span class="menu-item__icon">📝</span>
          <span class="menu-item__label">我的星尘</span>
          <svg class="menu-item__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <button class="menu-item" id="menuTheme">
          <span class="menu-item__icon">🌓</span>
          <span class="menu-item__label">主题设置</span>
          <svg class="menu-item__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <button class="menu-item" id="menuAbout">
          <span class="menu-item__icon">💫</span>
          <span class="menu-item__label">关于唯一</span>
          <svg class="menu-item__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
    </main>

    <!-- ════════════════════════════════════════════════════════
         FAB (浮动发布按钮，右下角)
         ════════════════════════════════════════════════════════ -->
    <button class="fab" id="fabPublish" aria-label="发布星尘">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
    </button>

    <!-- ════════════════════════════════════════════════════════
         底部 Tab 导航 (毛玻璃效果)
         ════════════════════════════════════════════════════════ -->
    <nav class="tab-bar" id="tabBar">
      <button class="tab-bar__item tab-bar__item--active" data-tab="stardust" aria-label="星尘">
        <svg class="tab-bar__icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
        </svg>
        <span class="tab-bar__label">星尘</span>
      </button>
      <button class="tab-bar__item" data-tab="curated" aria-label="策展">
        <svg class="tab-bar__icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        <span class="tab-bar__label">策展</span>
      </button>
      <button class="tab-bar__item" data-tab="write" aria-label="书写">
        <svg class="tab-bar__icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
        <span class="tab-bar__label">书写</span>
      </button>
      <button class="tab-bar__item" data-tab="profile" aria-label="我的">
        <svg class="tab-bar__icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span class="tab-bar__label">我的</span>
      </button>
    </nav>

    <!-- ════════════════════════════════════════════════════════
         Toast 通知容器
         ════════════════════════════════════════════════════════ -->
    <div class="toast-container" id="toastContainer" aria-live="polite">
      <!-- JS动态注入 .toast-item -->
    </div>

    <!-- ════════════════════════════════════════════════════════
         Modal 通用弹窗容器
         ════════════════════════════════════════════════════════ -->
    <div class="modal-overlay" id="modalOverlay" style="display:none;">
      <div class="modal-content" id="modalContent">
        <!-- JS动态渲染 -->
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════
         漂流瓶弹窗 (随机帖子)
         ════════════════════════════════════════════════════════ -->
    <div class="drift-bottle-modal" id="driftBottleModal" style="display:none;">
      <div class="drift-bottle-modal__backdrop"></div>
      <div class="drift-bottle-modal__card" id="driftBottleCard">
        <button class="drift-bottle-modal__close" id="driftBottleClose" aria-label="关闭">&times;</button>
        <div class="drift-bottle-modal__content" id="driftBottleContent">
          <!-- JS动态渲染随机帖子 -->
        </div>
        <button class="drift-bottle-modal__refresh" id="driftBottleRefresh" aria-label="再来一颗">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          <span>换一颗星星</span>
        </button>
      </div>
    </div>

  </div><!-- /app-shell -->

  <!-- ============================================================
       外部JS引用（最终将内联）
       ============================================================ -->
<script>
/**
 * ============================================================
 * 「唯一」文艺社区 — 应用主逻辑 (app.js)
 * ============================================================
 * 深空宇宙主题 · 五分类卡片 · 瀑布流 · 互动 · 漂流瓶
 * 纯 Vanilla JS · async/await · 无框架依赖
 * ============================================================
 */

// ═══════════════════════════════════════════════════════════
// 0. 配置常量
// ═══════════════════════════════════════════════════════════

const API_BASE = '';
const CONFIG = {
  // 无限滚动阈值（距底部多少px时触发加载）
  scrollThreshold: 300,
  // 每页帖子数
  pageSize: 20,
  // featured 卡片间隔（每N张放1张featured）
  featuredInterval: 6,
  // skeleton 骨架屏数量
  skeletonCount: 6,
  // Toast 持续时间 (ms)
  toastDuration: 2800,
  // 图片压缩配置
  imageMaxWidth: 1200,
  imageMaxHeight: 1200,
  imageQuality: 0.75,
  // 昵称长度限制
  nicknameMaxLen: 12,
  // 内容长度限制
  contentMaxLen: 5000,
  // 心情列表
  moods: [
    { id: 'calm',     emoji: '🌙', color: '#7eb8da', label: '平静' },
    { id: 'thoughtful', emoji: '🌿', color: '#a8c97e', label: '沉思' },
    { id: 'inspired', emoji: '✨', color: '#c9a045', label: '灵感' },
    { id: 'melancholy', emoji: '🌧️', color: '#9b8ec4', label: '感怀' },
    { id: 'passionate', emoji: '🔥', color: '#d4876e', label: '热烈' },
    { id: 'lonely',  emoji: '🌌', color: '#8ba5a5', label: '寂寥' },
    { id: 'grateful', emoji: '🙏', color: '#e4c36a', label: '感恩' },
    { id: 'hopeful', emoji: '🌅', color: '#c97a82', label: '期待' },
  ],
  // 分类映射
  categoryMap: {
    '诗歌': 'poetry',
    '语录': 'quote',
    '随笔': 'essay',
    '音乐': 'music',
    '光影': 'film',
  },
};

// ═══════════════════════════════════════════════════════════
// 1. 浏览器指纹 (Canvas Fingerprinting)
// ═══════════════════════════════════════════════════════════

function generateFingerprint() {
  return new Promise((resolve) => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 280;
      canvas.height = 60;
      const ctx = canvas.getContext('2d');

      // 绘制多层文本 + 几何图形
      ctx.textBaseline = 'top';
      ctx.font = '14px "Noto Serif SC", "PingFang SC", serif';
      ctx.fillStyle = '#c9a045';
      ctx.fillText('唯一 ✦ 星尘', 4, 4);

      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.fillStyle = '#7eb8da';
      ctx.fillText(navigator.userAgent.slice(0, 40), 4, 26);

      ctx.beginPath();
      ctx.arc(230, 30, 8, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(201,160,69,0.4)';
      ctx.fill();

      ctx.font = '10px "PingFang SC", sans-serif';
      ctx.fillStyle = '#a4a6b8';
      const extras = [
        navigator.language || '',
        screen.colorDepth || '',
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
      ].join('|');
      ctx.fillText(extras.slice(0, 60), 4, 46);

      const dataURL = canvas.toDataURL();
      let hash = 0;
      for (let i = 0; i < dataURL.length; i++) {
        const ch = dataURL.charCodeAt(i);
        hash = ((hash << 5) - hash) + ch;
        hash |= 0;
      }
      const fp = 'fp_' + Math.abs(hash).toString(36).padStart(8, '0');
      resolve(fp);
    } catch (e) {
      // 降级：基于 navigator 属性
      const raw = [
        navigator.userAgent,
        navigator.language,
        screen.colorDepth,
        screen.width,
        screen.height,
        new Date().getTimezoneOffset(),
      ].join('|');
      let h = 0;
      for (let i = 0; i < raw.length; i++) {
        h = ((h << 5) - h) + raw.charCodeAt(i);
        h |= 0;
      }
      resolve('fp_' + Math.abs(h).toString(36).padStart(8, '0'));
    }
  });
}

async function getOrCreateFingerprint() {
  let fp = localStorage.getItem('onlyone_fingerprint');
  if (!fp) {
    fp = await generateFingerprint();
    localStorage.setItem('onlyone_fingerprint', fp);
  }
  return fp;
}

// ═══════════════════════════════════════════════════════════
// 2. Toast 通知系统
// ═══════════════════════════════════════════════════════════

let toastTimer = null;

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  // 清除上一个定时器
  if (toastTimer) clearTimeout(toastTimer);

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span class="toast__icon">${type === 'success' ? '✦' : type === 'error' ? '✧' : '·'}</span>
    <span class="toast__text">${escapeHTML(message)}</span>
  `;

  container.appendChild(toast);

  // 入场动画
  requestAnimationFrame(() => {
    toast.classList.add('toast--visible');
  });

  // 自动消失
  toastTimer = setTimeout(() => {
    toast.classList.remove('toast--visible');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, CONFIG.toastDuration);
}

// ═══════════════════════════════════════════════════════════
// 3. 工具函数
// ═══════════════════════════════════════════════════════════

function escapeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (mins < 1) return '刚刚';
  if (mins < 60) return `${mins}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;

  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function getCategoryClass(category) {
  const map = {
    '诗歌': 'cat-poetry',
    '语录': 'cat-quote',
    '随笔': 'cat-essay',
    '音乐': 'cat-music',
    '光影': 'cat-film',
    'poetry': 'cat-poetry',
    'quote': 'cat-quote',
    'essay': 'cat-essay',
    'music': 'cat-music',
    'film': 'cat-film',
    'photo': 'cat-film',
  };
  return map[category] || 'cat-essay';
}

function getCardModifierClass(category) {
  const map = {
    '诗歌': 'post-card--poetry',
    '语录': 'post-card--quote',
    '随笔': 'post-card--essay',
    '音乐': 'post-card--music',
    '光影': 'post-card--photo',
    'poetry': 'post-card--poetry',
    'quote': 'post-card--quote',
    'essay': 'post-card--essay',
    'music': 'post-card--music',
    'film': 'post-card--photo',
    'photo': 'post-card--photo',
  };
  return map[category] || 'post-card--essay';
}

function getCategoryLabel(category) {
  const map = {
    'poetry': '诗歌',
    'quote': '语录',
    'essay': '随笔',
    'music': '音乐',
    'film': '光影',
    'photo': '光影',
  };
  return map[category] || category || '随笔';
}

// 图片 base64 压缩
function compressImage(file) {
  return new Promise((resolve, reject) => {
    if (!file) { resolve(null); return; }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        // 等比缩放
        if (width > CONFIG.imageMaxWidth) {
          height = Math.round((height * CONFIG.imageMaxWidth) / width);
          width = CONFIG.imageMaxWidth;
        }
        if (height > CONFIG.imageMaxHeight) {
          width = Math.round((width * CONFIG.imageMaxHeight) / height);
          height = CONFIG.imageMaxHeight;
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        const dataURL = canvas.toDataURL('image/jpeg', CONFIG.imageQuality);
        resolve(dataURL);
      };
      img.onerror = () => reject(new Error('图片加载失败'));
      img.src = e.target.result;
    };
    reader.onerror = () => reject(new Error('文件读取失败'));
    reader.readAsDataURL(file);
  });
}

// 防抖
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流
function throttle(fn, interval) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= interval) {
      last = now;
      fn.apply(this, args);
    }
  };
}

// ═══════════════════════════════════════════════════════════
// 4. API 层 (async/await + fetch)
// ═══════════════════════════════════════════════════════════

let fingerprint = null;

async function apiGet(path) {
  const url = API_BASE + path + (path.includes('?') ? '&' : '?') + 'fingerprint=' + fingerprint;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/json' },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, body = {}) {
  const payload = { ...body, fingerprint: fingerprint };
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(API_BASE + path + '?fingerprint=' + fingerprint, {
    method: 'DELETE',
    headers: { 'Accept': 'application/json' },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

// -- 具体 API 方法 --

async function fetchDailyMessage() {
  return apiGet('/api/daily-message');
}

async function fetchPosts(page = 1) {
  return apiGet(`/api/posts?page=${page}`);
}

async function fetchCurated() {
  return apiGet('/api/posts/curated');
}

async function fetchRandomPost() {
  return apiGet('/api/posts/random');
}

async function createPost(data) {
  return apiPost('/api/post', data);
}

async function likePost(id) {
  return apiPost(`/api/post/${id}/like`);
}

async function hugPost(id) {
  return apiPost(`/api/post/${id}/hug`);
}

async function deletePost(id) {
  return apiDelete(`/api/post/${id}`);
}

async function fetchMyPosts() {
  return apiGet('/api/my-posts');
}

// ═══════════════════════════════════════════════════════════
// 5. 状态管理
// ═══════════════════════════════════════════════════════════

const state = {
  currentTab: 'stardust',   // stardust | curated | compose | mine
  stardust: {
    page: 1,
    hasMore: true,
    loading: false,
    posts: [],
  },
  curated: {
    categories: null,
  },
  mine: {
    posts: [],
  },
};

// ═══════════════════════════════════════════════════════════
// 6. 涟漪点击效果
// ═══════════════════════════════════════════════════════════

function createRipple(e, el) {
  const ripple = document.createElement('span');
  ripple.className = 'ripple';
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
  ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
  el.appendChild(ripple);

  ripple.addEventListener('animationend', () => {
    if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
  });
}

// ═══════════════════════════════════════════════════════════
// 7. 骨架屏
// ═══════════════════════════════════════════════════════════

function showSkeletons(container, count = CONFIG.skeletonCount) {
  container.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const sk = document.createElement('div');
    sk.className = 'skeleton-card';
    sk.innerHTML = `
      <div class="skeleton-line skeleton-line--title"></div>
      <div class="skeleton-line skeleton-line--body"></div>
      <div class="skeleton-line skeleton-line--body skeleton-line--short"></div>
      <div class="skeleton-line skeleton-line--meta"></div>
    `;
    container.appendChild(sk);
  }
}

function hideSkeletons(container) {
  container.innerHTML = '';
}

// ═══════════════════════════════════════════════════════════
// 8. 卡片渲染
// ═══════════════════════════════════════════════════════════

/**
 * 渲染单张卡片 HTML 结构:
 *   时间左上 + 情绪(mood)右上 + 正文 + 图片(可选) + 互动区
 */
function renderCard(post, index = 0) {
  const catClass = getCategoryClass(post.category);
  const modClass = getCardModifierClass(post.category);
  const catLabel = getCategoryLabel(post.category);

  // featured 变体: 每 6 张中的第 0 张
  const isFeatured = (index % CONFIG.featuredInterval === 0);
  const featuredClass = isFeatured ? 'post-card--featured' : '';
  const spansClass = isFeatured ? 'post-card--spans' : '';

  const timeStr = formatTime(post.created_at);
  const moodEmoji = post.mood_emoji || '';
  const moodColor = post.mood_color || 'rgba(201,160,69,0.6)';
  const moodLabel = post.mood || '';
  const contentHTML = escapeHTML(post.content || '').replace(/
/g, '<br>');
  const nickname = escapeHTML(post.nickname || '匿名星尘');

  const hasImage = post.image && post.image.trim().length > 0;
  const imageHTML = hasImage
    ? `<div class="post-card__image-wrap"><img class="post-card__image lazyload" data-src="${escapeHTML(post.image)}" alt="" loading="lazy" /></div>`
    : '';

  const likeActive = post.liked_by_me ? 'post-card__action--active' : '';
  const hugActive = post.hugged_by_me ? 'post-card__action--active' : '';

  // 精选标记
  const curatedBadge = post.is_curated
    ? '<span class="post-card__badge">✦ 精选</span>'
    : '';

  return `
    <article
      class="post-card ${modClass} ${catClass} ${featuredClass} ${spansClass}"
      data-id="${post.id}"
      data-category="${catLabel}"
    >
      ${curatedBadge}
      <div class="post-card__header">
        <span class="post-card__time">${timeStr}</span>
        <span class="post-card__mood" style="color:${moodColor}" title="${escapeHTML(moodLabel)}">
          ${moodEmoji}
        </span>
      </div>

      <div class="post-card__body">
        <div class="post-card__content">${contentHTML}</div>
        ${imageHTML}
      </div>

      <div class="post-card__meta">
        <span class="post-card__nickname">— ${nickname}</span>
        ${post.source ? `<span class="post-card__source">${escapeHTML(post.source)}</span>` : ''}
      </div>

      <div class="post-card__actions">
        <button class="post-card__action post-card__like ${likeActive}" data-action="like" data-id="${post.id}" aria-label="喜欢">
          <span class="post-card__action-icon">♡</span>
          <span class="post-card__action-count">${post.like_count || 0}</span>
        </button>
        <button class="post-card__action post-card__hug ${hugActive}" data-action="hug" data-id="${post.id}" aria-label="拥抱">
          <span class="post-card__action-icon">◉</span>
          <span class="post-card__action-count">${post.hug_count || 0}</span>
        </button>
      </div>
    </article>
  `;
}

/**
 * 渲染帖子列表到容器
 */
function renderFeed(container, posts, startIndex = 0, append = false) {
  if (!append) {
    container.innerHTML = '';
  }

  const fragment = document.createDocumentFragment();
  posts.forEach((post, i) => {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = renderCard(post, startIndex + i);
    fragment.appendChild(wrapper.firstElementChild);
  });

  container.appendChild(fragment);

  // 懒加载图片
  lazyLoadImages();
}

/**
 * 策展视图：按分类分组渲染
 */
function renderCurated(container, categoriesData) {
  if (!categoriesData) return;

  container.innerHTML = '';

  const categoryOrder = ['诗歌', '语录', '随笔', '音乐', '光影'];

  categoryOrder.forEach((catName) => {
    const posts = categoriesData[catName];
    if (!posts || posts.length === 0) return;

    const catKey = CONFIG.categoryMap[catName] || 'essay';
    const catClass = `cat-${catKey}`;

    const section = document.createElement('section');
    section.className = `curated-section ${catClass}`;
    section.innerHTML = `
      <h2 class="curated-section__title">
        <span class="curated-section__icon"></span>
        ${escapeHTML(catName)}
        <span class="curated-section__count">${posts.length}篇</span>
      </h2>
    `;

    const grid = document.createElement('div');
    grid.className = 'post-grid post-grid--curated';

    posts.forEach((post, i) => {
      const wrapper = document.createElement('div');
      wrapper.innerHTML = renderCard(post, i);
      grid.appendChild(wrapper.firstElementChild);
    });

    section.appendChild(grid);
    container.appendChild(section);
  });

  lazyLoadImages();
}

/**
 * 我的帖子列表渲染（含删除按钮）
 */
function renderMyPosts(container, posts) {
  if (!posts || posts.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state__icon">◈</div>
        <p class="empty-state__text">你还没有发布过帖子</p>
        <p class="empty-state__sub">在星尘中留下你的痕迹吧</p>
      </div>
    `;
    return;
  }

  container.innerHTML = '';

  posts.forEach((post, i) => {
    const catClass = getCategoryClass(post.category);
    const modClass = getCardModifierClass(post.category);
    const timeStr = formatTime(post.created_at);
    const moodEmoji = post.mood_emoji || '';
    const moodColor = post.mood_color || 'rgba(201,160,69,0.6)';
    const contentHTML = escapeHTML(post.content || '').replace(/
/g, '<br>');
    const hasImage = post.image && post.image.trim().length > 0;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <article class="post-card ${modClass} ${catClass}" data-id="${post.id}">
        <div class="post-card__header">
          <span class="post-card__time">${timeStr}</span>
          <span class="post-card__mood" style="color:${moodColor}">${moodEmoji}</span>
        </div>
        <div class="post-card__body">
          <div class="post-card__content">${contentHTML}</div>
          ${hasImage ? `<div class="post-card__image-wrap"><img class="post-card__image lazyload" data-src="${escapeHTML(post.image)}" alt="" loading="lazy" /></div>` : ''}
        </div>
        <div class="post-card__actions">
          <span class="post-card__stat">♡ ${post.like_count || 0}</span>
          <span class="post-card__stat">◉ ${post.hug_count || 0}</span>
          <button class="post-card__delete-btn" data-action="delete" data-id="${post.id}" aria-label="删除">
            ✕ 删除
          </button>
        </div>
      </article>
    `;
    container.appendChild(wrapper.firstElementChild);
  });

  lazyLoadImages();
}

// ═══════════════════════════════════════════════════════════
// 9. 图片懒加载
// ═══════════════════════════════════════════════════════════

function lazyLoadImages() {
  const images = document.querySelectorAll('img.lazyload[data-src]');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazyload');
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '100px' });

    images.forEach((img) => observer.observe(img));
  } else {
    // 降级：直接加载
    images.forEach((img) => {
      img.src = img.dataset.src;
      img.classList.remove('lazyload');
    });
  }
}

// ═══════════════════════════════════════════════════════════
// 10. 星尘流 (Tab 1): 首屏加载 + 无限滚动
// ═══════════════════════════════════════════════════════════

async function loadStardust(append = false) {
  const container = document.getElementById('stardust-feed');
  if (!container) return;

  if (!append) {
    state.stardust.page = 1;
    state.stardust.hasMore = true;
    state.stardust.posts = [];
    showSkeletons(container);
  }

  if (state.stardust.loading || !state.stardust.hasMore) return;

  state.stardust.loading = true;

  try {
    const data = await fetchPosts(state.stardust.page);

    if (!append) {
      hideSkeletons(container);
    }

    const posts = data.posts || [];
    state.stardust.hasMore = data.has_more !== false;
    state.stardust.page = data.page || state.stardust.page;

    if (posts.length > 0) {
      state.stardust.posts = append
        ? [...state.stardust.posts, ...posts]
        : posts;
      renderFeed(container, posts, state.stardust.posts.length - posts.length, append);
    } else if (!append) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">✦</div>
          <p class="empty-state__text">暂无星尘</p>
          <p class="empty-state__sub">成为第一个留下光芒的人</p>
        </div>
      `;
    }

    // 没有更多内容时追加提示
    if (!state.stardust.hasMore && state.stardust.posts.length > 0) {
      const end = document.createElement('div');
      end.className = 'feed-end';
      end.innerHTML = '<span>— 已到达星尘尽头 —</span>';
      container.appendChild(end);
    }

  } catch (err) {
    if (!append) hideSkeletons(container);
    showToast('加载失败: ' + err.message, 'error');
  } finally {
    state.stardust.loading = false;
  }
}

// 无限滚动处理
const handleScroll = throttle(() => {
  if (state.currentTab !== 'stardust') return;
  if (!state.stardust.hasMore || state.stardust.loading) return;

  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const windowHeight = window.innerHeight;
  const docHeight = document.documentElement.scrollHeight;

  if (scrollTop + windowHeight >= docHeight - CONFIG.scrollThreshold) {
    state.stardust.page++;
    loadStardust(true);
  }
}, 200);

// ═══════════════════════════════════════════════════════════
// 11. 策展 (Tab 2): 分类分组展示
// ═══════════════════════════════════════════════════════════

async function loadCurated() {
  const container = document.getElementById('curated-feed');
  if (!container) return;

  showSkeletons(container, 4);

  try {
    const data = await fetchCurated();
    hideSkeletons(container);

    state.curated.categories = data.categories || data;
    renderCurated(container, state.curated.categories);

    if (!state.curated.categories || Object.keys(state.curated.categories).length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">✦</div>
          <p class="empty-state__text">暂无策展内容</p>
          <p class="empty-state__sub">编辑正在精心挑选中...</p>
        </div>
      `;
    }
  } catch (err) {
    hideSkeletons(container);
    showToast('策展加载失败: ' + err.message, 'error');
  }
}

// ═══════════════════════════════════════════════════════════
// 12. 书写 (Tab 3): 发布表单
// ═══════════════════════════════════════════════════════════

function initComposeForm() {
  const form = document.getElementById('compose-form');
  const contentInput = document.getElementById('compose-content');
  const charCount = document.getElementById('compose-charcount');
  const moodSelector = document.getElementById('compose-mood-selector');
  const imageInput = document.getElementById('compose-image');
  const imagePreview = document.getElementById('compose-image-preview');
  const submitBtn = document.getElementById('compose-submit');
  const nicknameInput = document.getElementById('compose-nickname');

  if (!form) return;

  // 字数统计
  if (contentInput && charCount) {
    contentInput.addEventListener('input', () => {
      const len = contentInput.value.length;
      charCount.textContent = `${len} / ${CONFIG.contentMaxLen}`;
      charCount.className = len > CONFIG.contentMaxLen
        ? 'compose__charcount compose__charcount--over'
        : 'compose__charcount';
    });
  }

  // 情绪选择器构建
  if (moodSelector) {
    CONFIG.moods.forEach((mood) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'mood-btn';
      btn.dataset.mood = mood.id;
      btn.dataset.emoji = mood.emoji;
      btn.dataset.color = mood.color;
      btn.innerHTML = `<span class="mood-btn__emoji">${mood.emoji}</span><span class="mood-btn__label">${mood.label}</span>`;
      btn.addEventListener('click', () => {
        moodSelector.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('mood-btn--selected'));
        btn.classList.add('mood-btn--selected');
      });
      moodSelector.appendChild(btn);
    });
    // 默认选中第一个
    const firstBtn = moodSelector.querySelector('.mood-btn');
    if (firstBtn) firstBtn.classList.add('mood-btn--selected');
  }

  // 图片预览
  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', async () => {
      const file = imageInput.files[0];
      if (!file) { imagePreview.innerHTML = ''; return; }

      if (!file.type.startsWith('image/')) {
        showToast('请选择图片文件', 'error');
        imageInput.value = '';
        return;
      }

      imagePreview.innerHTML = '<div class="compose__image-loading">压缩中...</div>';

      try {
        const dataURL = await compressImage(file);
        imagePreview.innerHTML = `<img src="${dataURL}" alt="预览" class="compose__image-thumb" />`;
        // 存储 base64 到 data 属性供提交时使用
        imagePreview.dataset.base64 = dataURL;
      } catch (err) {
        imagePreview.innerHTML = '';
        showToast('图片处理失败', 'error');
      }
    });
  }

  // 提交
  if (submitBtn) {
    submitBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      await handlePublish();
    });
  }

  // Enter 提交 (Ctrl+Enter)
  if (contentInput) {
    contentInput.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handlePublish();
      }
    });
  }
}

async function handlePublish() {
  const contentInput = document.getElementById('compose-content');
  const moodSelector = document.getElementById('compose-mood-selector');
  const imagePreview = document.getElementById('compose-image-preview');
  const submitBtn = document.getElementById('compose-submit');
  const nicknameInput = document.getElementById('compose-nickname');

  const content = (contentInput?.value || '').trim();
  if (!content) {
    showToast('请写下你想说的话', 'error');
    contentInput?.focus();
    return;
  }

  if (content.length > CONFIG.contentMaxLen) {
    showToast(`内容不能超过${CONFIG.contentMaxLen}字`, 'error');
    return;
  }

  // 获取选中的情绪
  const selectedMood = moodSelector?.querySelector('.mood-btn--selected');
  const mood = selectedMood?.dataset.mood || 'calm';
  const moodEmoji = selectedMood?.dataset.emoji || '🌙';
  const moodColor = selectedMood?.dataset.color || '#7eb8da';

  // 获取图片 base64
  const image = imagePreview?.dataset.base64 || null;

  // 昵称
  const nickname = (nicknameInput?.value || '').trim().slice(0, CONFIG.nicknameMaxLen) || '匿名星尘';

  // 禁用按钮
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = '发送中...';
  }

  try {
    const result = await createPost({
      content,
      image,
      mood,
      nickname,
    });

    showToast('发布成功 ✦', 'success');

    // 清空表单
    if (contentInput) contentInput.value = '';
    if (charCount) document.getElementById('compose-charcount').textContent = `0 / ${CONFIG.contentMaxLen}`;
    if (imagePreview) { imagePreview.innerHTML = ''; delete imagePreview.dataset.base64; }
    if (imageInput) document.getElementById('compose-image').value = '';

    // 重置情绪选择
    if (moodSelector) {
      moodSelector.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('mood-btn--selected'));
      const firstBtn = moodSelector.querySelector('.mood-btn');
      if (firstBtn) firstBtn.classList.add('mood-btn--selected');
    }

    // 如果 result 中有 post 对象，可以插入到 feed
    if (result.post) {
      // 切换到星尘 tab 并刷新
      const stardustTab = document.querySelector('[data-tab="stardust"]');
      if (stardustTab) stardustTab.click();
    }

  } catch (err) {
    showToast('发布失败: ' + err.message, 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = '✦ 发布星尘';
    }
  }
}

// ═══════════════════════════════════════════════════════════
// 13. 我的 (Tab 4): 帖子列表 + 删除
// ═══════════════════════════════════════════════════════════

async function loadMyPosts() {
  const container = document.getElementById('mine-feed');
  if (!container) return;

  showSkeletons(container, 3);

  try {
    const data = await fetchMyPosts();
    hideSkeletons(container);

    state.mine.posts = data.posts || [];
    renderMyPosts(container, state.mine.posts);
  } catch (err) {
    hideSkeletons(container);
    showToast('加载失败: ' + err.message, 'error');
  }
}

async function handleDelete(postId) {
  if (!confirm('确定要删除这篇帖子吗？此操作不可撤销。')) return;

  try {
    await deletePost(postId);
    showToast('已删除', 'success');

    // 从状态中移除
    state.mine.posts = state.mine.posts.filter(p => String(p.id) !== String(postId));

    // 重新渲染我的帖子列表
    const container = document.getElementById('mine-feed');
    if (container) {
      renderMyPosts(container, state.mine.posts);
    }
  } catch (err) {
    showToast('删除失败: ' + err.message, 'error');
  }
}

// ═══════════════════════════════════════════════════════════
// 14. Like / Hug 互动
// ═══════════════════════════════════════════════════════════

async function handleLike(postId, button) {
  try {
    const result = await likePost(postId);

    // 更新按钮状态
    const isActive = result.action === 'liked';
    button.classList.toggle('post-card__action--active', isActive);

    // 更新计数
    const countEl = button.querySelector('.post-card__action-count');
    if (countEl) {
      countEl.textContent = result.like_count || 0;
    }

    // 更新图标
    const iconEl = button.querySelector('.post-card__action-icon');
    if (iconEl) {
      iconEl.textContent = isActive ? '♥' : '♡';
    }

    // 小动画
    button.classList.add('post-card__action--pop');
    setTimeout(() => button.classList.remove('post-card__action--pop'), 300);

  } catch (err) {
    showToast('操作失败: ' + err.message, 'error');
  }
}

async function handleHug(postId, button) {
  try {
    const result = await hugPost(postId);

    // 更新按钮状态
    const isActive = result.action === 'hugged';
    button.classList.toggle('post-card__action--active', isActive);

    // 更新计数
    const countEl = button.querySelector('.post-card__action-count');
    if (countEl) {
      countEl.textContent = result.hug_count || 0;
    }

    // 更新图标
    const iconEl = button.querySelector('.post-card__action-icon');
    if (iconEl) {
      iconEl.textContent = isActive ? '◎' : '◉';
    }

    // 小动画
    button.classList.add('post-card__action--pop');
    setTimeout(() => button.classList.remove('post-card__action--pop'), 300);

  } catch (err) {
    showToast('操作失败: ' + err.message, 'error');
  }
}

// ═══════════════════════════════════════════════════════════
// 15. 漂流瓶 (随机帖子弹窗)
// ═══════════════════════════════════════════════════════════

async function openBottle() {
  const overlay = document.getElementById('bottle-overlay');
  const card = document.getElementById('bottle-card');
  const loading = document.getElementById('bottle-loading');
  const errorEl = document.getElementById('bottle-error');

  if (!overlay || !card) return;

  // 显示弹窗
  overlay.classList.add('bottle-overlay--visible');
  card.classList.remove('bottle-card--loaded', 'bottle-card--error');
  card.classList.add('bottle-card--loading');
  if (loading) loading.style.display = 'flex';
  if (errorEl) errorEl.style.display = 'none';

  // 卡片内容区
  const contentArea = card.querySelector('.bottle-card__content');
  if (contentArea) contentArea.innerHTML = '';

  try {
    const post = await fetchRandomPost();

    if (!post || !post.id) {
      throw new Error('empty');
    }

    // 渲染卡片
    if (contentArea) {
      const wrapper = document.createElement('div');
      wrapper.innerHTML = renderCard(post, 0);
      // 给漂流瓶卡片里的按钮加特殊class以便事件处理
      const cardEl = wrapper.firstElementChild;
      cardEl.classList.add('bottle-card__post');
      contentArea.appendChild(cardEl);
    }

    card.classList.remove('bottle-card--loading');
    card.classList.add('bottle-card--loaded');
    if (loading) loading.style.display = 'none';

    lazyLoadImages();

  } catch (err) {
    card.classList.remove('bottle-card--loading');
    card.classList.add('bottle-card--error');
    if (loading) loading.style.display = 'none';
    if (errorEl) errorEl.style.display = 'flex';

    if (err.message === 'empty' || err.message.includes('404')) {
      if (errorEl) errorEl.querySelector('.bottle-error__text').textContent = '这片海域暂无漂流瓶';
    } else {
      showToast('漂流瓶漂远了: ' + err.message, 'error');
    }
  }
}

function closeBottle() {
  const overlay = document.getElementById('bottle-overlay');
  const card = document.getElementById('bottle-card');

  if (overlay) overlay.classList.remove('bottle-overlay--visible');
  if (card) {
    card.classList.remove('bottle-card--loaded', 'bottle-card--error', 'bottle-card--loading');
  }
}

function initBottle() {
  const trigger = document.getElementById('bottle-trigger');
  const close = document.getElementById('bottle-close');
  const overlay = document.getElementById('bottle-overlay');
  const another = document.getElementById('bottle-another');

  if (trigger) {
    trigger.addEventListener('click', (e) => {
      createRipple(e, trigger);
      openBottle();
    });
  }

  if (close) {
    close.addEventListener('click', () => closeBottle());
  }

  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeBottle();
    });
  }

  if (another) {
    another.addEventListener('click', () => openBottle());
  }

  // ESC 关闭
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeBottle();
  });
}

// ═══════════════════════════════════════════════════════════
// 16. 每日星语
// ═══════════════════════════════════════════════════════════

async function loadDailyMessage() {
  const el = document.getElementById('daily-message');
  if (!el) return;

  try {
    const data = await fetchDailyMessage();
    el.innerHTML = `
      <p class="daily-message__text">${escapeHTML(data.message || '')}</p>
      ${data.author ? `<span class="daily-message__author">— ${escapeHTML(data.author)}</span>` : ''}
      ${data.source ? `<span class="daily-message__source">${escapeHTML(data.source)}</span>` : ''}
    `;
  } catch (err) {
    el.innerHTML = `
      <p class="daily-message__text">每一颗星都有自己的轨道，每束光都有自己的远方。</p>
      <span class="daily-message__author">— 唯一</span>
    `;
    // 静默失败，不弹 toast
  }
}

// ═══════════════════════════════════════════════════════════
// 17. Tab 切换
// ═══════════════════════════════════════════════════════════

function switchTab(tabName) {
  if (state.currentTab === tabName) return;

  state.currentTab = tabName;

  // 更新 nav 高亮
  document.querySelectorAll('.nav__item').forEach(item => {
    item.classList.toggle('nav__item--active', item.dataset.tab === tabName);
  });

  // 切换视图
  document.querySelectorAll('.view').forEach(view => {
    view.classList.toggle('view--active', view.dataset.view === tabName);
  });

  // 加载对应内容
  switch (tabName) {
    case 'stardust':
      if (state.stardust.posts.length === 0) {
        loadStardust(false);
      }
      break;
    case 'curated':
      if (!state.curated.categories) {
        loadCurated();
      }
      break;
    case 'compose':
      // 无需异步加载
      break;
    case 'mine':
      if (state.mine.posts.length === 0) {
        loadMyPosts();
      }
      break;
  }

  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function initTabs() {
  document.querySelectorAll('.nav__item').forEach(item => {
    item.addEventListener('click', (e) => {
      createRipple(e, item);
      const tab = item.dataset.tab;
      if (tab) switchTab(tab);
    });
  });
}

// ═══════════════════════════════════════════════════════════
// 18. 全局事件委托 (卡片互动、删除等)
// ═══════════════════════════════════════════════════════════

function initGlobalDelegation() {
  document.addEventListener('click', async (e) => {
    // Like 按钮
    const likeBtn = e.target.closest('[data-action="like"]');
    if (likeBtn) {
      e.preventDefault();
      const postId = likeBtn.dataset.id;
      if (postId) {
        createRipple(e, likeBtn);
        await handleLike(postId, likeBtn);
      }
      return;
    }

    // Hug 按钮
    const hugBtn = e.target.closest('[data-action="hug"]');
    if (hugBtn) {
      e.preventDefault();
      const postId = hugBtn.dataset.id;
      if (postId) {
        createRipple(e, hugBtn);
        await handleHug(postId, hugBtn);
      }
      return;
    }

    // Delete 按钮
    const deleteBtn = e.target.closest('[data-action="delete"]');
    if (deleteBtn) {
      e.preventDefault();
      const postId = deleteBtn.dataset.id;
      if (postId) {
        await handleDelete(postId);
      }
      return;
    }
  });
}

// ═══════════════════════════════════════════════════════════
// 19. 星空背景初始化 (纯CSS，无Canvas)
// ═══════════════════════════════════════════════════════════

function initStarfield() {
  const bg = document.getElementById('starfield-bg');
  if (!bg) return;

  // 通过 JS 动态生成若干星星元素，注入到背景容器中
  // CSS 将处理动画和位置
  const starCount = 120;
  const fragment = document.createDocumentFragment();

  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.setProperty('--star-x', Math.random());
    star.style.setProperty('--star-y', Math.random());
    star.style.setProperty('--star-size', (Math.random() * 3 + 1).toFixed(2) + 'px');
    star.style.setProperty('--star-opacity', (Math.random() * 0.6 + 0.2).toFixed(2));
    star.style.setProperty('--star-delay', (Math.random() * 5).toFixed(2) + 's');
    star.style.setProperty('--star-duration', (Math.random() * 4 + 3).toFixed(2) + 's');
    fragment.appendChild(star);
  }

  bg.appendChild(fragment);
}

// ═══════════════════════════════════════════════════════════
// 20. 应用初始化
// ═══════════════════════════════════════════════════════════

async function initApp() {
  try {
    // 1. 获取/生成浏览器指纹
    fingerprint = await getOrCreateFingerprint();

    // 2. 初始化星空背景
    initStarfield();

    // 3. 初始化 Tab 切换
    initTabs();

    // 4. 初始化书写表单
    initComposeForm();

    // 5. 初始化漂流瓶
    initBottle();

    // 6. 全局事件委托
    initGlobalDelegation();

    // 7. 无限滚动
    window.addEventListener('scroll', handleScroll, { passive: true });

    // 8. 加载每日星语
    loadDailyMessage();

    // 9. 加载首屏星尘流（默认tab）
    await loadStardust(false);

  } catch (err) {
    console.error('App init error:', err);
    showToast('初始化失败，请刷新页面', 'error');
  }
}

// ═══════════════════════════════════════════════════════════
// 启动
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', initApp);

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
