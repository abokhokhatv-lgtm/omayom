// blog.js
// يتولى عرض المقالات المخزنة في localStorage داخل صفحة المدونة

document.addEventListener('DOMContentLoaded', () => {
  const postsContainer = document.getElementById('posts-list');
  let posts = [];
  try {
    posts = JSON.parse(localStorage.getItem('posts') || '[]');
  } catch (e) {
    posts = [];
  }
  if (!posts || posts.length === 0) {
    postsContainer.innerHTML = '<p>لا توجد مقالات حاليا.</p>';
    return;
  }
  // ترتيب المقالات حسب التاريخ (الأحدث أولاً)
  posts.sort((a, b) => {
    const da = new Date(a.createdAt || a.date || 0);
    const db = new Date(b.createdAt || b.date || 0);
    return db - da;
  });
  posts.forEach((post) => {
    const card = document.createElement('article');
    card.className = 'post-card';
    const title = document.createElement('h3');
    title.textContent = post.title;
    card.appendChild(title);
    const dateEl = document.createElement('small');
    dateEl.className = 'post-date';
    // عرض التاريخ بصيغة محلية إذا توفر
    let dateStr = '';
    if (post.date) {
      dateStr = post.date;
    } else if (post.createdAt) {
      try {
        const d = new Date(post.createdAt);
        dateStr = d.toLocaleDateString('ar-EG');
      } catch (e) {
        dateStr = post.createdAt;
      }
    }
    dateEl.textContent = dateStr;
    card.appendChild(dateEl);
    const content = document.createElement('p');
    content.className = 'post-content';
    content.textContent = post.content;
    card.appendChild(content);
    postsContainer.appendChild(card);
  });
});