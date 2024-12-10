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
