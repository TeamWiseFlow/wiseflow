# hrbp-feedback-review

**触发条件**：用户请求分析对外 Crew 的表现，或 HRBP 定期自主检查外部 Crew 反馈。

## 功能说明
扫描所有活跃对外 Crew 实例的 `feedback/` 目录，聚合反馈数据，生成分析报告，并提出升级建议。

## 执行步骤

```
1. 读取 EXTERNAL_CREW_REGISTRY.md 获取所有活跃对外 Crew 实例列表
2. 对每个实例运行: bash ./skills/hrbp-feedback-review/scripts/scan-feedback.sh <instance-id>
3. 汇总分析：
   - 反馈总数
   - 未解决问题数量和分类
   - 高频投诉类别
   - 用户情绪分布
4. 生成改进建议并展示给用户（L3 确认后再应用）
```

## 脚本用法

```bash
# 扫描单个实例的反馈
bash ./skills/hrbp-feedback-review/scripts/scan-feedback.sh <instance-id>

# 扫描所有实例（需要 EXTERNAL_CREW_REGISTRY 存在）
bash ./skills/hrbp-feedback-review/scripts/scan-feedback.sh --all
```

## 输出格式示例

```
# Feedback Summary: cs-product-a (2026-03-01 to 2026-03-15)

总反馈条目: 12
  - 已解决: 8
  - 未解决: 3
  - 已升级: 1

问题分类:
  - 投诉: 5 (其中未解决 2)
  - 咨询: 6
  - 请求: 1

高频问题:
  1. 退款流程不清晰 (3次)
  2. 产品规格咨询无法解答 (2次)

建议:
  - MEMORY.md 增加退款流程指引
  - DECLARED_SKILLS 考虑加入 ordercli 以查询订单状态
```
