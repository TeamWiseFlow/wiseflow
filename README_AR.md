# المساعد الذكي للمعلومات (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **استخدم الذكاء الاصطناعي لاستخراج المعلومات التي تهتم بها حقاً من مصادر متعددة يومياً!**

المشكلة ليست في نقص المعلومات، بل في كيفية تصفية الضوضاء من المعلومات الهائلة للكشف عن المعلومات القيمة

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

## 🔥🔥🔥 تم إطلاق إصدار Wiseflow 4.1 رسميًا!

يقدم الإصدار 4.1 العديد من الميزات الجديدة والمثيرة بالإضافة إلى الإصدار 4.0!

### 🔍 مصادر بحث مخصصة

يدعم الإصدار 4.1 التكوين الدقيق لمصادر البحث لنقاط التركيز. وهو يدعم حاليًا أربعة مصادر بحث: bing و github و arxiv و ebay ، وكلها تستخدم واجهات برمجة تطبيقات أصلية للمنصة دون الحاجة إلى خدمات جهات خارجية إضافية.

<img src="docs/select_search_source.gif" alt="search_source" width="360">


### 🧠 دع الذكاء الاصطناعي يفكر من وجهة نظرك!

يدعم الإصدار 4.1 تعيين الأدوار والأهداف لنقاط التركيز لتوجيه LLM في تحليل واستخراج المعلومات من منظور معين أو لغرض معين. ومع ذلك ، يرجى ملاحظة ما يلي:

    - إذا كانت نقطة التركيز نفسها محددة للغاية ، فلن يكون لتعيين الأدوار والأهداف تأثير يذكر على النتائج.
    - العامل الأكثر أهمية الذي يؤثر على جودة النتائج النهائية هو دائمًا مصدر المعلومات. تأكد من توفير مصادر وثيقة الصلة بنقطة التركيز.

لحالات الاختبار حول كيفية تأثير تحديد الأدوار والأهداف على نتائج الاستخراج ، يرجى الرجوع إلى [task1](test/reports/report_v4x_llm/task1).


### ⚙️ وضع الاستخراج المخصص

يمكنك الآن إنشاء النماذج الخاصة بك في واجهة pb وتكوينها لنقاط تركيز محددة. سيقوم LLM بعد ذلك باستخراج المعلومات بدقة وفقًا لحقول النموذج.


### 👥 وضع البحث عن المبدعين لمصادر الوسائط الاجتماعية

يمكنك الآن تحديد البرنامج للعثور على محتوى ذي صلة على منصات الوسائط الاجتماعية بناءً على نقاط التركيز ، والعثور أيضًا على معلومات الصفحة الرئيسية لمنشئي المحتوى. بالاقتران مع "وضع الاستخراج المخصص" ، يمكن أن يساعدك wiseflow في البحث عن معلومات الاتصال بالعملاء المحتملين أو الشركاء أو المستثمرين عبر الشبكة بأكملها.

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">


**لمزيد من المعلومات حول التحديثات في الإصدار 4.1 ، يرجى مراجعة [CHANGELOG](CHANGELOG.md)**

## 🧐  'البحث العميق' مقابل 'البحث الواسع'

أطلقنا على منتج Wiseflow مصطلح "البحث الواسع"، وهذا مقابل "البحث العميق" الشائع حالياً.

"البحث العميق" يتضمن تخطيطاً ديناميكياً لمسار البحث بواسطة LLM لاستكشاف صفحات مختلفة وجمع معلومات كافية للإجابة على سؤال محدد أو إنتاج تقرير. لكن في بعض الأحيان، نحن لا نبحث عن إجابة لسؤال محدد ولا نحتاج إلى استكشاف عميق، بل نحتاج فقط إلى جمع معلومات واسعة (مثل جمع معلومات الصناعة، معلومات الخلفية، معلومات العملاء، إلخ). في هذه الحالات، يكون الاتساع أكثر أهمية. رغم أن "البحث العميق" يمكنه تحقيق هذه المهمة، إلا أنه مثل استخدام مدفع لقتل بعوضة - غير فعال ومكلف. Wiseflow هو الأداة المثالية لمثل هذه السيناريوهات.

## ✋ ما الذي يجعل Wiseflow مختلفاً عن برامج الزحف المدعومة بالذكاء الاصطناعي الأخرى؟

