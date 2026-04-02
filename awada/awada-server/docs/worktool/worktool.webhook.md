# 消息回调接口规范

### QA问答接口回调（高级能力）

由您的技术团队按本接口文档开发一个接口并将接口地址设置绑定到对应机器人id，可以使@机器人回复时使用个性化接口来定制回答。

也就是说由第三方自己接收所有单聊和群聊消息，并进行回答处理。接口开发后调用 “**机器人回调配置-机器人消息回调配置**” 将接口地址设置给机器人。
**注意:** 
- 设置成功后还必须在WTAPP里打开**新消息接收**开关（默认开启）。
- 消息回调接口**必须**在3秒内处理响应，否则平台将放弃本次请求。如果接口确实处理耗时较长，应立即响应，处理消息后异步调用**发送消息**等指令进行回复。
- 消息回调记录可查询“历史消息-机器人消息回调日志列表查询”，包含请求耗时等信息。
- 图片消息需要在WTAPP里打开**图片消息回调**开关（默认关闭）（企微APP需相册权限）。
- 文件消息仅可识别消息类型无法提取内容，如需回调文件等内容需私有化部署并加购企微会话存档功能。


**Path：** 您开发并测试验证过的接口地址(url支持带param参数以区分多个机器人)
测试工具：http://testqa.streamlit.ymdyes.cn

**Method：** POST  application/json

**接口描述：**


### 请求参数


| 参数名称     | 是否必须 | 示例   | 备注                                                       |
| ------------ | -------- | ------ | ---------------------------------------------------------- |
| spoken       | 是       | 你好啊 | 问题文本                                                   |
| rawSpoken| 是       | @me 你好啊 | 原始问题文本                                                   |
| receivedName | 是       | 仑哥 | 提问者名称                                                 |
| groupName    | 是       | 测试群1  | QA所在群名（群聊）                               |
| groupRemark| 是       | 测试群1备注名 | QA所在群备注名（群聊）                               |
| roomType     | 是       | 1      | QA所在房间类型 1=外部群 2=外部联系人 3=内部群 4=内部联系人 |
| atMe| 是       | true     | 是否@机器人（群聊） |
| textType| 是       | 1     | 消息类型 0=未知 1=文本 2=图片 3=语音 5=视频 7=小程序 8=链接 9=文件 13=合并记录 15=带回复文本|
| fileBase64| 是       | iVBORxxx==     | 图片base64 (png)|



### 返回数据

| 名称    | 是否必须 | 示例    | 备注                                        |
| ------- | -------- | ------- | ------------------------------------------- |
| code    | 是       | 0       | 0 调用成功 -1或其他值 调用失败并回复message |
| message | 是       | success | 对本次接口调用的信息描述                    |




### 请求示例（您开发的接口需要支持互联网访问）

**Path：** https://mock.apifox.cn/m1/1035094-0-default/thirdQa

**Method：** POST   application/json
**Body：**
```json
{ 
     "spoken": "你好", 
     "rawSpoken": "@管家 你好", 
     "receivedName": "仑哥",
     "groupName": "测试群1",
     "groupRemark": "测试群1备注名",
     "roomType": 1,
     "atMe": "true",
     "textType": 1
}
```
### 返回数据
```json
{
    "code": 0,
    "message": "参数接收成功"
}
```


### Python代码示例（flask框架）
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/thirdQa', methods=['POST'])
def third_qa():
    # 哦，看来我们有一个大牛想要解析JSON数据
    data = request.json
    # 打印出来，希望你能理解这些
    print("接收到的参数：", data)
    
    # 子线程异步处理消息
    # thread {...}

    # 既然我们已经打印了数据，让我们返回点什么
    return jsonify({"message": "参数接收成功"})

if __name__ == '__main__':
    # 好吧，启动服务器，别告诉我你不知道怎么做
    app.run(debug=True)

```

### Java代码示例（springboot框架）
```java
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api") // 可以根据需要更改路径
public class ApiController {

    @PostMapping("/thirdQa")
    public ResponseEntity<?> thirdQa(@RequestBody RequestData data) {
        // 打印收到的数据，这对我来说是轻而易举的事
        System.out.println("接收到的参数：" + data);

        // 子线程异步处理消息
        // thread {...}

        // 立即返回一个简单的响应
        return ResponseEntity.ok("{\"message\": \"参数接收成功\"}");

    }

    // 假设你知道怎么定义这个类
    public static class RequestData {
        private String spoken;
        private String rawSpoken;
        private String receivedName;
        private String groupName;
        private String groupRemark;
        private String roomType;
        private String atMe;

        // getter和setter方法在这里
        // 但我假设你知道如何生成它们
    }
}

```

