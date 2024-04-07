# WiseFlow Client Backend

# for developers

## 部署

1、建议创建新环境， **python版本为3.10**

2、 安装requirements.txt

## 单独启动数据库

```bash
cd pb
./pocketbase serve
```

注：pb目录下的pb_migrations文件夹保持与repo同步，数据库会自动创建本项目需要的表单，如果不一致，可能导致后面运行失败

pb_data是数据库数据存放目录，如果更改了admin的密码，记得修改.env

## 脚本文件说明

- tasks.sh #这是启动定时爬虫任务的脚本 （本地纯调试后端，这个不启动也行）
- backend.sh #这是启动后端服务的脚本,(默认使用 localhost:7777， 通过 http://localhost:7777/docs/ 查看接口详情)

备注：backend 服务返回格式统一为 dict，`{"flag": int, "result": [{"type": "text", "content": "xxx"}]}`

统一返回flag约定

| flag 码 | 内容              | 
|--------|-----------------|
| -11    | LLM 错误/异常       |
| -7     | 网络请求失败（爬虫或搜索阶段） |
| -6     | 翻译接口失败          |
| -5     | 入参格式错误          |
| -4     | 向量模型错误          |
| -3     | （预留）            | 
| -2     | pb数据库接口失败       | 
| -1     | 未知错误            | 
| 0      | 正常返回            | 
| 1      | （预留）   | 
| 2      | （预留） | 
| 3      | （预留）   | 
| 11     | 用户所处流程正常结束      |
| 21     | 生成了新的文件         |

注： 1、提交后端request status 200 只意味着提交成功，不表示后端完全处理成功，**收到flag 11才表示流程正常结束**，所有运算成功。

2、flag 0 通常意味着虽然所有运算都执行了，但没有任何结果，即没有新文件产生，也没有新的数据提交给数据库。

3、另外对于translation接口，由于是批量处理，存在着部分成功（翻译结果提交数据库并做了关联），部分失败的情况，所以即便是没有收到flag11，也建议重新从pb读一遍数据


## 目录结构

```
backend
├── llms # 大模型的wraper
├── scrapers # 爬虫库
    |—— __init__.py #如果要添加具体网站的专有爬虫，需要把爬虫脚本放在这个文件的同级目录，同时编辑这面的scraper_map字典
    |—— general_scraper.py #通用信源爬虫
    |—— simple_crawler.py #基于gne的快速单一文章网页爬虫
|—— __init__.py # backend主函数
├── background_task.py # 后台任务主程序，如果要定义多个后台任务，请编辑这个文件
├── main.py # 后端服务主程序（fastapi框架）
├── tasks.sh # 后台服务启动脚本
|—— backend.sh # 后端服务启动脚本`
├── embedding.py # embedding模型服务
├── pb_api.py # pb数据库接口
├── general_utils.py # 工具库
├── get_insight.py # 线索分析与提炼模块
├── get_logger.py # logger配置
├── get_report.py # 报告生成模块
├── get_search.py # 基于sogu的搜索实现
├── work_process.py # 后台服务主流程（抓取与提炼）
├── tranlsation_volcengine.py # 基于火山引擎api的翻译模块
```
