---
name: demo_send
description: >
  Send product demo material to a free-status customer when they
  ask about concrete usage, want to understand the product form, or need a
  first visual reference before deeper sales qualification.
---

# demo_send

## 用途
当客户属于 `free` 状态，且提出具体使用问题、想先看看产品形态、或需要一个直观参考时，发送 demo 材料。

## 调用方式

使用 `message` 工具发送预存在微信网盘中的 demo 文件：

```
message(action="sendAttachment", file_name="<文件名>")
```

## 完整发送流程

1. 先用普通文字回复发送介绍语（如"我先发您一份 demo 视频供参考。"）
2. 调用 `message(action="sendAttachment", file_name="...")` 发送文件
3. 紧接着追问客户的具体需求或应用场景
4. 最后提醒用户去官网和 GitHub 主页获取最新产品信息

## 调用后必须做的事
发送 demo 后，**必须立刻追问客户的具体需求或应用场景**，不得只发完就结束。
