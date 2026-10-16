# API 会话导入与管理

X、TikTok、微博通过 `xiaobei-runtime import-session --platform <x|tiktok|weibo> --account <alias> --file <用户授权私有文件>` 导入。文件可以是 Cookie 数组或平台原生会话对象，权限仅当前用户可读写；不从 OpenClaw 或浏览器 profile 取凭据。快手仍使用 `kuaishou-hunter login/login-confirm` 的 HTTP QR/SMS 流程。

导入在临时私有目录执行 auth login 和 auth status，核对新会话与在线用户 ID 一致后才原子写入私有平台状态目录。失败不覆盖旧会话，同一账号别名不允许更换用户；导入新账号用新 alias，不自动改变已有默认账号。多账号业务操作显式传 `--account`。成功后执行对应 hunter check；有 Cookie 不等于通过在线校验。

TikTok 写操作仍要求 ticket_guard_private_key、ticket_guard_encrypt_ticket、ticket_guard_ts_sign 等同次材料；缺项返回只读状态，写工具请求前再次检查。不要补造材料或拼接其他设备的票据。

代理使用明确 PLATFORM_API_<平台大写ID>_PROXY、PLATFORM_API_PROXY 或宿主 HTTPS_PROXY/HTTP_PROXY。凭据与代理值不输出日志。明确会话失效、网络/风控故障、依赖缺失分别报告；不自动重登或重发未知写操作。
