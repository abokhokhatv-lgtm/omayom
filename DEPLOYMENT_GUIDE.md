# دليل النشر - موقع عمر علي المعالج الروحاني

## 🚀 النشر على Vercel (الطريقة المفضلة)

### الخطوة 1: إنشاء حساب GitHub
1. اذهب إلى [GitHub.com](https://github.com)
2. أنشئ حساب جديد أو سجل دخول
3. أنشئ مستودع جديد باسم `omar-ali-healing-site`

### الخطوة 2: رفع الكود
```bash
git remote add origin https://github.com/YOUR_USERNAME/omar-ali-healing-site.git
git branch -M main
git push -u origin main
```

### الخطوة 3: النشر على Vercel
1. اذهب إلى [Vercel.com](https://vercel.com)
2. سجل دخول باستخدام GitHub
3. اختر "Import Project"
4. اختر مستودع `omar-ali-healing-site`
5. اضغط "Deploy"

### الخطوة 4: تعيين Environment Variables
في لوحة تحكم Vercel:
1. اذهب إلى Settings > Environment Variables
2. أضف المتغيرات التالية:

```
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ADMIN_EMAIL=abokhokhatv@gmail.com
ADMIN_PASSWORD=OmarAli2025!
BANK_NAME=البنك الأهلي المصري
BANK_ACCOUNT_NAME=Omar Ali
BANK_ACCOUNT_NUMBER=1234567890123456
BANK_IBAN=EG380002001234567890123456
WHATSAPP_NUMBER=+201234567890
```

## 🌐 النشر على Netlify (البديل)

### الخطوة 1: النشر
1. اذهب إلى [Netlify.com](https://netlify.com)
2. سجل دخول باستخدام GitHub
3. اختر "New site from Git"
4. اختر مستودع `omar-ali-healing-site`
5. Build command: `npm run build`
6. Publish directory: `dist`

### الخطوة 2: تعيين Environment Variables
في لوحة تحكم Netlify:
1. اذهب إلى Site settings > Environment variables
2. أضف نفس المتغيرات المذكورة أعلاه

## 🔧 إعداد قاعدة البيانات

### تهيئة النظام
بعد النشر، اذهب إلى:
```
https://your-domain.vercel.app/api/setup/initialize
```

هذا سيقوم بـ:
- إنشاء قاعدة البيانات
- إضافة حساب المدير
- إضافة البيانات الافتراضية
- إنشاء الكورسات النموذجية

## 👤 بيانات الدخول

### المدير
- **الرابط**: `https://your-domain.vercel.app/admin`
- **الإيميل**: abokhokhatv@gmail.com
- **كلمة المرور**: OmarAli2025!

## 📱 الروابط المهمة

### الصفحات الرئيسية
- الصفحة الرئيسية: `/`
- من أنا: `/about`
- الخدمات: `/services`
- الكورسات: `/courses`
- المدونة: `/blog`
- التواصل: `/contact`

### صفحات خاصة
- صفحة TikTok: `/tiktok`
- تسجيل الدخول: `/login`
- لوحة التحكم: `/admin`

### API Endpoints
- تهيئة النظام: `/api/setup/initialize`
- حالة النظام: `/api/setup/status`
- تسجيل الدخول: `/api/auth/login`
- الكورسات: `/api/courses`
- الحجوزات: `/api/bookings`

## 🔐 الأمان

### كلمات المرور
- غير كلمة مرور المدير فوراً بعد النشر
- استخدم كلمات مرور قوية
- فعل المصادقة الثنائية إن أمكن

### النسخ الاحتياطية
- اعمل نسخة احتياطية من قاعدة البيانات دورياً
- احتفظ بنسخة من Environment Variables

## 📊 التحليلات

### Google Analytics
1. أنشئ حساب Google Analytics
2. احصل على Tracking ID
3. أضفه في Environment Variables:
```
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### Facebook Pixel
1. أنشئ Facebook Pixel
2. احصل على Pixel ID
3. أضفه في Environment Variables:
```
FACEBOOK_PIXEL_ID=your_facebook_pixel_id
```

## 💳 إعداد الدفع

### Stripe
1. أنشئ حساب Stripe
2. احصل على API Keys
3. أضفها في Environment Variables:
```
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

### PayPal
1. أنشئ حساب PayPal Business
2. احصل على Client ID & Secret
3. أضفها في Environment Variables:
```
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_MODE=live
```

## 📧 إعداد البريد الإلكتروني

### Gmail SMTP
1. فعل 2-Factor Authentication
2. أنشئ App Password
3. أضف الإعدادات:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

## 🎥 إعداد الفيديوهات

### YouTube
1. أنشئ قناة YouTube
2. احصل على API Key
3. ارفع الفيديوهات كـ "Unlisted"

### Vimeo
1. أنشئ حساب Vimeo Pro
2. احصل على Access Token
3. ارفع الفيديوهات كـ "Private"

## 📞 الدعم الفني

### في حالة وجود مشاكل:
1. تحقق من logs في Vercel/Netlify
2. تأكد من Environment Variables
3. تحقق من حالة قاعدة البيانات
4. راجع ملف README.md

### التواصل:
- **الإيميل**: abokhokhatv@gmail.com
- **واتساب**: +201234567890

---

**ملاحظة**: هذا الدليل يحتوي على جميع المعلومات اللازمة للنشر والإدارة. احتفظ به في مكان آمن.

