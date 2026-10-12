# 招聘与合作需求

本站点组统一使用共享 session/profile `default`；每条 Camoufox 操作带 `--persistent`。入口常量见 [site-catalog.json](../site-catalog.json)。只搜索和读取当前账号可见的岗位、人才与项目；主动沟通、投递、邀约等操作交给 `expert-bd` 的具体 workflow，不在本规则执行。

| 站点 | session / profile | 搜索入口 |
|---|---|---|
| BOSS直聘 | `default` | `https://www.zhipin.com/web/geek/jobs?query={keyword}` |
| 51job/前程无忧 | `default` | `https://we.51job.com/`，使用页面搜索 |
| Indeed | `default` | `https://www.indeed.com/jobs?q={keyword}` |
| 脉脉 | `default` | `https://maimai.cn/ent/talents/discover/search_v2`，使用页面人才搜索 |
| Upwork | `default` | `https://www.upwork.com/nx/search/jobs/?q={keyword}` |

## BOSS直聘

- 打开搜索后核对当前城市，按用户要求通过页面选择城市、经验、学历、薪资、行业和岗位性质；不能把上游默认北京当作用户地区。
- 提取岗位名称、真实详情链接、公司、城市/地点、经验学历要求、可见薪资及薪数。详情核对职责、要求、公司信息和页面实际显示的发布时间。
- 薪资区间与“面议”、是否月薪/年薪分别保留；不点击“立即沟通”或发送自动招呼。验证/登录按 browser-guide 处理。

## 51job/前程无忧

- 在首页实际岗位搜索框输入关键词并选择城市，使用页面的行业、职能、薪资、经验、学历和发布时间筛选；由真实控件进入结果页。
- 保存岗位名、职位链接、公司、地区、薪资、经验/学历、发布时间；进入职位详情核对完整职责与招聘主体。
- 不将上游 `buildSearchUrl` 返回的 `/api/job/search-pc` 当作网页地址；不生成 API key、时间戳或签名。网页不可访问时记录缺口，不改用接口。

## Indeed

- 默认使用国际入口；用户指定地区时选择页面提供的对应站点并记录实际域名。地点可追加编码后的 `&l={location}`，再核对页面显示的地点与远程条件。
- 通过页面筛选日期、岗位类型、薪资和排序；提取职位名、公司、地点、薪资、职位详情链接及实际显示的发布时间。
- 保留页面 `viewjob` 等真实链接/职位标识；推荐岗位与自然搜索结果分开。无法确认发布时间时不把索引时间替代它，不点击申请。

## 脉脉

- 此入口是企业人才检索，实际账号可能需要企业权限。核对当前账号可见的搜索框与结果；未开放权限时标记本次不可用，不声称支持所有账号搜索。
- 通过页面筛选职位、公司、地区、行业、经验和学历；提取公开可见姓名/展示名、职业标题、公司、地区、工作经历、资料链接及实际显示的字段。
- 只读取当前账号可见资料，遮挡联系方式保留缺项；不复制 CSRF、会话随机值或接口请求，不点击私信/邀约。

## Upwork

- 默认搜 jobs；人才/freelancers 需求通过页面实际类别入口切换，并在结果中注明类别。
- 通过实际控件筛选技能、类别、预算、客户所在地、经验及发布时间，不自行猜测 `category2_uid` 等 ID。
- 提取项目名、真实详情链接、发布时间、技能、固定预算或小时费率、客户地区及可见验证标记；进入详情核对交付要求和付费方式。
- 固定预算与小时费率分别记录，不将客户历史总支出当作本项目预算；不提交 proposal 或联系客户。

源码参考：[OpenCLI BOSS](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/boss/search.js)、[51job](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/51job/utils.js)、[Indeed](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/indeed/utils.js)、[脉脉](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/maimai/search-talents.js)、[Upwork](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/upwork/utils.js)。
