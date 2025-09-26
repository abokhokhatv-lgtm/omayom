// بيانات الكورسات والكتب للموقع
const courses = [
  {
    title: 'التوازن الروحاني',
    description:
      'تعلم أسس التوازن بين الروح والجسد والعقل، وطرق المحافظة على سلامة الطاقة الداخلية.',
    price: '250 جنيه',
    // الرابط يوجه إلى صفحة تسجيل الدخول/الدورة
    link: 'login.html',
  },
  {
    title: 'قوة العقل الباطن',
    description:
      'استكشف قدرات العقل الباطن وكيفية استخدامه لتحقيق النجاح والراحة النفسية.',
    price: '300 جنيه',
    link: 'login.html',
  },
  {
    title: 'العلاج بالطاقة',
    description:
      'تعلم كيفية استخدام الطاقة في العلاج الذاتي ومساعدة الآخرين على الشفاء.',
    price: '350 جنيه',
    link: 'login.html',
  },
];

// قائمة الكتب الافتراضية تُستخدم فقط إذا لم تكن هناك كتب مخزنة في localStorage
const defaultBooks = [
  {
    title: 'كتاب أسرار العلاج',
    description: 'دليل شامل لفنون العلاج الروحاني وتقنياته المختلفة.',
    link: '#',
  },
  {
    title: 'كتاب الطاقة الروحانية',
    description: 'تعرف على مفهوم الطاقة الروحانية وكيفية استغلالها في حياتك اليومية.',
    link: '#',
  },
  {
    title: 'كتاب مسارات التأمل',
    description: 'طرق وتمارين عملية لتحقيق حالة الهدوء والسكينة الداخلية.',
    link: '#',
  },
];

// دالة لإنشاء عنصر كورس
function createCourseCard(course) {
  const card = document.createElement('div');
  card.className = 'course-card';

  const title = document.createElement('h3');
  title.textContent = course.title;
  card.appendChild(title);

  const desc = document.createElement('p');
  desc.textContent = course.description;
  card.appendChild(desc);

  const price = document.createElement('div');
  price.className = 'price';
  price.textContent = course.price;
  card.appendChild(price);

  const button = document.createElement('a');
  button.className = 'btn-primary';
  button.href = course.link;
  button.textContent = 'اشتر الكورس';
  card.appendChild(button);

  return card;
}

// دالة لإنشاء عنصر كتاب
function createBookCard(book) {
  const card = document.createElement('div');
  card.className = 'book-card';

  const title = document.createElement('h4');
  title.textContent = book.title;
  card.appendChild(title);

  const desc = document.createElement('p');
  desc.textContent = book.description;
  card.appendChild(desc);

  const button = document.createElement('a');
  button.className = 'btn-secondary';
  button.href = book.link;
  button.textContent = 'تحميل الكتاب';
  card.appendChild(button);

  return card;
}

// تحميل الكورسات والكتب عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
  const coursesContainer = document.getElementById('courses-list');
  courses.forEach((course) => {
    const card = createCourseCard(course);
    coursesContainer.appendChild(card);
  });

  // تحميل الكتب من localStorage إذا وجدت، وإلا استخدم القائمة الافتراضية
  const booksContainer = document.getElementById('books-list');
  let storedBooks = [];
  try {
    storedBooks = JSON.parse(localStorage.getItem('books') || '[]');
  } catch (e) {
    storedBooks = [];
  }
  const booksToShow = storedBooks && storedBooks.length ? storedBooks : defaultBooks;
  booksToShow.forEach((book) => {
    const card = createBookCard(book);
    booksContainer.appendChild(card);
  });
});