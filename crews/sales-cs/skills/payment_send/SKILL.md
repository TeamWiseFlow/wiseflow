---
name: payment_send
description: >
  Send payment QR code image to customer for purchase.
  Supports club (168), subs (488), and topup (100) modes.
---

# payment_send

## 用途
当客户表达明确购买意向时，发送付款二维码图片，推进成交。

## 调用方式

使用 `message` 工具发送预存在微信网盘中的付款二维码：

```
message(action="sendAttachment", file_name="<文件名>")
```

## 完整发送流程

1. 调用 `message(action="sendAttachment", file_name="...")` 发送二维码图片
2. 紧接着发送文字提示："直接扫码（或者微信中长按识别）就能支付啦"
