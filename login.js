// login.js
// هذا الملف يتعامل مع عملية تسجيل الدخول للمستخدمين والإدمن.

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const errorEl = document.getElementById('login-error');

  // تأكد من وجود مستخدم إدمن افتراضي إذا لم تتم تهيئة أية بيانات مسبقًا
  initializeDefaultAdmin();

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find(
      (u) => u.username === username && u.password === password
    );
    if (user) {
      // تحقق من تاريخ انتهاء الاشتراك إن وجد للمستخدمين العاديين
      if (user.role !== 'admin' && user.expiry) {
        const now = new Date();
        const expiryDate = new Date(user.expiry);
        if (expiryDate < now) {
          errorEl.textContent = 'انتهت صلاحية حسابك. يرجى التواصل مع الإدارة.';
          return;
        }
      }
      // حفظ معلومات الجلسة مؤقتًا
      sessionStorage.setItem(
        'loggedInUser',
        JSON.stringify({ username: user.username, role: user.role })
      );
      // التوجيه حسب الدور
      if (user.role === 'admin') {
        window.location.href = 'admin.html';
      } else {
        window.location.href = 'course.html';
      }
    } else {
      errorEl.textContent = 'اسم المستخدم أو كلمة المرور غير صحيحة.';
    }
  });
});

// إضافة إدمن افتراضي إذا لم يوجد إدمن مسجل سابقًا
function initializeDefaultAdmin() {
  let users = [];
  try {
    users = JSON.parse(localStorage.getItem('users') || '[]');
  } catch (e) {
    users = [];
  }
  const hasAdmin = users.some((u) => u.role === 'admin');
  if (!hasAdmin) {
    users.push({ username: 'admin', password: 'admin123', role: 'admin' });
    localStorage.setItem('users', JSON.stringify(users));
  }
}