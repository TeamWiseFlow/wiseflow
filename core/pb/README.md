# for developer

如果你只是用户，无需关注这个文件夹。

对于python开发者，请使用  backend/pb_api.py 模块进行数据库操作

对于js开发者，可以直接启动数据库后，在数据库各个collection页面中的api详情查看接口说明

```bash
cd pb
./pocketbase --dev admin create test@example.com 123467890 #如果没有初始账号，请用这个命令创建
./pocketbase serve
```