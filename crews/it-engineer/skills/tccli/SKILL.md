---
name: tccli
description:
  腾讯云命令行工具速查手册。通过命令行方式管理和操作腾讯云 200+ 云产品资源，
  支持实例查询、启动、停止、域名解析等功能。当用户提到腾讯云、tccli、CVM、
  Lighthouse、DNSPod、VPC、SSL 证书等腾讯云服务操作时触发。
metadata:
  openclaw:
    emoji: ☁️
    requires:
      bins:
        - tccli
---

# TCCLI - 腾讯云命令行工具

> 通过命令行管理腾讯云资源

---

## 简介

TCCLI（Tencent Cloud Command Line Interface）是腾讯云官方提供的命令行工具，支持管理 200+ 云产品。

---

## 安装

```bash
pip3 install tccli
```

## 配置

```bash
# 配置密钥（只需一次）
tccli configure set secretId <your-secret-id>
tccli configure set secretKey <your-secret-key>
tccli configure set region ap-guangzhou
```

---

## 常用服务速查

### 云服务器 (CVM)

| 操作 | 命令 |
|------|------|
| 查看实例列表 | `tccli cvm DescribeInstances` |
| 查看实例状态 | `tccli cvm DescribeInstancesStatus` |
| 查看可用区 | `tccli cvm DescribeZones` |
| 查看地域 | `tccli cvm DescribeRegions` |
| 查看镜像 | `tccli cvm DescribeImages` |
| 启动实例 | `tccli cvm StartInstances --InstanceIds '["ins-xxxxx"]'` |
| 停止实例 | `tccli cvm StopInstances --InstanceIds '["ins-xxxxx"]'` |
| 重启实例 | `tccli cvm RebootInstances --InstanceIds '["ins-xxxxx"]'` |

### 轻量应用服务器 (Lighthouse)

| 操作 | 命令 |
|------|------|
| 查看实例列表 | `tccli lighthouse DescribeInstances` |
| 查看套餐 | `tccli lighthouse DescribeBundles` |
| 查看镜像 | `tccli lighthouse DescribeBlueprints` |
| 查看防火墙规则 | `tccli lighthouse DescribeFirewallRules` |
| 创建防火墙规则 | `tccli lighthouse CreateFirewallRules --InstanceId ins-xxxxx --FirewallRules '[{"Protocol":"TCP","Port":"80","Action":"ACCEPT"}]'` |

### SSL 证书

| 操作 | 命令 |
|------|------|
| 查看证书列表 | `tccli ssl DescribeCertificates` |
| 查看证书详情 | `tccli ssl DescribeCertificate --CertificateId xxx` |
| 下载证书 | `tccli ssl DownloadCertificate --CertificateId xxx` |
| 部署证书 | `tccli ssl DeployCertificateInstance ...` |

### DNSPod (域名解析)

| 操作 | 命令 |
|------|------|
| 查看域名列表 | `tccli dnspod DescribeDomainList` |
| 查看域名详情 | `tccli dnspod DescribeDomain --Domain example.com` |
| 查看记录列表 | `tccli dnspod DescribeRecordList --Domain example.com` |
| 创建记录 | `tccli dnspod CreateRecord --Domain example.com --RecordType A --RecordLine 默认 --Value 1.2.3.4` |

### 私有网络 (VPC)

| 操作 | 命令 |
|------|------|
| 查看 VPC 列表 | `tccli vpc DescribeVpcs` |
| 查看子网列表 | `tccli vpc DescribeSubnets` |
| 查看安全组 | `tccli vpc DescribeSecurityGroups` |
| 查看安全组规则 | `tccli vpc DescribeSecurityGroupPolicies --SecurityGroupId sg-xxxxx` |

### 域名注册

| 操作 | 命令 |
|------|------|
| 查看域名列表 | `tccli domain DescribeDomainNameList` |
| 检查域名 | `tccli domain CheckDomain --DomainName example.com` |
| 查看价格 | `tccli domain DescribeDomainPriceList` |

### 云监控 (Monitor)

| 操作 | 命令 |
|------|------|
| 查看指标数据 | `tccli monitor GetMonitorData` |
| 查看告警策略 | `tccli monitor DescribeAlarmPolicies` |

---

## 输出格式

```bash
# JSON 格式（默认）
tccli cvm DescribeInstances

# 表格格式
tccli cvm DescribeInstances --output table

# 文本格式
tccli cvm DescribeInstances --output text
```

---

## 帮助命令

```bash
# 查看所有服务
tccli help

# 查看服务详情
tccli cvm help
tccli ssl help
tccli lighthouse help

# 查看具体接口
tccli cvm DescribeInstances help
```

---

## 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--Region` | 指定地域 | `--Region ap-shanghai` |
| `--output` | 输出格式 | `--output table` |
| `--filter` | 过滤结果 | `--filter 'Instances[0].InstanceId'` |
| `--cli-unfold-argument` | 展开参数 | 用于复杂嵌套参数 |

---

## 使用示例

### 获取第一个实例的公网 IP
```bash
tccli cvm DescribeInstances --filter 'Instances[0].PublicIpAddresses[0]'
```

### 查看所有运行中的实例
```bash
tccli cvm DescribeInstances --Filters '[{"Name":"instance-state","Values":["RUNNING"]}]'
```

### 批量查询多个实例
```bash
tccli cvm DescribeInstances --InstanceIds '["ins-xxx1","ins-xxx2"]' --output table
```

---

## 完整服务列表

TCCLI 支持 200+ 云服务，常用包括：

| 服务代码 | 服务名称 |
|----------|----------|
| cvm | 云服务器 |
| lighthouse | 轻量应用服务器 |
| vpc | 私有网络 |
| ssl | SSL 证书 |
| dnspod | DNS 解析 |
| domain | 域名注册 |
| cdn | 内容分发网络 |
| cls | 日志服务 |
| cos | 对象存储 |
| monitor | 云监控 |
| cam | 访问管理 |
| cdb | 云数据库 MySQL |
| redis | 云数据库 Redis |
| mongodb | 云数据库 MongoDB |
| tke | 容器服务 |
| scf | 云函数 |

---

## 安全注意事项

- **最小权限原则**：配置的 API 密钥应仅授予所需的最小权限，避免使用主账号密钥
- **密钥保护**：不要在共享终端、日志、截图或代码仓库中暴露 secretId / secretKey
- **写操作确认**：执行变更类命令（启停实例、修改防火墙、部署证书、创建 DNS 记录等）前，务必确认目标账号、地域、资源 ID 和操作意图
- **区域确认**：执行写操作前确认 `--Region` 参数正确，避免误操作其他地域的资源

---

## 参考文档

- [TCCLI 官方文档](https://cloud.tencent.com/document/product/440/34011)
- [TCCLI GitHub](https://github.com/TencentCloud/tencentcloud-cli)
