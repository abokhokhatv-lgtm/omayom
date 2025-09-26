// admin.js
// هذا الملف يتحكم في لوحة الإدارة: إضافة مستخدمين، تحديثهم، وتغيير بيانات الإدمن.

document.addEventListener('DOMContentLoaded', () => {
  // تحقق من تسجيل الدخول كإدمن، وإلا أعد التوجيه إلى صفحة الدخول
  const loggedIn = JSON.parse(sessionStorage.getItem('loggedInUser') || 'null');
  if (!loggedIn || loggedIn.role !== 'admin') {
    // إذا لم يكن المستخدم مسجلًا كإدمن، أعد التوجيه
    window.location.href = 'login.html';
    return;
  }

  // عرض المستخدمين الحاليين
  renderUsersTable();

  // ربط نماذج المقالات والكتب إذا كانت العناصر موجودة
  renderPostsTable();
  renderBooksTable();

  // رسم جدول الدروس الحالية
  renderLessonsTable();

  // رسم جدول المخطوطات الحالية
  renderManuscriptsTable();

  const addPostForm = document.getElementById('add-post-form');
  if (addPostForm) {
    addPostForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('post-title').value.trim();
      const content = document.getElementById('post-content').value.trim();
      if (!title || !content) return;
      let posts = [];
      try {
        posts = JSON.parse(localStorage.getItem('posts') || '[]');
      } catch (e) {
        posts = [];
      }
      const newPost = {
        id: Date.now(),
        title,
        content,
        createdAt: new Date().toISOString(),
      };
      posts.push(newPost);
      localStorage.setItem('posts', JSON.stringify(posts));
      document.getElementById('add-post-msg').textContent = 'تم نشر المقالة بنجاح.';
      addPostForm.reset();
      renderPostsTable();
    });
  }

  const addBookForm = document.getElementById('add-book-form');
  if (addBookForm) {
    addBookForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('book-title').value.trim();
      const description = document.getElementById('book-description').value.trim();
      const link = document.getElementById('book-link').value.trim();
      if (!title || !link) return;
      let books = [];
      try {
        books = JSON.parse(localStorage.getItem('books') || '[]');
      } catch (e) {
        books = [];
      }
      const newBook = {
        id: Date.now(),
        title,
        description,
        link,
      };
      books.push(newBook);
      localStorage.setItem('books', JSON.stringify(books));
      document.getElementById('add-book-msg').textContent = 'تم إضافة الكتاب بنجاح.';
      addBookForm.reset();
      renderBooksTable();
    });
  }

  // ربط نموذج إضافة درس جديد
  const addLessonForm = document.getElementById('add-lesson-form');
  if (addLessonForm) {
    addLessonForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('lesson-title').value.trim();
      const rawUrl = document.getElementById('lesson-url').value.trim();
      const free = document.getElementById('lesson-free').checked;
      if (!title || !rawUrl) return;
      // قراءة الدروس الحالية
      let lessons = [];
      try {
        lessons = JSON.parse(localStorage.getItem('lessons') || '[]');
      } catch (e) {
        lessons = [];
      }
      // إنشاء درس جديد
      const newLesson = {
        id: Date.now(),
        title,
        url: parseEmbedURL(rawUrl),
        rawUrl,
        free
      };
      lessons.push(newLesson);
      localStorage.setItem('lessons', JSON.stringify(lessons));
      document.getElementById('add-lesson-msg').textContent = 'تم إضافة الدرس بنجاح.';
      addLessonForm.reset();
      renderLessonsTable();
    });
  }

  // ربط نموذج إضافة مخطوطة جديدة
  const addManuscriptForm = document.getElementById('add-manuscript-form');
  if (addManuscriptForm) {
    addManuscriptForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('manuscript-title').value.trim();
      const description = document
        .getElementById('manuscript-description')
        .value.trim();
      const link = document.getElementById('manuscript-link').value.trim();
      if (!title || !link) return;
      let manuscripts = [];
      try {
        manuscripts = JSON.parse(localStorage.getItem('manuscripts') || '[]');
      } catch (e) {
        manuscripts = [];
      }
      const newManuscript = {
        id: Date.now(),
        title,
        description,
        link,
      };
      manuscripts.push(newManuscript);
      localStorage.setItem('manuscripts', JSON.stringify(manuscripts));
      document.getElementById('add-manuscript-msg').textContent =
        'تم إضافة المخطوطة بنجاح.';
      addManuscriptForm.reset();
      renderManuscriptsTable();
    });
  }

  // ربط نموذج إضافة مستخدم جديد
  const addUserForm = document.getElementById('add-user-form');
  addUserForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('new-username').value.trim();
    const password = document.getElementById('new-password').value;
    const expiry = document.getElementById('new-expiry').value;
    let users = JSON.parse(localStorage.getItem('users') || '[]');
    // تحقق من عدم وجود مستخدم بنفس الاسم
    if (users.some((u) => u.username === username)) {
      document.getElementById('add-user-msg').textContent =
        'يوجد مستخدم بهذا الاسم بالفعل.';
      return;
    }
    users.push({ username, password, expiry, role: 'user' });
    localStorage.setItem('users', JSON.stringify(users));
    document.getElementById('add-user-msg').textContent =
      'تم إضافة المستخدم بنجاح.';
    addUserForm.reset();
    renderUsersTable();
  });

  // ربط نموذج تعديل بيانات الإدمن
  const adminChangeForm = document.getElementById('admin-change-form');
  adminChangeForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const newUsername = document
      .getElementById('admin-new-username')
      .value.trim();
    const newPassword = document.getElementById('admin-new-password').value;
    let users = JSON.parse(localStorage.getItem('users') || '[]');
    // ابحث عن الإدمن الحالي
    const adminIndex = users.findIndex((u) => u.role === 'admin');
    if (adminIndex === -1) {
      // إذا لم يوجد إدمن، أضفه
      users.push({ username: newUsername, password: newPassword, role: 'admin' });
    } else {
      users[adminIndex].username = newUsername;
      users[adminIndex].password = newPassword;
    }
    localStorage.setItem('users', JSON.stringify(users));
    document.getElementById('admin-update-msg').textContent =
      'تم تحديث بيانات الأدمن بنجاح.';
    // تحديث الجلسة إذا كانت الجلسة الحالية للإدمن
    sessionStorage.setItem(
      'loggedInUser',
      JSON.stringify({ username: newUsername, role: 'admin' })
    );
    renderUsersTable();
  });

  // تسجيل الخروج
  document.getElementById('logout-link').addEventListener('click', (e) => {
    e.preventDefault();
    sessionStorage.removeItem('loggedInUser');
    window.location.href = 'login.html';
  });
});