- قدرات الحصول على البيانات من جميع المنصات، بما في ذلك صفحات الويب، ووسائل التواصل الاجتماعي (حالياً تدعم منصتي Weibo و Kuaishou)، ومصادر RSS، بالإضافة إلى مصادر البحث مثل Bing و GitHub و arXiv و eBay، إلخ؛
- سير عمل فريد لمعالجة HTML يقوم تلقائيًا باستخراج المعلومات بناءً على نقاط التركيز ويكتشف الروابط التي تستحق المزيد من الاستكشاف، ويعمل بشكل جيد مع نموذج لغوي كبير بحجم 14 مليار معلمة فقط؛
- سهل الاستخدام (ليس فقط للمطورين)، لا حاجة لتكوين Xpath يدويًا، "جاهز للاستخدام"؛
- استقرار وتوافرية عالية من خلال التكرار المستمر، وكفاءة معالجة توازن بين موارد النظام والسرعة؛
- سيكون أكثر من مجرد "زاحف"...

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(النطاق العام لهندسة 4.x. يشير المربع المتقطع إلى الأجزاء غير المكتملة. نأمل أن ينضم إلينا مطورو المجتمع القادرون ويساهموا بطلبات السحب. سيحصل جميع المساهمين على وصول مجاني إلى الإصدار المحترف!)

## 🌟 البدء السريع

**ثلاث خطوات فقط للبدء!**

**يجب على مستخدمي Windows تحميل أداة git bash مسبقاً وتنفيذ الأوامر التالية في bash [رابط تحميل bash](https://git-scm.com/downloads/win)**

### 📋 تحميل كود المصدر وتثبيت uv و pocketbase

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

ستكتمل عملية تثبيت uv من خلال الخطوات السابقة.

بعد ذلك، قم بزيارة [pocketbase docs](https://pocketbase.io/docs/) لتحميل برنامج pocketbase المناسب لنظام التشغيل الخاص بك وضعه في مجلد [.pb](./pb/)

يمكنك أيضاً استخدام install_pocketbase.sh (لنظامي MacOS/Linux) أو install_pocketbase.ps1 (لنظام Windows) للتثبيت.

### 📥 تكوين ملف .env

في مجلد wiseflow (المجلد الرئيسي للمشروع)، قم بإنشاء ملف .env بناءً على env_sample وإدخال المعلومات المطلوبة.

الإصدار 4.x لا يتطلب من المستخدم توفير بيانات اعتماد pocketbase في ملف .env، ولا يحد من إصدار pocketbase. كما ألغينا مؤقتاً إعداد Secondary Model، لذلك تحتاج فقط إلى أربعة معلمات أساسية:

- LLM_API_KEY="" # مفتاح خدمة LLM (يمكن استخدام أي مزود خدمة يوفر واجهة برمجة تطبيقات بتنسيق OpenAI، لا حاجة للإعداد عند استخدام ollama محلياً)
- LLM_API_BASE="https://api.siliconflow.com/v1" # عنوان واجهة خدمة LLM
- PRIMARY_MODEL="Qwen/Qwen3-14B" # نوصي بـ Qwen3-14B أو نموذج تفكير بنفس المستوى
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # من الأفضل وجوده

### 🚀  ابدأ!

```bash
cd wiseflow
uv venv # فقط يحتاج إلى التنفيذ في المرة الأولى
source .venv/bin/activate  # Linux/macOS
# لنظام Windows:
# .venv\Scripts\activate
uv sync # فقط يحتاج إلى التنفيذ في المرة الأولى
python -m playwright install --with-deps chromium # فقط يحتاج إلى التنفيذ في المرة الأولى
chmod +x run.sh # فقط يحتاج إلى التنفيذ في المرة الأولى
./run.sh
```

للحصول على دليل استخدام مفصل، يرجى الرجوع إلى [docs/manual/manual_ar.md](./docs/manual/manual_ar.md)

## 📚 كيفية استخدام البيانات المجمعة من Wiseflow في برنامجك الخاص

يتم تخزين جميع البيانات المجمعة في pocketbase مباشرة، لذلك يمكنك الوصول إلى البيانات مباشرة من خلال قاعدة بيانات pocketbase.

PocketBase كقاعدة بيانات خفيفة الوزن شائعة الاستخدام، يتوفر حالياً SDK بلغات Go/Javascript/Python وغيرها.

نرحب بمشاركة وترويج أمثلة تطبيقات التطوير الثانوية الخاصة بك في المستودع التالي!

- https://github.com/TeamWiseFlow/wiseflow_plus


## 🛡️ الترخيص

هذا المشروع مفتوح المصدر بموجب [Apache2.0](LICENSE).

للتعاون التجاري، يرجى الاتصال بـ **البريد الإلكتروني: zm.zhao@foxmail.com**

- يرجى من العملاء التجاريين الاتصال بنا للتسجيل، النسخة المفتوحة المصدر مجانية للأبد.

## 📬 معلومات الاتصال

لأي أسئلة أو اقتراحات، يرجى ترك تعليق في [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 هذا المشروع مبني على المشاريع المفتوحة المصدر التالية:

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## الاقتباس

إذا استخدمت أو استشهدت بجزء أو كل من هذا المشروع في عملك، يرجى تضمين المعلومات التالية:

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```

## روابط صديقة

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)