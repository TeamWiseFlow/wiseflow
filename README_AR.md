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

والأكثر إثارة للدهشة أنه من خلال تجاربنا واستكشافاتنا المبكرة، اكتشفنا أن دمج قدرات جمع البيانات في wiseflow في openclaw على شكل "إضافات" يحل المشكلتين المذكورتين أعلاه بشكل مثالي.

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

تجدر الإشارة إلى أن نظام الإضافات في openclaw يختلف كثيراً عما نفهمه تقليدياً بـ"الإضافات" (المشابهة لإضافات Claude Code). لذلك اضطررنا إلى تقديم مفهوم "add-on". وبشكل دقيق، سيظهر wiseflow 5.x على شكل add-on لـ openclaw. لا يحتوي openclaw الأصلي على بنية "add-on"، لكن عملياً تحتاج فقط إلى بضعة أوامر shell بسيطة لإتمام هذا "التحويل". كما أعددنا نسخة معززة من openclaw جاهزة للاستخدام مع إعدادات مسبقة لسيناريوهات الأعمال الحقيقية: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). يمكنك ببساطة استنساخها ووضع إصدار wiseflow في مجلد add-on الخاص بـ openclaw_for_business.

## ✨ ما الذي ستكسبه بتثبيت wiseflow (أفضل من openclaw الأصلي)؟

### 1. متصفح مضاد للكشف، دون الحاجة لتثبيت أي إضافات للمتصفح

يستبدل patch-001 الخاص بـ wiseflow برنامج Playwright المدمج في openclaw بـ [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) (نسخة fork غير قابلة للكشف من Playwright)، مما يقلل بشكل كبير من احتمالية اكتشاف المتصفحات الآلية وحجبها من قبل المواقع المستهدفة. وهذا يعني أنه دون الحاجة إلى تثبيت امتداد Chrome Relay، يمكن لمتصفح مُدار وحده تحقيق قدرات اكتساب وتشغيل الويب المماثلة لإعداد relay أو حتى أفضل منه.

📥 *قمنا بتقييم جميع أطر عمل أتمتة المتصفح الرائجة في السوق، بما في ذلك nodriver وbrowser-use وagent-browser من Vercel. يمكننا التأكيد أنه رغم أن جميعها تعمل عبر CDP وتوفر ملفات تعريف مخصصة ومستمرة لـ openclaw، إلا أن Patchright وحده يوفر إزالة كاملة لبصمات CDP. بعبارة أخرى، حتى نهج الاتصال المباشر بـ CDP الأكثر نقاءً لا يزال يحمل توقيعات قابلة للكشف. تم تصميم الأطر الأخرى للاختبار الآلي، وليس لجمع البيانات، بينما تم تصميم Patchright خصيصاً للاستحواذ. ونظراً لأنه في جوهره تصحيح (patch) على Playwright، فإنه يرث تقريباً جميع واجهات برمجة التطبيقات عالية المستوى الخاصة بـ Playwright، مما يجعله متوافقاً بطبيعته مع openclaw دون الحاجة إلى تثبيت أي إضافات أو MCP إضافية.*

### 2. آلية الاسترداد التلقائي لعلامات التبويب

عندما تُغلق أو تُفقد علامة تبويب مستهدفة بشكل غير متوقع أثناء عملية Agent، يقوم النظام تلقائياً بإجراء استرداد علامة التبويب بناءً على لقطات الحالة، مما يضمن عدم انقطاع المهام بسبب فقدان علامة التبويب.

### 3. مهارة البحث الذكي (Smart Search Skill)

يحل محل `web_search` المدمج في openclaw بقدرات بحث أكثر قوة. مقارنةً بأداة web search المدمجة الأصلية، يتميز البحث الذكي بثلاث مزايا جوهرية:

