# crew-list

**触发条件**：用户请求查看内部团队成员列表，或询问当前有哪些专员可用。

## 功能说明
列出所有已注册的**内部 Crew** 实例，显示其路由模式、渠道绑定和运行状态。

**注意**：对外 Crew（customer-service 等）不在此列表中，由 HRBP 管理。

## 执行步骤

1. 运行脚本：`./skills/crew-list/scripts/list-internal-crews.sh`
2. 将输出展示给用户
3. 如发现异常（workspace 缺失、无绑定等），向用户说明

## 脚本说明

```bash
./skills/crew-list/scripts/list-internal-crews.sh
```

## 示例输出

```
# Internal Crew Directory

| ID | Name | Route | Bindings | Status |
|----|------|-------|----------|--------|
| hrbp | HRBP | spawn | — | active |
| it-engineer | IT Engineer | both | feishu:it-engineer-bot | active |
```
