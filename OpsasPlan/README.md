# OpsasPlan

OpsAS 运营助手生成的所有运营计划归档目录。

## 目录结构

| 大类 | 说明 | 对应 Skill |
|---|---|---|
| `song-release/` | 歌曲发布策划 | `opsas-song-release` |
| `cover-selection/` | 翻唱选题 | `opsas-cover-selection` |
| `stream-planning/` | 直播规划 | `opsas-stream-planning` |
| `weekly-schedule/` | 周度排期 | `opsas-weekly-schedule` |
| `promo-pack/` | 推广文案 | `opsas-promo-pack` |
| `campaign-design/` | 活动策划 | `opsas-campaign-design` |
| `content-review/` | 内容审查报告 | `opsas-content-review` |

## 文件命名

`YYYY-MM-DD_<slug>.md` — 当天日期 + ASCII 短标题。

## 文件头（必填）

```yaml
---
category: song-release
title: 契约合唱单曲发布方案
slug: SRNR
created_at: 2026-04-18
plan_type: song-release
tags: [歌曲发布, 契约]
---
```

所有文件可通过前端「运营计划」页面在线查看与编辑。
