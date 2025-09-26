// course.js
// يتأكد من أن المستخدم مسجل الدخول وأن صلاحية اشتراكه سارية، وإلا يعيد التوجيه.
document.addEventListener('DOMContentLoaded', () => {
  const logged = JSON.parse(sessionStorage.getItem('loggedInUser') || 'null');
  if (!logged) {
    window.location.href = 'login.html';
    return;
  }
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const currentUser = users.find((u) => u.username === logged.username);
  if (!currentUser) {
    sessionStorage.removeItem('loggedInUser');
    window.location.href = 'login.html';
    return;
  }
  // إذا كان المستخدم ليس إدمن، تحقق من تاريخ الانتهاء
  if (currentUser.role !== 'admin' && currentUser.expiry) {
    const expiryDate = new Date(currentUser.expiry);
    const now = new Date();
    if (expiryDate < now) {
      alert('انتهت صلاحية اشتراكك. يرجى التواصل مع الإدارة.');
      sessionStorage.removeItem('loggedInUser');
      window.location.href = 'login.html';
      return;
    }
  }
  // زر تسجيل الخروج
  const logoutBtn = document.getElementById('logout-course');
  logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    sessionStorage.removeItem('loggedInUser');
    window.location.href = 'login.html';
  });

  // تحميل الدروس وعرضها
  const lessonsList = document.getElementById('lessons-list');
  const lessonPlayer = document.getElementById('lesson-player');
  if (lessonsList && lessonPlayer) {
    // تحميل الدروس من localStorage
    let lessons = [];
    try {
      lessons = JSON.parse(localStorage.getItem('lessons') || '[]');
    } catch (e) {
      lessons = [];
    }
    // إذا لا توجد دروس
    if (!lessons || lessons.length === 0) {
      lessonsList.innerHTML = '<p>لا توجد دروس متاحة حالياً.</p>';
      lessonPlayer.innerHTML = '';
    } else {
      // تحديد صلاحيات الوصول لكل درس
      const nowDate = new Date();
      const isAdmin = currentUser.role === 'admin';
      const hasValidSubscription = currentUser.expiry
        ? new Date(currentUser.expiry) >= nowDate
        : false;
      // بناء القائمة
      lessonsList.innerHTML = '';
      lessons.forEach((lesson, idx) => {
        const btn = document.createElement('button');
        btn.className = 'lesson-item';
        btn.textContent = `${idx + 1}. ${lesson.title}${lesson.free ? ' (مجاني)' : ''}`;
        // تحقق من السماح بالوصول
        let accessible = true;
        if (!lesson.free) {
          accessible = isAdmin || hasValidSubscription;
        }
        if (!accessible) {
          btn.classList.add('locked');
        }
        btn.addEventListener('click', () => {
          if (!accessible) {
            alert('هذا الدرس غير متاح ضمن النسخة المجانية. يرجى الاشتراك أو تجديد الاشتراك للوصول إلى هذا المحتوى.');
            return;
          }
          playLesson(idx);
        });
        lessonsList.appendChild(btn);
      });
      // وظيفة تشغيل الدرس
      function playLesson(i) {
        const lesson = lessons[i];
        if (!lesson) return;
        // تحديث المشغل
        lessonPlayer.innerHTML = '';
        const titleEl = document.createElement('h3');
        titleEl.textContent = lesson.title;
        lessonPlayer.appendChild(titleEl);
        const ratio = document.createElement('div');
        ratio.className = 'ratio';
        const iframe = document.createElement('iframe');
        iframe.src = lesson.url;
        iframe.frameBorder = '0';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        ratio.appendChild(iframe);
        lessonPlayer.appendChild(ratio);
        // تمييز العنصر النشط
        const buttons = lessonsList.querySelectorAll('.lesson-item');
        buttons.forEach((b) => b.classList.remove('active'));
        buttons[i].classList.add('active');
      }
      // تشغيل أول درس متاح
      let initialIndex = lessons.findIndex((ls) => {
        if (ls.free) return true;
        return isAdmin || hasValidSubscription;
      });
      if (initialIndex < 0) initialIndex = 0;
      // تأكد أن الدرس الأول قابل للتشغيل
      const initialLesson = lessons[initialIndex];
      if (initialLesson) {
        if (initialLesson.free || isAdmin || hasValidSubscription) {
          playLesson(initialIndex);
        }
      }
    }
  }
});