// تحويل رابط الفيديو إلى رابط مضمّن يمكن عرضه في iframe
function parseEmbedURL(input) {
  try {
    const urlStr = input.trim();
    const url = new URL(urlStr);
    const host = url.hostname.replace('www.', '');
    // YouTube الحالات
    if (host.includes('youtube.com')) {
      // قائمة تشغيل
      if (url.searchParams.get('list')) {
        const listId = url.searchParams.get('list');
        return `https://www.youtube.com/embed/videoseries?list=${listId}`;
      }
      // watch?v=
      const v = url.searchParams.get('v');
      if (v) {
        return `https://www.youtube.com/embed/${v}`;
      }
      // /embed/VIDEO
      const parts = url.pathname.split('/').filter(Boolean);
      const idx = parts.indexOf('embed');
      if (idx >= 0 && parts[idx + 1]) {
        return `https://www.youtube.com/embed/${parts[idx + 1]}`;
      }
    }
    // youtu.be
    if (host === 'youtu.be') {
      const id = url.pathname.substring(1);
      if (id) {
        return `https://www.youtube.com/embed/${id}`;
      }
    }
    // Vimeo
    if (host.includes('vimeo.com')) {
      const segments = url.pathname.split('/').filter(Boolean);
      const id = segments.pop();
      if (id) {
        return `https://player.vimeo.com/video/${id}`;
      }
    }
    // غير ذلك، أعد الرابط كما هو
    return urlStr;
  } catch (err) {
    return input;
  }
}

// تحميل الدروس من localStorage
function loadLessons() {
  try {
    return JSON.parse(localStorage.getItem('lessons') || '[]');
  } catch (e) {
    return [];
  }
}

