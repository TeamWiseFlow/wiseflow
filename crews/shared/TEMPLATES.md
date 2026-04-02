# Shared Templates

## Closeout Template

```
## Closeout: {task-title}

**Type**: {Q|A|P|S}
**Result**: {one-line summary}
**Deliverables**: {list of outputs}
**Decisions made**: {key choices and rationale}
**值得沉淀**: {yes/no — if yes, what insight is reusable}
**Follow-ups**: {any next steps or open items}
```

## Checkpoint Template

For P-class tasks, report progress at natural breakpoints:

```
## Checkpoint: {task-title} — {phase}

**Progress**: {what's done}
**Next**: {what's coming}
**Blockers**: {any issues}
**ETA shift**: {on track / delayed — reason}
```

## Internal Crew Roster Entry (Main Agent MEMORY.md)

```
| ID | Name | Template | Type | Route Mode | Bound Channels | Status |
|----|------|----------|------|------------|----------------|--------|
```

Type values: `internal`
Route Mode values: `spawn` / `binding` / `both`

## External Crew Registry Entry (HRBP EXTERNAL_CREW_REGISTRY.md)

```
| Instance ID | Template | 类型 | 渠道绑定 | 创建日期 | 状态 | 备注 |
|-------------|----------|------|---------|---------|------|------|
```

Type values: `external`