- **مجاني تماماً، لا يتطلب مفتاح API**: لا يعتمد على أي API بحث من طرف ثالث — تكلفة صفرية
- **بحث فوري لأقصى درجات الحداثة**: يوجّه المتصفح مباشرةً إلى الصفحات المستهدفة أو منصات التواصل الاجتماعي الكبرى (ويبو، Twitter/X، Facebook، إلخ) للحصول فوراً على أحدث المنشورات
- **مصادر بحث قابلة للتخصيص**: يمكن للمستخدمين تحديد مصادر بحثهم بحرية للحصول على معلومات دقيقة وموجّهة

### 4. New Media Editor Crew (وكيل AI مسبق الإعداد)

وكيل AI جاهز للاستخدام لإنشاء محتوى وسائل التواصل الاجتماعي الصينية، متخصص في المنصات الرئيسية الصينية مثل Weibo وXiaohongshu وZhihu وBilibili وDouyin.

**القدرات الرئيسية:**

- بحث الموضوعات + تحليل الاتجاهات (الوضع A)
- توسيع المسودة + إضافة أدلة من الإنترنت (الوضع B)
- بعد الانتهاء من المقال، استدعاء [Wenyan](https://github.com/caol64/wenyan) تلقائياً لتحويله إلى HTML بتنسيق حساب WeChat العام (7 قوالب مدمجة)
- الدفع المباشر إلى صندوق مسودات حساب WeChat العام (الوضع C، يتطلب `WECHAT_APP_ID`/`WECHAT_APP_SECRET`)
- دعم توليد الصور/الفيديو بالذكاء الاصطناعي ([SiliconFlow](https://www.siliconflow.com/) لتوليد الصور/الفيديو، يتطلب `SILICONFLOW_API_KEY`)

## 🌟 البدء السريع

> **💡 ��لاحظة حول تكاليف API**
>
> يعتمد wiseflow 5.x على سير عمل Agent الخاص بـ openclaw، مما يتطلب الوصول إلى واجهة برمجة تطبيقات LLM. نوصي بإعداد بيانات اعتماد API مسبقاً:
>
> - **المستخدمون الدوليون (موصى به)**: [SiliconFlow](https://www.siliconflow.com/) — رصيد مجاني متاح بعد التسجيل يغطي تكاليف الاستخدام الأولي
> - **OpenAI / Anthropic ومزودون آخرون**: أي API متوافق يعمل

قم بتنزيل الحزمة المتكاملة (التي تشمل openclaw_for_business وإضافة wiseflow) مباشرةً من [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) لهذا المستودع.

1. تنزيل الأرشيف وفك ضغطه
2. الانتقال إلى المجلد المستخرج
3. اختيار وضع التشغيل:

**وضع التصحيح** (تشغيل مفرد، للاختبار والتطوير):

<div dir="ltr">

```bash
./scripts/dev.sh gateway
```

</div>

**وضع الإنتاج** (التثبيت كخدمة نظام، للتشغيل طويل الأمد):

<div dir="ltr">

```bash
./scripts/reinstall-daemon.sh
```

</div>

> **متطلبات النظام**
> - يُنصح باستخدام نظام **Ubuntu 22.04**
> - بيئة **Windows WSL2** مدعومة
> - **macOS** مدعوم
> - التشغيل المباشر على **Windows الأصلي** **غير مدعوم**

### [بديل] التثبيت اليدوي

> ملاحظة: تحتاج أولاً إلى تنزيل ��نشر openclaw_for_business من: https://github.com/TeamWiseFlow/openclaw_for_business/releases

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
wiseflow/                         # حزمة addon (انسخها إلى مجلد addons/)
├── addon.json                    # البيانات الوصفية
├── overrides.sh                  # pnpm overrides + تعطيل web_search المدمج
├── patches/
│   ├── 001-browser-tab-recovery.patch        # رقعة استعادة علامات التبويب
│   ├── 002-disable-web-search-env-var.patch  # تعطيل web_search المدمج (env var)
│   └── 003-act-field-validation.patch        # رقعة التحقق من حقول ACT
├── skills/                       # المهارات العامة (متاحة لجميع الوكلاء)
│   ├── browser-guide/SKILL.md    # أفضل ممارسات المتصفح (تسجيل الدخول/CAPTCHA/التحميل الكسول، إلخ)
│   ├── smart-search/SKILL.md     # منشئ URL البحث متعدد المنصات (يحل محل web_search المدمج)
│   └── rss-reader/               # قارئ خلاصات RSS/Atom
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # وكلاء AI مسبقو الإعداد (قوالب Crew)
    └── new-media-editor/         # محرر الوسائط ��لجديدة (إنشاء محتوى وسائل التواصل الاجتماعي الصينية)
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # مهارات خاصة بـ Crew
            ├── siliconflow-img-gen/   # توليد صور AI (SiliconFlow API)
            ├── siliconflow-video-gen/ # توليد فيديو AI (SiliconFlow API)
            └── wenyan-formatter/      # Markdown → HTML WeChat / إرسال المسودة

docs/                             # التوثيق التقني (جذر المستودع)
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # النصوص البرمجية المساعدة (جذر المستودع)
└── generate-patch.sh

tests/                            # حالات الاختبار والنصوص البرمجية (جذر المستودع)
├── README.md
└── run-managed-tests.mjs
```

</div>

## WiseFlow Pro متوفر الآن!

قدرات استخراج أقوى، دعم أشمل لوسائل التواصل الاجتماعي، مع واجهة مستخدم وحزمة تثبيت بنقرة واحدة — لا حاجة للنشر!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **النسخة الاحترافية معروضة للبيع الآن**: https://shouxiqingbaoguan.com/

🌹 بدءاً من اليوم، ساهم بطلبات السحب (PR) في النسخة مفتوحة المصدر من wiseflow (الكود والتوثيق ومشاركة قصص النجاح مرحب بها). عند القبول، سيحصل المساهمون على ترخيص لمدة عام واحد لـ wiseflow Pro!

## 🛡️ الترخيص

منذ الإصدار 4.2، قمنا بتحديث ترخيصنا مفتوح المصدر. يرجى الاطلاع على: [LICENSE](LICENSE)

للتعاون التجاري، يرجى التواصل عبر **البريد الإلكتروني: zm.zhao@foxmail.com**

## 📬 اتصل بنا

لأي أسئلة أو اقتراحات، لا تتردد في ترك رسالة عبر [المشكلات](https://github.com/TeamWiseFlow/wiseflow/issues).

🎉 يقدم wiseflow & OFB الآن **قاعدة معرفة مدفوعة**، تتضمن دروس تعليمية للتثبيت خطوة بخطوة، ونصائح تطبيقية حصرية، و**مجموعة WeChat VIP**:

أضف "Keeper" على WeChat Enterprise للاستفسار:

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 المصدر المفتوح يتطلب جهداً كبيراً — شكراً لدعمكم!

## 🤝 wiseflow 5.x مبني على المشاريع مفتوحة المصدر الممتازة التالية:

- Patchright (نسخة Python غير قابلة للكشف من مكتبة Playwright للاختبار والأتمتة) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (تحليل الخلاصات في Python) https://github.com/kurtmckee/feedparser
- SearXNG (محرك بحث وصفي مجاني على الإنترنت يجمع النتائج من خدمات البحث وقواعد البيانات المختلفة) https://github.com/searxng/searxng
- Wenyan (أداة تنسيق ونشر Markdown متعددة المنصات، يستخدمها New Media Editor Crew عبر مهارة wenyan-formatter) https://github.com/caol64/wenyan

## الاستشهاد

إذا أشرت إلى أو استشهدت بجزء أو كل هذا المشروع في عملك، يرجى تضمين المعلومات التالية:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## الشركاء

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)

</div>