// حفظ الدروس إلى localStorage
function saveLessons(list) {
  localStorage.setItem('lessons', JSON.stringify(list));
}

// رسم جدول الدروس الحالية في لوحة التحكم
function renderLessonsTable() {
  const table = document.getElementById('lessons-table');
  if (!table) return;
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  let lessons = loadLessons();
  lessons.forEach((lesson) => {
    const tr = document.createElement('tr');
    // العنوان
    const titleTd = document.createElement('td');
    titleTd.textContent = lesson.title;
    tr.appendChild(titleTd);
    // مجاني
    const freeTd = document.createElement('td');
    freeTd.textContent = lesson.free ? 'نعم' : 'لا';
    tr.appendChild(freeTd);
    // الرابط
    const linkTd = document.createElement('td');
    const linkAnchor = document.createElement('a');
    linkAnchor.href = lesson.rawUrl || lesson.url;
    linkAnchor.target = '_blank';
    linkAnchor.textContent = 'عرض';
    linkTd.appendChild(linkAnchor);
    tr.appendChild(linkTd);
    // الإجراءات
    const actionsTd = document.createElement('td');
    // تعديل
    const editBtn = document.createElement('button');
    editBtn.textContent = 'تعديل';
    editBtn.className = 'btn-secondary';
    editBtn.addEventListener('click', () => {
      const newTitle = prompt('العنوان الجديد:', lesson.title);
      if (newTitle === null) return;
      const newUrl = prompt('رابط الفيديو الجديد:', lesson.rawUrl || lesson.url);
      if (newUrl === null) return;
      const newFree = confirm('هل تريد جعل الدرس مجاني؟ اضغط "موافق" للموافقة، "إلغاء" لرفض');
      let list = loadLessons();
      const idx = list.findIndex((l) => l.id === lesson.id);
      if (idx !== -1) {
        list[idx].title = newTitle.trim();
        list[idx].rawUrl = newUrl.trim();
        list[idx].url = parseEmbedURL(newUrl.trim());
        list[idx].free = newFree;
        saveLessons(list);
        renderLessonsTable();
      }
    });
    // حذف
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'حذف';
    deleteBtn.className = 'btn-secondary';
    deleteBtn.addEventListener('click', () => {
      if (confirm('هل أنت متأكد من حذف الدرس؟')) {
        let list = loadLessons();
        list = list.filter((l) => l.id !== lesson.id);
        saveLessons(list);
        renderLessonsTable();
      }
    });
    actionsTd.appendChild(editBtn);
    actionsTd.appendChild(deleteBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  });
}

// تحميل المخطوطات من localStorage
function loadManuscripts() {
  try {
    return JSON.parse(localStorage.getItem('manuscripts') || '[]');
  } catch (e) {
    return [];
  }
}

// حفظ المخطوطات في localStorage
function saveManuscripts(list) {
  localStorage.setItem('manuscripts', JSON.stringify(list));
}

// رسم جدول المخطوطات في لوحة التحكم
function renderManuscriptsTable() {
  const table = document.getElementById('manuscripts-table');
  if (!table) return;
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  let manuscripts = [];
  try {
    manuscripts = JSON.parse(localStorage.getItem('manuscripts') || '[]');
  } catch (e) {
    manuscripts = [];
  }
  manuscripts.forEach((manuscript) => {
    const tr = document.createElement('tr');
    // عنوان
    const titleTd = document.createElement('td');
    titleTd.textContent = manuscript.title;
    tr.appendChild(titleTd);
    // الوصف
    const descTd = document.createElement('td');
    descTd.textContent = manuscript.description || '';
    tr.appendChild(descTd);
    // الرابط
    const linkTd = document.createElement('td');
    const linkAnchor = document.createElement('a');
    linkAnchor.href = manuscript.link;
    linkAnchor.target = '_blank';
    linkAnchor.textContent = 'عرض';
    linkTd.appendChild(linkAnchor);
    tr.appendChild(linkTd);
    // الإجراءات
    const actionsTd = document.createElement('td');
    // تعديل
    const editBtn = document.createElement('button');
    editBtn.textContent = 'تعديل';
    editBtn.className = 'btn-secondary';
    editBtn.addEventListener('click', () => {
      const newTitle = prompt('العنوان الجديد:', manuscript.title);
      if (newTitle === null) return;
      const newDesc = prompt('الوصف الجديد:', manuscript.description || '');
      if (newDesc === null) return;
      const newLink = prompt('الرابط الجديد:', manuscript.link);
      if (newLink === null) return;
      let list = loadManuscripts();
      const idx = list.findIndex((m) => m.id === manuscript.id);
      if (idx !== -1) {
        list[idx].title = newTitle.trim();
        list[idx].description = newDesc.trim();
        list[idx].link = newLink.trim();
        saveManuscripts(list);
        renderManuscriptsTable();
      }
    });
    // حذف
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'حذف';
    deleteBtn.className = 'btn-secondary';
    deleteBtn.addEventListener('click', () => {
      if (confirm('هل أنت متأكد من حذف المخطوطة؟')) {
        let list = loadManuscripts();
        list = list.filter((m) => m.id !== manuscript.id);
        saveManuscripts(list);
        renderManuscriptsTable();
      }
    });
    actionsTd.appendChild(editBtn);
    actionsTd.appendChild(deleteBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  });
}

// رسم جدول المقالات
function renderPostsTable() {
  const table = document.getElementById('posts-table');
  if (!table) return;
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  let posts = [];
  try {
    posts = JSON.parse(localStorage.getItem('posts') || '[]');
  } catch (e) {
    posts = [];
  }
  posts.sort((a, b) => {
    const da = new Date(a.createdAt || a.date || 0);
    const db = new Date(b.createdAt || b.date || 0);
    return db - da;
  });
  posts.forEach((post) => {
    const tr = document.createElement('tr');
    const titleTd = document.createElement('td');
    titleTd.textContent = post.title;
    tr.appendChild(titleTd);
    const dateTd = document.createElement('td');
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
    dateTd.textContent = dateStr;
    tr.appendChild(dateTd);
    const actionsTd = document.createElement('td');
    // زر التعديل
    const editBtn = document.createElement('button');
    editBtn.textContent = 'تعديل';
    editBtn.className = 'btn-secondary';
    editBtn.addEventListener('click', () => {
      const newTitle = prompt('العنوان الجديد:', post.title);
      if (newTitle === null) return;
      const newContent = prompt('نص المقالة الجديد:', post.content);
      if (newContent === null) return;
      let list = [];
      try {
        list = JSON.parse(localStorage.getItem('posts') || '[]');
      } catch (e) {
        list = [];
      }
      const idx = list.findIndex((p) => p.id === post.id);
      if (idx !== -1) {
        list[idx].title = newTitle.trim();
        list[idx].content = newContent.trim();
        localStorage.setItem('posts', JSON.stringify(list));
        renderPostsTable();
      }
    });
    // زر الحذف
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'حذف';
    deleteBtn.className = 'btn-secondary';
    deleteBtn.addEventListener('click', () => {
      if (confirm('هل أنت متأكد من حذف المقالة؟')) {
        let list = [];
        try {
          list = JSON.parse(localStorage.getItem('posts') || '[]');
        } catch (e) {
          list = [];
        }
        list = list.filter((p) => p.id !== post.id);
        localStorage.setItem('posts', JSON.stringify(list));
        renderPostsTable();
      }
    });
    actionsTd.appendChild(editBtn);
    actionsTd.appendChild(deleteBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  });
}

// رسم جدول الكتب
function renderBooksTable() {
  const table = document.getElementById('books-table');
  if (!table) return;
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  let books = [];
  try {
    books = JSON.parse(localStorage.getItem('books') || '[]');
  } catch (e) {
    books = [];
  }
  books.forEach((book) => {
    const tr = document.createElement('tr');
    const titleTd = document.createElement('td');
    titleTd.textContent = book.title;
    tr.appendChild(titleTd);
    const descTd = document.createElement('td');
    descTd.textContent = book.description || '';
    tr.appendChild(descTd);
    const linkTd = document.createElement('td');
    const linkAnchor = document.createElement('a');
    linkAnchor.href = book.link;
    linkAnchor.target = '_blank';
    linkAnchor.textContent = 'رابط';
    linkTd.appendChild(linkAnchor);
    tr.appendChild(linkTd);
    const actionsTd = document.createElement('td');
    const editBtn = document.createElement('button');
    editBtn.textContent = 'تعديل';
    editBtn.className = 'btn-secondary';
    editBtn.addEventListener('click', () => {
      const newTitle = prompt('العنوان الجديد:', book.title);
      if (newTitle === null) return;
      const newDesc = prompt('الوصف الجديد:', book.description || '');
      if (newDesc === null) return;
      const newLink = prompt('الرابط الجديد:', book.link);
      if (newLink === null) return;
      let list = [];
      try {
        list = JSON.parse(localStorage.getItem('books') || '[]');
      } catch (e) {
        list = [];
      }
      const idx = list.findIndex((b) => b.id === book.id);
      if (idx !== -1) {
        list[idx].title = newTitle.trim();
        list[idx].description = newDesc.trim();
        list[idx].link = newLink.trim();
        localStorage.setItem('books', JSON.stringify(list));
        renderBooksTable();
      }
    });
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'حذف';
    deleteBtn.className = 'btn-secondary';
    deleteBtn.addEventListener('click', () => {
      if (confirm('هل أنت متأكد من حذف الكتاب؟')) {
        let list = [];
        try {
          list = JSON.parse(localStorage.getItem('books') || '[]');
        } catch (e) {
          list = [];
        }
        list = list.filter((b) => b.id !== book.id);
        localStorage.setItem('books', JSON.stringify(list));
        renderBooksTable();
      }
    });
    actionsTd.appendChild(editBtn);
    actionsTd.appendChild(deleteBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  });
}

// دالة لرسم جدول المستخدمين
function renderUsersTable() {
  const tbody = document.querySelector('#users-table tbody');
  tbody.innerHTML = '';
  let users = JSON.parse(localStorage.getItem('users') || '[]');
  // استبعد الإدمن من القائمة المعروضة
  const filtered = users.filter((u) => u.role !== 'admin');
  filtered.forEach((user, idx) => {
    const tr = document.createElement('tr');
    // العمود الأول: اسم المستخدم
    const nameTd = document.createElement('td');
    nameTd.textContent = user.username;
    tr.appendChild(nameTd);
    // العمود الثاني: تاريخ الانتهاء
    const expiryTd = document.createElement('td');
    const expiryInput = document.createElement('input');
    expiryInput.type = 'date';
    expiryInput.value = user.expiry || '';
    expiryTd.appendChild(expiryInput);
    tr.appendChild(expiryTd);
    // العمود الثالث: كلمة المرور
    const passTd = document.createElement('td');
    const passInput = document.createElement('input');
    passInput.type = 'password';
    passInput.placeholder = 'تغيير كلمة المرور';
    passTd.appendChild(passInput);
    tr.appendChild(passTd);
    // العمود الرابع: الإجراءات
    const actionsTd = document.createElement('td');
    const updateBtn = document.createElement('button');
    updateBtn.textContent = 'تحديث';
    updateBtn.className = 'btn-secondary';
    updateBtn.addEventListener('click', () => {
      const usersList = JSON.parse(localStorage.getItem('users') || '[]');
      const targetIndex = usersList.findIndex((u) => u.username === user.username);
      if (targetIndex !== -1) {
        usersList[targetIndex].expiry = expiryInput.value;
        // فقط إذا أدخلت كلمة مرور جديدة
        if (passInput.value) {
          usersList[targetIndex].password = passInput.value;
        }
        localStorage.setItem('users', JSON.stringify(usersList));
        alert('تم تحديث بيانات المستخدم');
        // إعادة رسم الجدول
        renderUsersTable();
      }
    });
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'حذف';
    deleteBtn.className = 'btn-secondary';
    deleteBtn.addEventListener('click', () => {
      if (
        confirm('هل أنت متأكد من حذف المستخدم ' + user.username + '؟')
      ) {
        let usersList = JSON.parse(localStorage.getItem('users') || '[]');
        usersList = usersList.filter((u) => u.username !== user.username);
        localStorage.setItem('users', JSON.stringify(usersList));
        renderUsersTable();
      }
    });
    actionsTd.appendChild(updateBtn);
    actionsTd.appendChild(deleteBtn);
    tr.appendChild(actionsTd);
    tbody.appendChild(tr);
  });
}