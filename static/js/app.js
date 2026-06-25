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
