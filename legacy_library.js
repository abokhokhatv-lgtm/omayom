// library.js
// يعرض الكتب المخزنة في localStorage أو الكتب الافتراضية في صفحة المكتبة

document.addEventListener('DOMContentLoaded', () => {
  // عرض الكتب
  const booksContainer = document.getElementById('books-list');
  let books = [];
  try {
    books = JSON.parse(localStorage.getItem('books') || '[]');
  } catch (e) {
    books = [];
  }
  if (!books || books.length === 0) {
    booksContainer.innerHTML = '<p>لا توجد كتب حاليا.</p>';
  } else {
    books.forEach((book) => {
      const card = document.createElement('div');
      card.className = 'book-card';
      const title = document.createElement('h4');
      title.textContent = book.title;
      card.appendChild(title);
      const desc = document.createElement('p');
      desc.textContent = book.description || '';
      card.appendChild(desc);
      if (book.link) {
        const button = document.createElement('a');
        button.href = book.link;
        button.target = '_blank';
        button.className = 'btn-secondary';
        button.textContent = 'تحميل الكتاب';
        card.appendChild(button);
      }
      booksContainer.appendChild(card);
    });
  }
  // عرض المخطوطات
  const manuscriptsContainer = document.getElementById('manuscripts-list');
  let customManuscripts = [];
  try {
    customManuscripts = JSON.parse(localStorage.getItem('manuscripts') || '[]');
  } catch (e) {
    customManuscripts = [];
  }
  // رابط مخطوطات افتراضي
  const defaultManuscripts = [
    {
      id: 'default',
      title: 'المخطوطات',
      description: 'للاطلاع على جميع المخطوطات المتوفرة، اضغط على الرابط.',
      link: 'https://drive.google.com/drive/folders/19DKYkhGpq22OLOdYAZO8mwrsGLPlXLTF',
    },
  ];
  const allManuscripts = defaultManuscripts.concat(customManuscripts);
  if (!allManuscripts || allManuscripts.length === 0) {
    manuscriptsContainer.innerHTML = '<p>لا توجد مخطوطات حاليا.</p>';
  } else {
    allManuscripts.forEach((m) => {
      const card = document.createElement('div');
      card.className = 'book-card';
      const title = document.createElement('h4');
      title.textContent = m.title;
      card.appendChild(title);
      const desc = document.createElement('p');
      desc.textContent = m.description || '';
      card.appendChild(desc);
      if (m.link) {
        const button = document.createElement('a');
        button.href = m.link;
        button.target = '_blank';
        button.className = 'btn-secondary';
        // إذا كانت المخطوطة الافتراضية، استخدم نص مختلف
        button.textContent = m.id === 'default' ? 'فتح الرابط' : 'عرض المخطوطة';
        card.appendChild(button);
      }
      manuscriptsContainer.appendChild(card);
    });
  }
});