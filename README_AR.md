<div dir="rtl">

# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **STEP INTO 5.x**

> 📌 **تبحث عن الإصدار 4.x؟** الكود الأصلي للإصدار v4.30 والإصدارات السابقة متوفر في [فرع `4.x`](https://github.com/TeamWiseFlow/wiseflow/tree/4.x).

```
"حياتي لها حدود، لكن المعرفة بلا حدود. أن تلاحق اللامحدود بالمحدود — فذلك خطر محدق!" — تشوانغ تزو، الفصول الداخلية، تغذية مبدأ الحياة
```

حقق wiseflow 4.x (بما في ذلك الإصدارات السابقة) قدرات قوية في جمع البيانات في سيناريوهات محددة من خلال سلسلة من سير العمل الدقيقة، لكنه لا يزال يعاني من قيود كبيرة:

- 1. عدم القدرة على جمع المحتوى التفاعلي (المحتوى الذي لا يظهر إلا بعد النقر، خاصة في حالات التحميل الديناميكي)
- 2. يقتصر على تصفية واستخراج المعلومات، مع غياب شبه كامل لقدرات معالجة المهام اللاحقة
- ……

على الرغم من أننا عملنا باستمرار على تحسين وظائفه وتوسيع حدوده، إلا أن العالم الحقيقي معقد، وكذلك الإنترنت. لا يمكن أن تكون القواعد شاملة أبداً، لذا فإن سير العمل الثابت لن يتمكن أبداً من التكيف مع جميع السيناريوهات. هذه ليست مشكلة wiseflow — إنها مشكلة البرمجيات التقليدية!

ومع ذلك، أظهر لنا التقدم السريع في تقنية الوكلاء (Agents) خلال العام الماضي الإمكانية التقنية لمحاكاة سلوك الإنسان على الإنترنت بالكامل بواسطة نماذج اللغة الكبيرة. وقد عزز ظهور [openclaw](https://github.com/openclaw/openclaw) هذا الاقتناع بشكل أكبر.

والأكثر إثارة للدهشة أنه من خلال تجاربنا واستكشافاتنا المبكرة، اكتشفنا أن دمج قدرات جمع البيانات في wiseflow في openclaw على شكل "إضافات" يحل المشكلتين المذكورتين أعلاه بشكل مثالي. سنقوم بنشر مقاطع فيديو تجريبية حقيقية مثيرة قريباً، إلى جانب إصدار هذه "الإضافات" كمصدر مفتوح.

تجدر الإشارة إلى أن نظام الإضافات في openclaw يختلف كثيراً عما نفهمه تقليدياً بـ"الإضافات" (المشابهة لإضافات Claude Code). لذلك اضطررنا إلى تقديم مفهوم "add-on". وبشكل دقيق، سيظهر wiseflow 5.x على شكل add-on لـ openclaw. لا يحتوي openclaw الأصلي على بنية "add-on"، لكن عملياً تحتاج فقط إلى بضعة أوامر shell بسيطة لإتمام هذا "التحويل". كما أعددنا نسخة معززة من openclaw جاهزة للاستخدام مع إعدادات مسبقة لسيناريوهات الأعمال الحقيقية: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). يمكنك ببساطة استنساخها ووضع إصدار wiseflow في مجلد add-on الخاص بـ openclaw_for_business.

## 🌟 البدء السريع

قم بتنزيل الحزمة المتكاملة (التي تشمل openclaw_for_business و��ضافة wiseflow) مباشرةً من [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) لهذا المستودع، ثم فك الضغط وشغّل سكريبت النشر بنقرة واحدة.

### [بديل] التثبيت اليدوي

> ملاحظة: تحتاج أولاً إلى تنزيل ونشر openclaw_for_business من: https://github.com/TeamWiseFlow/openclaw_for_business/releases

انسخ مجلد `wiseflow` من هذا المستودع (وليس المستودع بأكمله) إلى مجلد `addons/` الخاص بـ openclaw_for_business:

<div dir="ltr">

```bash
# الطريقة 1: الاستنساخ من مستودع wiseflow
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

</div>

أعد تشغيل openclaw_for_business بعد التثبيت لتفعيل التغييرات.

## هيكل المجلدات

<div dir="ltr">

```
wiseflow/
├── addon.json                    # البيانات الوصفية
├── overrides.sh                  # pnpm overrides + تعطيل web_search المدمج
├── patches/
│   ├── 001-browser-tab-recovery.patch        # رقعة استعادة علامات التبويب
│   └── 002-disable-web-search-env-var.patch  # تعطيل web_search المدمج (env var)
├── skills/
│   ├── browser-guide/SKILL.md    # أفضل ممارسات المتصفح (تسجيل الدخول/CAPTCHA/التحميل الكسول، إلخ)
│   ├── smart-search/SKILL.md     # منشئ URL البحث متعدد المنصات (يحل محل web_search المدمج)
│   └── rss-reader/               # قارئ خلاصات RSS/Atom
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
├── docs/                         # التوثيق التقني
│   ├── anti-detection-research.md
│   └── more_powerful_search_skill/
└── tests/                        # حالات الاختبار والنصوص البرمجية
    ├── README.md
    └── run-managed-tests.mjs
```

</div>

## WiseFlow Pro متوفر الآن!

قدرات استخراج أقوى، دعم أشمل لوسائل التواصل الاجتماعي، مع واجهة مستخدم وحزمة تثبيت بنقرة واحدة — لا حاجة للنشر!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **النسخة الاحترافية معروضة للبيع الآن**: https://shouxiqingbaoguan.com/

🌹 بدءاً من اليوم، ساهم بطلبات السحب (PR) في النسخة مفتوحة المصدر من wiseflow (الكود والتوثيق ومشاركة قصص النجاح مرحب بها). عند القبول، سيحصل المساهمون على ترخيص لمدة عام واحد لـ wiseflow Pro!

📥 🎉 📚

## 🛡️ الترخيص

منذ الإصدار 4.2، قمنا بتحديث ترخيصنا مفتوح المصدر. يرجى الاطلاع على: [LICENSE](LICENSE)

للتعاون التجاري، ير��ى التواصل عبر **البريد الإلكتروني: zm.zhao@foxmail.com**

## 📬 اتصل بنا

لأي أسئلة أو اقتراحات، لا تتردد في ترك رسالة عبر [المشكلات](https://github.com/TeamWiseFlow/wiseflow/issues).

لمتطلبات النسخة الاحترافية أو ملاحظات التعاون، يرجى التواصل معنا عبر WeChat:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x مبني على المشاريع مفتوحة المصدر الممتازة التالية:

- Patchright (نسخة Python غير قابلة للكشف من مكتبة Playwright للاختبار والأتمتة) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (تحليل الخلاصات في Python) https://github.com/kurtmckee/feedparser
- SearXNG (محرك بحث وصفي مجاني على الإنترنت يجمع النتائج من خدمات البحث وقواعد البيانات المختلفة) https://github.com/searxng/searxng

## الاستشهاد

إذا أشرت إلى أو استشهدت بجزء أو كل هذا المشروع في عملك، يرجى تضمين المعلومات التالية:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## الشركاء

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)

</div>
