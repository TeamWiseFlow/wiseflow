# V0.3.8

- 增加对 RSS 信源的支持

  add support for RSS source

- 支持为关注点指定信源，并且可以为每个关注点增加搜索引擎作为信源

  support to specify source for each focus point, and add search engine as source

- 进一步优化信息提取策略（每次只处理一个关注点）

  Further optimized information extraction strategy (processing one focus point at a time)

- 优化入口逻辑，简化并合并启动方案 （感谢 @c469591 贡献windows版本启动脚本）

  Optimized entry logic, simplified and merged startup solutions (thanks to @c469591 for contributing Windows startup script)


# V0.3.7

- 新增通过wxbot方案获取微信公众号订阅消息信源（不是很优雅，但已是目前能找到的最佳方案）
  
  Added WeChat Official Account subscription message source acquisition through wxbot solution (not very elegant, but currently the best solution available)

- 升级适配 Crawl4ai 0.4.247 版本，

  Upgraded to fit Crawl4ai 0.4.247 version,

- 通过新增预处理流程以及全新设计的推荐链接提取策略，大幅提升信息抓取效果，现在7b 这样的小模型也能比较好的完成复杂关注点（explanation中包含时间、指标限制这种）的提取了。

  Through the addition of a new pre-processing process and a completely redesigned recommended link extraction strategy, the information capture effect has been significantly improved, and now even small models like 7b can better complete the extraction of complex focus points (such as time and index limits in the explanation).

- 提供自定义提取器接口，方便用户根据实际需求进行定制。

  Provided a custom extractor interface to allow users to customize according to actual needs.

- bug 修复以及其他改进（crawl4ai浏览器生命周期管理，异步 llm wrapper 等）（感谢 @tusik 贡献异步 llm wrapper）

  Bug fixes and other improvements (crawl4ai browser lifecycle management, asynchronous llm wrapper, etc.)

  Thanks to @tusik for contributing the asynchronous LLM wrapper

# V0.3.6
- 改用 Crawl4ai 作为底层爬虫框架，其实Crawl4ai 和 Crawlee 的获取效果差别不大，二者也都是基于 Playwright ，但 Crawl4ai 的 html2markdown 功能很实用，而这对llm 信息提取作用很大，另外 Crawl4ai 的架构也更加符合我的思路；

  Switched to Crawl4ai as the underlying web crawling framework. Although Crawl4ai and Crawlee both rely on Playwright with similar fetching results, Crawl4ai's html2markdown feature is quite practical for LLM information extraction. Additionally, Crawl4ai's architecture better aligns with my design philosophy.

- 在 Crawl4ai 的 html2markdown 基础上，增加了 deep scraper，进一步把页面的独立链接与正文进行区分，便于后一步 llm 的精准提取。由于html2markdown和deep scraper已经将原始网页数据做了很好的清理，极大降低了llm所受的干扰和误导，保证了最终结果的质量，同时也减少了不必要的 token 消耗；

  Built upon Crawl4ai's html2markdown, we added a deep scraper to further differentiate standalone links from the main content, facilitating more precise LLM extraction. The preprocessing done by html2markdown and deep scraper significantly cleans up raw web data, minimizing interference and misleading information for LLMs, ensuring higher quality outcomes while reducing unnecessary token consumption.

   *列表页面和文章页面的区分是所有爬虫类项目都头痛的地方，尤其是现代网页往往习惯在文章页面的侧边栏和底部增加大量推荐阅读，使得二者几乎不存在文本统计上的特征差异。*
   *这一块我本来想用视觉大模型进行 layout 分析，但最终实现起来发现获取不受干扰的网页截图是一件会极大增加程序复杂度并降低处理效率的事情……*

  *Distinguishing between list pages and article pages is a common challenge in web scraping projects, especially when modern webpages often include extensive recommended readings in sidebars and footers of articles, making it difficult to differentiate them through text statistics.*

  *Initially, I considered using large visual models for layout analysis, but found that obtaining undistorted webpage screenshots greatly increases program complexity and reduces processing efficiency...*
  
- 重构了提取策略、llm 的 prompt 等；

  Restructured extraction strategies and LLM prompts;

  *有关 prompt 我想说的是，我理解好的 prompt 是清晰的工作流指导，每一步都足够明确，明确到很难犯错。但我不太相信过于复杂的 prompt 的价值，这个很难评估，如果你有更好的方案，欢迎提供 PR*

   *Regarding prompts, I believe that a good prompt serves as clear workflow guidance, with each step being explicit enough to minimize errors. However, I am skeptical about the value of overly complex prompts, which are hard to evaluate. If you have better solutions, feel free to submit a PR.*

- 引入视觉大模型，自动在提取前对高权重（目前由 Crawl4ai 评估权重）图片进行识别，并补充相关信息到页面文本中；

  Introduced large visual models to automatically recognize high-weight images (currently evaluated by Crawl4ai) before extraction and append relevant information to the page text;

- 继续减少 requirement.txt 的依赖项，目前不需要 json_repair了（实践中也发现让 llm 按 json 格式生成，还是会明显增加处理时间和失败率，因此我现在采用更简单的方式，同时增加对处理结果的后处理）

  Continued to reduce dependencies in requirement.txt; json_repair is no longer needed (in practice, having LLMs generate JSON format still noticeably increases processing time and failure rates, so I now adopt a simpler approach with additional post-processing of results)

- pb info 表单的结构做了小调整，增加了 web_title 和 reference 两项。

  Made minor adjustments to the pb info form structure, adding web_title and reference fields.

- @ourines 贡献了 install_pocketbase.sh 脚本

  @ourines contributed the install_pocketbase.sh script

- @ibaoger 贡献了 windows 下的pocketbase 安装脚本

  @ibaoger contributed the pocketbase installation script for Windows

- docker运行方案被暂时移除了，感觉大家用起来也不是很方便……

  Docker running solution has been temporarily removed as it wasn't very convenient for users...

# V0.3.5
- 引入 Crawlee(playwrigt模块)，大幅提升通用爬取能力，适配实际项目场景；
  
  Introduce Crawlee (playwright module), significantly enhancing general crawling capabilities and adapting to real-world task;

- 完全重写了信息提取模块，引入“爬-查一体”策略，你关注的才是你想要的；

  Completely rewrote the information extraction module, introducing an "integrated crawl-search" strategy, focusing on what you care about;

- 新策略下放弃了 gne、jieba 等模块，去除了安装包；

  Under the new strategy, modules such as gne and jieba have been abandoned, reducing the installation package size;

- 重写了 pocketbase 的表单结构；
  
  Rewrote the PocketBase form structure;

- llm wrapper引入异步架构、自定义页面提取器规范优化（含 微信公众号文章提取优化）；

  llm wrapper introduces asynchronous architecture, customized page extractor specifications optimization (including WeChat official account article extraction optimization);

- 进一步简化部署操作步骤。

  Further simplified deployment steps.
