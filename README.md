
# 🔧 پاک‌ساز کامنت‌های کد (Code Comment Stripping Tool)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/yourusername/Code-Comment-Stripper)

یک ابزار دسکتاپ قدرتمند و ایمن نوشته شده با **Python** و **Tkinter** برای حذف کامنت‌ها از فایل‌های کد منبع. این ابزار با پشتیبانی از زبان‌های متعدد، به توسعه‌دهندگان کمک می‌کند تا قبل از انتشار نهایی پروژه یا تحلیل کد، حجم فایل‌ها را کاهش دهند و کد را تمیزتر کنند.

## ✨ ویژگی‌های کلیدی

- 🌍 **پشتیبانی چندزبانه:** شناسایی و حذف کامنت‌های خطی و بلوکی در زبان‌های Python, C, C++, Java, JavaScript, TypeScript, HTML, CSS, Go, Rust و غیره.
- 🛡️ **حالت پیش‌نمایش (Dry Run):** قبل از اعمال تغییرات واقعی، دقیقاً ببینید چه خطوطی حذف خواهند شد.
- 💾 **پشتیبان‌گیری خودکار:** ایجاد فایل `.bak` از فایل‌های اصلی قبل از هرگونه تغییر، برای اطمینان از امنیت کد.
- 🚫 **الگوهای استثناء (Exclude Patterns):** قابلیت نادیده گرفتن پوشه‌هایی مانند `node_modules`, `.git`, `venv` و فایل‌های `min.js`.
- 📊 **گزارش‌دهی دقیق:** نمایش تعداد فایل‌های بررسی شده، خطوط و بایت‌های حذف شده و لیست فایل‌های تغییر یافته.
- 🖥️ **رابط کاربری گرافیکی (GUI):** محیط کاربری ساده و کاربرپسند با استفاده از Tkinter.

## 🚀 زبان‌های پشتیبانی شده

ابزار از اکثر زبان‌های برنامه‌نویسی محبوب پشتیبانی می‌کند. لیستی از پسوندهای فایل‌های پشتیبانی شده عبارتند از:

`py`, `c`, `h`, `cpp`, `hpp`, `cc`, `java`, `kt`, `cs`, `js`, `mjs`, `ts`, `jsx`, `tsx`, `go`, `rs`, `swift`, `php`, `rb`, `sh`, `sql`, `css`, `scss`, `less`, `html`, `xml`, `vue`, `lua`, `hs`

## 📋 پیش‌نیازها

- **Python 3.8 یا بالاتر**
- کتابخانه‌های استاندارد (`tkinter`, `os`, `re`, `fnmatch` معمولاً به همراه پایتون نصب می‌شوند).

## 🛠️ نصب و راه‌اندازی

### ۱. کلون کردن مخزن
```bash
git clone https://github.com/hmplus28/Code-Comment-Stripper.git
cd Code-Comment-Stripper
```

### ۲. اجرای برنامه
برای اجرای ابزار کافیست دستور زیر را در ترمینال وارد کنید:

```bash
python comment_cleaner.py
```

## 📖 نحوه استفاده

1.  **انتخاب پوشه پروژه:** با کلیک روی دکمه "Browse" پوشه‌ای که حاوی فایل‌های کد شما است را انتخاب کنید.
2.  **تنظیم گزینه‌ها:**
    -   **Dry Run (توصیه می‌شود):** این گزینه را فعال کنید تا تغییرات فقط در لاگ نمایش داده شوند و فایل‌ها واقعاً تغییر نکنند.
    -   **Create .bak backups:** برای ایجاد نسخه پشتیبان این گزینه را فعال نگه دارید.
    -   **Only known code extensions:** اگر می‌خواهید فقط فایل‌های کدی که شناخته شده‌اند پردازش شوند، این گزینه را فعال کنید.
3.  **تنظیم استثناها:** در کادر متنی مربوطه، پوشه‌هایی که نمی‌خواهید اسکن شوند (مثل `node_modules`) را وارد کنید (هر خط یک الگو).
4.  **اجرای عملیات:** دکمه "Run" را بزنید.
5.  **مشاهده نتایج:** خروجی عملیات را در بخش "Operation Log" مشاهده کنید. اگر از حالت Dry Run استفاده کرده‌اید، نمونه‌ای از کامنت‌هایی که حذف خواهند شد را خواهید دید.
6.  **اعمال نهایی:** اگر از نتایج Dry Run راضی بودید، تیک Dry Run را بردارید و دوباره Run را بزنید تا فایل‌ها پاکسازی شوند.

## ⚠️ هشدارهای ایمنی

- همیشه قبل از استفاده از این ابزار روی پروژه‌های حساس، از پروژه خود **Backup** کامل بگیرید (از Git استفاده کنید).
- این ابزار کامنت‌هایی که داخل String‌ها باشند (مانند `url = "http://example.com #comment"`) را تشخیص داده و حذف نمی‌کند، اما اگر الگوریتم تشخیص زبان دچار خطا شود، ممکن است رخ دهد.
- فایل‌های `.bak` ایجاد شده توسط این ابزار به طور خودکار در اسکن‌های بعدی نادیده گرفته می‌شوند.

## 🤝 مشارکت (Contributing)

Contributions, issues and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



## 👨‍💻 توسعه‌دهنده

**حمیدرضا مهرآبادی**
- [GitHub](https://github.com/hmplus28)
- [LinkedIn](https://linkedin.com/in/hamidreza-mehrabadi-6a6439322)

---

اگر این ابزار برای شما مفید بود، لطفاً به این پروژه ستاره (Star) دهید!
