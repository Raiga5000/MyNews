export let articles = [];

const colors = { it:['#e0f0ff','#136388'], security:['#e8e6f7','#3f3f8f'], network:['#dcf1f3','#10606b'], yokohama:['#dff4ed','#19745a'], outing:['#fff0d9','#9a5810'], top:['#ffe4e2','#b0453d'] };
const labels = { all:'すべてのニュース', it:'IT関連ニュース', security:'セキュリティ', network:'通信技術', yokohama:'横浜イベント', outing:'おでかけ', top:'トップニュース' };
export function filterAndSort(items, category, sort) {
  const filtered = category === 'all' ? items : items.filter(item => item.category === category);
  const limited = category === 'all'
    ? Object.values(filtered.reduce((groups, item) => {
      (groups[item.category] ||= []).push(item);
      return groups;
    }, {})).flatMap(group => group.slice(0, 5))
    : filtered.slice(0, 5);
  return [...limited].sort((a, b) => sort === 'recommended'
    ? (b.score || 0) - (a.score || 0)
    : new Date(b.publishedAt || 0) - new Date(a.publishedAt || 0));
}
function escapeHtml(value) { const element = document.createElement('div'); element.textContent = value; return element.innerHTML; }
function card(article) { const [bg, color] = colors[article.category]; const title = escapeHtml(article.title); const summary = escapeHtml(article.summary || ''); const url = encodeURI(article.url); return `<article class="news-card"><div class="news-meta"><span class="tag" style="--tag-bg:${bg};--tag-color:${color}">${escapeHtml(article.label)}</span><time class="time">取得 ${escapeHtml(article.time)}</time></div><div><h2 class="news-title">${title}</h2><p class="news-summary">${summary}</p><a class="source-link" href="${url}" target="_blank" rel="noopener noreferrer" aria-label="${title}の元記事を別タブで開く">元記事を読む <span aria-hidden="true">↗</span></a></div><div class="rating">おすすめ度<strong>${article.score}<small> / 100</small></strong><div class="rating-meter"><span style="--score:${article.score}%"></span></div></div></article>`; }
let category = 'all'; let sort = 'newest';
function render() { const visible = filterAndSort(articles, category, sort); document.querySelector('#news-list').innerHTML = visible.map(card).join(''); document.querySelector('#result-label').textContent = labels[category]; document.querySelector('#result-count').textContent = `${visible.length} ARTICLES`; document.querySelector('#empty-state').hidden = visible.length !== 0; document.querySelector('#article-total').textContent = `${articles.length}件を表示中`; }
async function loadNews() { try { const response = await fetch(`data/news.json?updated=${Date.now()}`); if (!response.ok) throw new Error('ニュースデータを取得できませんでした'); const data = await response.json(); articles = data.articles || []; const updated = data.updatedAt ? new Date(data.updatedAt) : null; if (updated) document.querySelector('.update-status span:nth-child(2)').textContent = `最終更新: ${new Intl.DateTimeFormat('ja-JP', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' }).format(updated)}`; } catch { articles = []; } render(); }
function initialize() { const now = new Intl.DateTimeFormat('ja-JP', { year:'numeric', month:'long', day:'numeric', weekday:'short' }).format(new Date()); document.querySelector('#today').textContent = now; document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => { category = button.dataset.category; document.querySelectorAll('.filter').forEach(item => item.classList.toggle('active', item === button)); render(); })); document.querySelectorAll('.sort').forEach(button => button.addEventListener('click', () => { sort = button.dataset.sort; document.querySelectorAll('.sort').forEach(item => item.classList.toggle('active', item === button)); render(); })); loadNews(); }
if (typeof document !== 'undefined') initialize();
