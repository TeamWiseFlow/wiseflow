# 声明

wxbot 方案完全来自开源项目 https://github.com/jwping/wxbot

wiseflow 并不涉及 wxbot 项目的维护，也不能保证该方案的稳定性和可持续性，请自行评估使用风险。

**任何对本项目代码的使用、阅读、拷贝、修改、分发以及整合都被视为完全阅读并理解、接受如下各项声明，并且以上行为的所有后果均为使用者本人承担，与wxbot、wiseflow项目作者、贡献者、运营者无关！**

  - 1、微信软件的各项产权等归属腾讯公司；
  - 2、使用者应使用自有所有权的微信账号作为 bot 账号，并承担一切使用风险，包括但不限于账号封禁、信息泄露、信息安全以及腾讯公司可能的法律追责等；
  - 3、don't be evil。


# wxbot 配置部署流程（getting started）

## windows用户

  在这里下载对应版本微信客户端和wxbot-sidecar.exe：阿里网盘： https://www.aliyundrive.com/s/4eiNnE4hp4n 提取码: rt25

  然后命令行运行 

  `.\wxbot-sidecar.exe -p 8066`

  也可以参考 [这里](https://github.com/jwping/wxbot?tab=readme-ov-file#231%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%A4%BA%E4%BE%8B) 在 wxbot-sidecar.exe 同级目录构建配置文件，文件内容只需要：

`  {
      "addr": "0.0.0.0:8066"
  }`

  这样之后就可以直接双击 wxbot-sidecar.exe 启动，启动成功后会自动拉起微信 PC 客户端（如果未拉起，请手动打开微信 PC 客户端），此时使用作为 bot 账号的微信扫码登录即可。

  **注意：可以选择“自动登录该设备”，但不要选择“同步最近消息”，否则会导致程序批量处理近期消息，进而批量回复，轻则导致进程阻塞，重则导致微信账号触发风控。**

## mac/linux 用户

### 运行命令拉取镜像

`docker run -itd --name wxbot -e WXBOT_ARGS="-q http://127.0.0.1:8080/qr_callback" -p 8066:8080 registry.cn-shanghai.aliyuncs.com/jwping/wxbot:v1.10.1-9-3.9.8.25`

以上命令参数最好不要改，WXBOT_ARGS部分不写的话，出不来登录二维码链接；

端口映射如果改变的话，需要更改run_tasks.sh 和 run_weixin.sh 两个脚本中'WX_BOT_ENDPOINT'的值。

### 首次登录

docker container启动成功后（终端会出现一行 container id，然后光标换行闪烁），启动如下命令

`docker logs -f wxbot`

_（注意，如果你使用OrbStack，直接用软件界面打开container的日志，可能看不到二维码链接，一定要用系统自带的终端使用上述命令。）_

耐心等待终端输出，这个过程会很漫长，10min 是有的，期间屏幕出现的所有报错信息都可以忽略，不影响后面正常使用。

直到看到 类似  “http://weixin.qq.com/x/QfOfkbfe_P5wdeKNjR7S”  这样的登录二维码链接信息，复制（**注意不要直接打开，那没用！**）

使用二维码生成器（比如草料 https://cli.im/url） 生成一个二维码，用需要的微信扫码登录（仅限个微）

**注意：这里手机上可以选择“自动登录该设备”，但不要选择“同步最近消息”，否则会导致程序批量处理近期消息，进而批量回复，轻则导致进程阻塞，重则导致微信账号触发风控。**

直到logs出现  `Http Server Listen 0.0.0.0:8080` 那就好了，终端里面出现的任何报错信息都可以忽略，不影响正常使用。

好了 `ctrl+C` 退出 终端logs界面，之后终端直接关闭都行。

用作助理的个微小号建议把支付还有服务等都关闭，不要暴露敏感信息，**使用者请风险自担**！

### 再次登录

在macOS或者linux上运行wxbot最适合成功后常开，不要频繁关闭打开，就放在那里就好，反正默认是静默运行，终端正常也不会输出什么信息的。

理论上，关掉container（包括电脑重启），再次启动会自动登录，此时只需要在微信手机端上点同意就行。

如果失败的话， 先运行 `docker logs -f wxbot` 看看是不是要重新登录。

如果看不到让你重新登录的二维码链接信息，尝试

`docker restart wxbot`

**注意：docker restart之前先操作手机上退出 windows 登录，不然 restart 没用**

如果还不行，运行，

`docker rm -f wxbot`

然后用最开始那个运行命令再次创建container，放心image已经在本地，不会再次下载。

### 问题排查

首先logs界面里面出现的任何报错信息都可以忽略，每次启动（包括重启），最长需要10min才能出现 Http Server Listen 0.0.0.0:8080  或者二维码链接，期间任何报错信息都没所谓

如果长时间（大于等于10min）不出任何信息，那可能是出问题了。参考再次登录方案。

`Http Server Listen 0.0.0.0:8080` 之后基本终端界面就不会出新的消息了，这是正常的，这个时候其实可以退出logs，甚至关闭终端。

更多，请参考：https://github.com/jwping/wxbot?tab=readme-ov-file#linux%E4%B8%8Bdocker%E9%83%A8%E7%BD%B2


# 更多有关wxbot的问题请参考原repo

  https://github.com/jwping/wxbot

  作者写的很详细，尤其是接口部分，希望大家能够顺手给作者打个赏。

**<span style="color:red;">声明：wiseflow项目目前不涉及，也永远不会涉及任何对微信客户端的破解，逆向等，我们充分尊重并严格遵守微信的各项协议以及腾讯公司的知识产权，也请广大用户知悉。</span>**

# 使用

完成上述部署可以通过 wxbot 获取信息后，请在本目录（'wiseflow/weixin_mp'）下创建 config.json 文件，内容如下（示意）：

```json
{"01o1g6n53o14gu5": ["新华网", "__all__"]}
```

key 是关注点id，此id 请从 pb 管理界面 （http://127.0.0.1:8090/_/） 中的“focus_points”表中获取，value 是此关注点对应的公众号名称，所有来自此公众号的信息都会关联到这个focus point（即提炼此关注点的内容）。

如果你想配置所有公众号文章都关联某一关注点，请在对应关注点的 value 中填入 `"__all__"` 这一项。

之后就可以在本目录下执行 

```bash
python __init__.py
```

**注意：在这之前保证 pocketbase 和 wxbot 都已经启动**

结果查看页面：http://127.0.0.1:8090/_/ 
