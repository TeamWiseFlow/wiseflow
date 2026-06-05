---
name: alicloud-find-skills
description:
  搜索、发现和安装阿里云 Agent Skills。当用户提到阿里云、alicloud、aliyun、
  ECS、RDS、OSS 等阿里云服务操作或需要查找阿里云相关 skill 时触发。
  典型触发词："找阿里云 skill"、"搜索 alicloud skills"、"有没有管理 ECS 的 skill"、
  "阿里云 skills 有哪些类目"、"安装阿里云 skill"。
metadata:
  openclaw:
    emoji: ☁️
    requires:
      bins:
        - aliyun
---

# 阿里云 Agent Skills 搜索与发现

> 通过 Aliyun CLI 的 `agentexplorer` 插件搜索、浏览和安装阿里云官方 Agent Skills。

---

## 前置条件

### 1. Aliyun CLI >= 3.3.3

```bash
aliyun version
```

如未安装或版本过低：

```bash
# macOS
brew install aliyun-cli

# Linux (x86_64)
curl -fsSL https://aliyuncli.alicdn.com/aliyun-cli-linux-latest-amd64.tgz -o /tmp/aliyun-cli.tgz
tar -xzf /tmp/aliyun-cli.tgz -C /tmp
sudo mv /tmp/aliyun /usr/local/bin/

# Linux (ARM64)
curl -fsSL https://aliyuncli.alicdn.com/aliyun-cli-linux-latest-arm64.tgz -o /tmp/aliyun-cli.tgz
tar -xzf /tmp/aliyun-cli.tgz -C /tmp
sudo mv /tmp/aliyun /usr/local/bin/
```

> ⚠️ **安全提示**：避免使用 `curl | bash` 管道安装模式。先下载脚本审查内容再执行更安全。

### 2. 认证配置

```bash
aliyun configure list
```

**安全规则**：
- **禁止**读取、回显或打印 AK/SK 值（`echo $ALIBABA_CLOUD_ACCESS_KEY_ID` 严禁执行）
- **禁止**在对话中要求用户直接输入 AK/SK
- **禁止**使用 `aliyun configure set` 传入明文凭据值
- **仅用** `aliyun configure list` 检查凭据状态

如无有效 profile，告知用户：
1. 在 [RAM 控制台](https://ram.console.aliyun.com/manage/ak) 获取 AccessKey
2. 在终端中执行 `aliyun configure` 完成配置（不在当前会话中操作）
3. 配置完成后返回继续

### 3. 插件安装

```bash
# 启用自动插件安装
aliyun configure set --auto-plugin-install true

# 安装 agentexplorer 插件
aliyun plugin update
aliyun plugin install --names agentexplorer

# 验证
aliyun plugin list | grep agentexplorer
```

---

## API 调用规范

所有 `aliyun agentexplorer` 命令**必须**携带以下标志：

| 标志 | 值 | 说明 |
|------|---|------|
| `--endpoint` | `agentexplorer.aliyuncs.com` | 固定端点 |
| `--user-agent` | `AlibabaCloud-Agent-Skills/alicloud-find-skills` | 请求标识 |

> 本地管理命令（`aliyun configure`、`aliyun plugin`、`aliyun version`）**不支持** `--user-agent` 标志。

---

## 核心工作流

### Step 1: 理解需求

分析用户请求，提取：
- **领域**：ECS、RDS、OSS、SLS、PAI 等
- **任务**：诊断、部署、数据同步、权限审查等
- **搜索意图**：将用户需求转化为能力导向的搜索短语

### Step 2: 搜索 Skills

```bash
# 语义搜索（默认，按意图匹配）
aliyun agentexplorer search-skills \
  --keyword "<用户意图>" \
  --search-mode semantic \
  --max-results 20 \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills

# 关键词搜索
aliyun agentexplorer search-skills \
  --keyword "<产品关键词>" \
  --search-mode semantic \
  --max-results 20 \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills

# 浏览类目
aliyun agentexplorer list-categories \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills

# 按类目列出 skills
aliyun agentexplorer search-skills \
  --category-code "<category-code>" \
  --max-results 20 \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills

# 类目 + 语义组合搜索
aliyun agentexplorer search-skills \
  --keyword "<意图>" \
  --category-code "<category-code>" \
  --search-mode semantic \
  --max-results 20 \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills
```

### Step 3: 迭代搜索

首次搜索无明确匹配时，自动调整策略重试：
1. 提取产品/任务关键词
2. 中英文切换（"云服务器" → "ECS"，"对象存储" → "OSS"）
3. 简化关键词（"RDS 备份自动化" → "RDS"）
4. 先 `list-categories` 定位类目，再组合搜索
5. 尝试同义词（"实例" → "ECS"，"桶" → "OSS"）

每个搜索意图单元至少尝试一次能力导向搜索后才可声明"无对应 Skill"。

### Step 4: 查看详情（可选）

```bash
aliyun agentexplorer get-skill-content \
  --skill-name "<skill-name>" \
  --endpoint 'agentexplorer.aliyuncs.com' \
  --user-agent AlibabaCloud-Agent-Skills/alicloud-find-skills
```

### Step 5: 安装（仅用户要求时）

```bash
# OpenClaw 生态安装
npx clawhub install <selected-skill-name>

# 或通过 npx skills add
npx skills add aliyun/alibabacloud-aiops-skills \
  --skill <skill-name> \
  --full-depth \
  --agent qwen-code \
  -g -y
```

> ⚠️ **安装前审查**：建议先用 `get-skill-content` 查看待安装 skill 的内容，确认安全后再安装。

安装后验证 skill 出现在可用列表中。

---

## RAM 权限

本 skill 仅使用只读 API，所需最小权限：

| API | 权限 | 风险级别 |
|-----|------|---------|
| `ListCategories` | `agentexplorer:ListCategories` | Low（只读，公开数据） |
| `SearchSkills` | `agentexplorer:SearchSkills` | Low（只读，公开数据） |
| `GetSkillContent` | `agentexplorer:GetSkillContent` | Low（只读，公开数据） |

最小 RAM 策略：

```json
{
  "Version": "1",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "agentexplorer:ListCategories",
      "agentexplorer:SearchSkills",
      "agentexplorer:GetSkillContent"
    ],
    "Resource": "*"
  }]
}
```

权限错误时：告知用户所需权限 → 暂停等待用户授权 → 确认后继续。

---

## 常用场景示例

| 用户请求 | 搜索命令 |
|---------|---------|
| "找管理 ECS 的 skill" | `--keyword "管理ECS实例" --search-mode semantic` |
| "阿里云数据库相关 skill" | `--keyword "数据库管理" --search-mode semantic` |
| "有哪些类目" | `list-categories` |
| "计算类目下的 skills" | `--category-code "computing"` |
| "OSS 文件同步" | `--keyword "OSS文件同步" --search-mode semantic` |

---

## 安全注意事项

- **最小权限**：仅使用 3 个只读 API 权限，不涉及任何写操作
- **凭据保护**：严禁暴露 AK/SK，严禁在会话中配置凭据
- **子 skill 审查**：本 skill 引导安装其他 skill，安装前务必审查内容
- **安装风险**：`npx` 会从 npm 下载执行代码，确认包来源可信后再安装
- **CLI 安装**：优先使用包管理器（brew / 手动下载二进制）而非 `curl | bash`
