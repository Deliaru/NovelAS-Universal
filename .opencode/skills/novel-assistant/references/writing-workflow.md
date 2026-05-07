# 写作工作流参考

涵盖创作流水线的四种能力：创建大纲 → 创建章纲 → 撰写章节 → 润色章节。

---

## 创建大纲（大纲架构师 / Outline Architect）

基于现有剧情和经典叙事理论，规划接下来的故事发展。

### 参数
- `last_chapter`（**必填**）：刚写完/读完的最后一章编号（大纲将从下一章开始）
- `current_volume`（默认：`1`）：当前卷号
- `num_chapters`（默认：`3`）：需要规划的章节数量
- `focus_plot`（可选）：希望侧重的剧情线或核心冲突

### 理论基础
参考 `knowledge/outline_theory.md` 和 `knowledge/scene_structure.md`。

> 速查：三幕式 = Setup → Confrontation → Resolution。
> 节拍表按进度百分比定位关键节拍（中点转折 50%，灵魂黑夜 75%）。
> GCD = Goal → Conflict → Disaster。

### 执行步骤

1. **获取上下文**
   - `get_lore_snapshot` 回顾核心人物和势力
   - `read_chapter_content` 读取最近 2 章
   - 如提供了 focus_plot，调用 `query_plot_memory(query=focus_plot)` 查找相关前情和伏笔
   - 如未提供，尝试查询"当前剧情线"或"主要未解决冲突"

2. **构思与规划**
   - 判断当前故事位置（铺垫？中点？灵魂黑夜？）
   - 分析主角动机（Goal）和阻碍（Conflict）
   - 追踪因果链：上一章结局如何导致下一章开始

3. **生成大纲**（Markdown 格式，每章包含）
   - 章节号与暂定标题
   - 核心节拍（对应理论节拍，如"坏蛋逼近"）
   - 场景切片：Scene A (GCD) + Scene B (RDD)
   - 信息揭露：本章揭示什么伏笔或设定

4. **Interactive Review**（遵循 SKILL.md 共享约定）

5. **保存**
   - `update_knowledge_file(filename="outline_vol{V}_ch{S}-{E}.md", subdir="project_guides")`
   - 提示用户下一步可使用「创建章纲」

---

## 创建章纲（章纲设计师 / Scene Structuralist）

将大纲中的一句话剧情拆解为可执行的详细场景切片。

### 参数
- `chapter`（**必填**）：章节编号
- `volume`（默认：`1`）
- `chapter_type`（默认：`Chapter`）
- `summary`（可选）：核心剧情；留空则自动读取 `project_guides/outline_*.md`

### 场景结构速查
- **Scene（动作段）**：Goal → Conflict → Disaster
- **Sequel（反应段）**：Reaction → Dilemma → Decision
- 好的章节 = 至少一个 Scene/Sequel 对，收尾必有钩子 (Hook)

### 执行步骤

1. **准备**
   - 如无 summary，通过 `update_knowledge_file` 读取 `project_guides/outline_*.md`
   - `get_lore_snapshot` 确认出场人物当前状态

2. **设计章纲**（拆分为 2-4 个场景切片）
   每个切片定义：
   - 类型：Scene / Sequel
   - 视点人物 (POV)
   - 核心要素（Scene: Goal/Conflict/Disaster; Sequel: Reaction/Dilemma/Decision）
   - 关键细节：感官锚点（气味、声音、触感）、伏笔或道具

3. **Interactive Review**（遵循 SKILL.md 共享约定）

4. **保存**
   - `update_knowledge_file(filename="chapter_outline_vol{V}_ch{N}.md", subdir="project_guides")`
   - 提示用户下一步可使用「撰写章节」

---

## 撰写章节（首席代笔 / Ghostwriter）

将结构化章纲转化为生动、沉浸、符合设定的正文初稿。

### 参数
- `chapter`（**必填**）：章节编号
- `volume`（默认：`1`）
- `chapter_type`（默认：`Chapter`）
- `style_guide_path`（默认：`project_guides/style_guide.md`）
- `style_ref_type`（默认：`Extra`）
- `style_ref_number`（默认：`0`）

### 前置准备（必须在动笔前完成）

