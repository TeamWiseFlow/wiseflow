---
name: alipay-mcp-config
description: >
  Reference guide for system administrators and IT engineers to configure
  the Alipay MCP Server with mcporter. Covers prerequisite setup on
  Alipay Open Platform, credential generation, mcporter.json configuration,
  sandbox testing, and troubleshooting.
metadata:
  {
    "openclaw": {
      "emoji": "💳",
      "audience": "admin"
    }
  }
---

# 支付宝 MCP Server 配置指南

本文档面向系统管理员和 IT 工程师，完整说明如何在 openclaw 环境中通过 mcporter 接入支付宝支付 MCP Server。

---

## 一、前置条件：支付宝开放平台准备

### 1.1 注册并创建应用

1. 登录 [支付宝开放平台](https://open.alipay.com/)
2. 进入「控制台」→「网页&移动应用」→「创建应用」
3. 填写应用名称（如：AI客服支付系统），选择「网页应用」
4. 提交审核并等待上线（沙箱环境无需审核）

### 1.2 开通支付宝支付能力

在应用详情页，找到「添加能力」，添加以下能力：
- **手机网站支付**（`create-mobile-alipay-payment` 需要）
- **电脑网站支付**（`create-web-page-alipay-payment` 需要）
- **退款**（`refund-alipay-payment` 需要）

### 1.3 申请并配置「受限密钥」

支付宝为 AI Agent 场���专门提供**受限密钥**，与常规业务密钥隔离：

1. 应用详情页 → 「开发设置」→「受限密钥」→「查看」
2. 点击「开启支付 MCP Server」开关（**必须开启，否则调用报错 `isv.invalid-cloud-app-permission`**）
3. 在「接口加签方式」中设置密钥：
   - 推荐使用**系统生成密钥**（支付宝帮你生成，更安全）
   - 或使用[支付宝开放平台开发助手](https://opendocs.alipay.com/common/02kirf)本地生成 RSA2 密钥对
4. 完成配置后，记录以下信息：
   - `AP_APP_ID`：应用 APPID（如 `2021xxxxxxxxx8009`）
   - `AP_APP_KEY`：受限密钥对的**私钥**（`MIIEvw...`）
   - `AP_PUB_KEY`：支付宝**服务端公钥**（在「查看」页面获取，`MIIBIjA...`）

> ⚠️ **安全提示**：私钥（`AP_APP_KEY`）务必妥善保管，不得泄露。如已泄露，立即在开放平台使「密钥失效」。

---

## 二、配置 mcporter.json

将 `config-templates/mcporter.json` 复制到 openclaw 网关工作目录下的 `config/` 子目录：

```bash
# openclaw 默认从其运行目录读取 ./config/mcporter.json
cp config-templates/mcporter.json openclaw/config/mcporter.json
```

编辑 `openclaw/config/mcporter.json`，填入真实凭据：

```json
{
  "mcpServers": {
    "alipay": {
      "command": "npx",
      "args": ["-y", "@alipay/mcp-server-alipay"],
      "env": {
        "AP_APP_ID": "2021xxxxxxxxx8009",
        "AP_APP_KEY": "MIIEvwIBADANBgkq...（你的受限私钥）",
        "AP_PUB_KEY": "MIIBIjANBgkqhkiG...（支付宝服务端公钥）",
        "AP_RETURN_URL": "https://your-domain.com/payment/success",
        "AP_NOTIFY_URL": "https://your-domain.com/payment/notify",
        "AP_CURRENT_ENV": "prod",
        "AP_SELECT_TOOLS": "all",
        "AP_LOG_ENABLED": "true"
      }
    }
  }
}
```

### 环境变量完整说明

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `AP_APP_ID` | ✅ | 开放平台应用 APPID | `2021xxxxxxxxx8009` |
| `AP_APP_KEY` | ✅ | 受限密钥对的私钥 | `MIIEvw...kO71sA==` |
| `AP_PUB_KEY` | ✅ | 支付宝服务端公钥 | `MIIBIjA...AQAB` |
| `AP_RETURN_URL` | 可选 | 网页支付成功后同步跳转地址 | `https://example.com/success` |
| `AP_NOTIFY_URL` | 可选 | 支付结果异步通知接收地址 | `https://example.com/notify` |
| `AP_ENCRYPTION_ALGO` | 可选 | 签名算法，默认 `RSA2` | `RSA2` / `RSA` |
| `AP_CURRENT_ENV` | 可选 | 环境，默认 `prod` | `prod` / `sandbox` |
| `AP_SELECT_TOOLS` | 可选 | 允许使用的工具，默认 `all` | 见下方工具列表 |
| `AP_LOG_ENABLED` | 可选 | 是否输出日志，默认 `true` | `~/mcp-server-alipay.log` |
| `AP_INVOKE_AUTH_TOKEN` | 可选 | 服务商三方代调用授权 Token | 仅服务商场景使用 |

### AP_SELECT_TOOLS 工具列表

```
create-mobile-alipay-payment    # 手机支付
create-web-page-alipay-payment  # 网页支付
query-alipay-payment            # 查询支付
refund-alipay-payment           # 发起退款
query-alipay-refund             # 查询退款
```

按需配置示例（只开放支付和查询，不开放退款）：
```json
"AP_SELECT_TOOLS": "create-mobile-alipay-payment,create-web-page-alipay-payment,query-alipay-payment"
```

---

## 三、沙箱环境调试

建议在正式上线前先用沙箱环境验证：

1. 在 [支付宝沙箱控制台](https://open.alipay.com/develop/sandbox/app) 获取沙箱 APPID 和密钥
2. 修改 mcporter.json：
   ```json
   {
     "env": {
       "AP_APP_ID": "沙箱APPID",
       "AP_APP_KEY": "沙箱私钥",
       "AP_PUB_KEY": "沙箱支付宝公钥",
       "AP_CURRENT_ENV": "sandbox"
     }
   }
   ```
3. 使用[支付宝沙箱 App](https://open.alipay.com/develop/sandbox/tool) 扫码测试

---

## 四、验证配置是否生效

启动网关后，用 mcporter 测试连接：

```bash
# 列出所有已配置的 MCP Server
mcporter list

# 查看 alipay server 的可用工具
mcporter list alipay --schema

# 测试查询（用沙箱订单号）
mcporter call alipay.query-alipay-payment outTradeNo=TEST_ORDER_001
```

---

## 五、安全加固建议

### 5.1 限制工具权限
根据业务场景，通过 `AP_SELECT_TOOLS` 只开放必要工具：
- **纯查询场景**：只开放 `query-alipay-payment,query-alipay-refund`
- **完整客服场景**：开放全部工具（`all`）

### 5.2 控制 Agent 访问范围
已在 `config-templates/openclaw.json` 中，通过 `agents.list[].skills` 将 `mcporter` 仅分配给 `customer-service` agent，其他 agent（main/hrbp/it-engineer）的 skills 列表中不包含 `mcporter`，无法调用支付工具。

### 5.3 私钥保护
- **不要**将填写了真实凭据的 mcporter.json 提交到代码仓（已被 `.gitignore` 忽略）
- 考虑通过环境变量注入密钥，而非硬编码在文件中：
  ```bash
  export AP_APP_KEY="MIIEvw..."
  ```
  然后在 mcporter.json 中引用：
  ```json
  "AP_APP_KEY": "${AP_APP_KEY}"
  ```

---

## 六、常见错误排查

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| `isv.invalid-cloud-app-permission` | 支付 MCP Server 开关未开启 | 登录开放平台 → 受限密钥 → 开启「支付 MCP Server」 |
| `isv.missing-signature-key` | 受限密钥未设置接口加签方式 | 在受限密钥详情页完成「接口加签方式」设置 |
| `isv.invalid-signature` | 私钥与公钥不匹配 | 重新生成密钥对，确保私钥和公钥配套 |
| `isv.invalid-open-scene-api-permission` | 未选择要调用的工具 | 在受限密钥详情页勾选要使用的工具 |
| `mcporter: command not found` | mcporter 未安装 | `npm install -g mcporter` |
| MCP Server 启动失败 | `@alipay/mcp-server-alipay` 包问题 | `npx -y @alipay/mcp-server-alipay` 手动测试 |

日志文件位置：`~/mcp-server-alipay.log`

---

## 七、相关文档

- [支付宝 MCP 产品介绍](https://opendocs.alipay.com/open/0h3gdq)
- [支付 MCP 快速开始](https://opendocs.alipay.com/open/0h3irn)
- [支付宝开放平台接入准备](https://opendocs.alipay.com/solution/0ilmhz)
- [密钥配置说明](https://opendocs.alipay.com/common/02kirf)
- [沙箱环境使用指南](https://opendocs.alipay.com/common/02kkv7)
- [mcporter CLI 文档](http://mcporter.dev)