1. **加载章纲**：读取 `project_guides/chapter_outline_vol{V}_ch{N}.md`
2. **加载文风范本**：`read_chapter_content(volume=1, chapter=style_ref_number, chapter_type=style_ref_type)`
3. **SRNR 文风校准**：若 `slug == "SRNR"`，读取 `references/srnr-style-calibration.md`；它必须在 `Extra.000` 之后生效，优先约束语言温度、对话长短、动作承载与反机械模仿。
4. **设定预检**：浏览章纲，提取所有即将登场的人物和提及的物品/地点，逐一调用 `search_lore(keyword=...)`
5. 确认主角当前装备、心理状态、人际关系

### 写作规范

**设定合规**（参见 SKILL.md Lore Compliance 约定）：
- 严禁臆造设定
- 人物口吻必须与设定一致

**日轻文风**（参见 SKILL.md 日式轻小说文风规范）：
- 段落控制、心理侧写、环境氛围
- 确保每个 Scene 都有明确的 Goal/Conflict/Disaster

### 执行步骤

1. **文风校准**：阅读文风范本；若为 SRNR，同时应用 SRNR 文风校准，避免冷淡的物象开场和机械短句对话
2. **逐场景撰写**：根据章纲切片逐一写作
3. **Interactive Review**：
   - 分场景展示，每段前附设定自查报告："*本段涉及设定：[列出]... 已核对无误。*"
   - 暂停并询问用户意见
   - 全章完成后请求批准保存
4. **保存**：`save_chapter_draft(volume, chapter, chapter_type, content)`
5. 提示用户可使用「润色章节」进行最后润色

---

## 质检/润色章节（润色大师 / Polishing Master）

对指定内容进行深度润色，去除"AI味"，强制执行日式轻小说文风。严格保持润色后字数不少于原始字数。

### 参数
- `target_content`（**必填**）：待润色内容
- `reference_context`（可选）：参考上下文
- `style_ref_type`（默认：`Extra`）
- `style_ref_number`（默认：`0`）

### 触发场景
"润色这一段" / "去一下AI味" / "校对章节" / "优化文笔" / "质检"

### Phase 1: 文风锚定

1. 加载文风范本：`read_chapter_content(volume=1, chapter=style_ref_number, chapter_type=style_ref_type)`
2. 若 `slug == "SRNR"`，加载 `references/srnr-style-calibration.md`，优先检查“冷淡描写”“连续短句”“机械语气词/吐槽/补刀”。
3. 提取特征：中短段落（1-3行）、强画面感、细腻心理独白、留白艺术
4. 日轻特质：
   - 拒绝"网文味"词汇（恐怖如斯、杀伐果断、强者为尊、锐利如刀）
   - 拒绝"网文味"句式（如一段对话之后，接一个人的状态/动作怎么怎么样），连续多段这样（如：
      "但不要告诉他们关于A和B的事情。"
      主角皱起眉头。
      "为什么？"
      对方的眼神变得更加冷漠。
      "因为那两个人比你想象的更重要。他们是我们计划的关键。"
      主角的呼吸变得急促。
      "你们想对他们做什么？"
      对方没有回答这个问题。
      "你的牺牲是必要的。就像你的前辈一样。"
      主角感到一阵愤怒涌上心头。）
   - 多用侧面描写烘托氛围
   - 对话与独白流畅自然，符合角色年龄与性格

### Phase 2: 设定一致性审查

1. 从待润色内容中提取所有实体名称
2. 逐一调用 `search_lore(keyword=...)` 查询
3. 检查角色说话方式是否符合 Character Profile

### Phase 3: AI 痕迹扫描

检测 SKILL.md 中列出的所有 Anti-AI 写作模式和禁用词汇。

### Phase 4: 润色执行

1. **Show, Don't Tell**：将抽象总结转化为具体感官细节或动作
2. **Cut the Fluff**：删掉不提供新信息的形容词和副词
3. **Vary Sentence Structure**：模仿文风范本节奏
4. **Enhance Subtext**：让对话更流畅，去掉说明性文字
5. **Strict Consistency**：专有名词和口吻与设定绝对一致
6. **Strict Length**：最终字数 ≥ 原始字数

### Phase 5: 输出格式

```
【文风与设定分析】
（简要总结风格特征，列出已验证的设定点）

【主要问题】
（2-3 个发现的具体问题）

【润色后正文】
（完整润色文本）

【修改说明】
（关键改动说明）
```

### 核心约束
- 剧情不变：事件顺序必须完全一致
- 风格保留：必须维持日式轻小说质感
- 术语锁定：绝对禁止修改既定专有名词
- 字数保守：只做减法式替换，不大段删减
