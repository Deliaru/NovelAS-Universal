# 记忆工具参考

涵盖 2 种记忆和回顾能力：构建情节记忆 / 生成叙事回顾。

两者共享 Job Routing 批量处理模式（参见 SKILL.md 共享约定）。

---

## 构建情节记忆（记忆建筑师 / Memory Architect）

将每章的关键情节提取后存入向量数据库，供后续逻辑验证和回顾使用。

### 参数
- `start_chapter`（首次运行**必填**）：起始章节编号
- `end_chapter`（首次运行**必填**）：结束章节编号
- `volume`（默认：`1`）
- `include_interludes`（默认：`true`）：是否处理间章
- `job_id`（可选）：断点续传用；提供时不需要 start/end_chapter

### 章节文件名解析
- `Chapter.001` → chapter_type="Chapter", chapter=1
- `Interlude.000` → chapter_type="Interlude", chapter=0
- `Extra.000` → chapter_type="Extra", chapter=0

### 执行步骤

1. **Job Routing**（遵循 SKILL.md 共享约定）：
   - 有 job_id → `claim_next_batch(job_id)`
   - 无 job_id → `calculate_chapter_batches(volume, max_chars=50000, start_chapter, end_chapter)` → 获取 job_id → `claim_next_batch`

2. **逐章处理**（对 chapters 列表循环）：
   - 解析文件名 → 提取 chapter_type 和 chapter_number
   - `read_chapter_content(volume, chapter=N, chapter_type="...")`
   - **深度分析与提取**：
     - 一句话梗概：本章发生了什么
     - 关键事件 (Events)：导致剧情转向的节点
     - 伏笔 (Foreshadowing)：暗示未来的细节（标记 🚩）
     - 伏笔回收 (Payoff)：兑现了之前哪个伏笔（标记 🏁）
     - 人物状态变更：如"某人受伤"、"某人获得新技能"

3. **向量化存储**：对**每一条**提取的关键信息，调用：
   ```
   store_plot_memory(
     content="提取的信息文本",
     metadata_json={
       "volume": V,
       "chapter": N,
       "chapter_type": "Chapter",
       "type": "event | foreshadowing | payoff | character_state",
       "characters": ["角色名列表"]
     }
   )
   ```

4. **循环控制**：
   - `is_last_batch` 为 true → "✅ **全部章节处理完毕。向量记忆库已更新。**"
   - `is_last_batch` 为 false → "⚠️ **批次处理完毕（防止幻觉）。请执行 `/clear` 后运行：**"
     `/novel-assistant build_memory job_id="[job_id]"`

### 🚀 Agent Team 并行处理（推荐）

对于大量章节的处理，**强烈推荐**使用 Agent Team 并行处理模式，可大幅提升效率。

**工作原理：**
- 每个 Agent 独立调用 `claim_next_batch(job_id)` 自动领取不同批次
- 后端批次分配机制确保无冲突
- 各 Agent 在独立上下文中并行处理，避免 token 累积

**使用步骤：**

1. **创建任务并获取 job_id：**
   ```
   /novel-assistant build_memory volume=1 start_chapter=1 end_chapter=10
   ```
   系统返回 `job_id`（如 `"0b15c97b"`）

2. **启动多个并行 Agent：**
   ```python
   # 启动 N 个 Agent（建议 3-8 个，根据批次数量调整）
   for i in range(N):
       Agent(
           description="处理记忆构建",
           prompt="""你是小说记忆构建助手。

           任务：为当前项目构建情节记忆。

           执行步骤：
           1. 调用 claim_next_batch(job_id="[job_id]") 领取批次
           2. 读取该批次的所有章节
           3. 提取关键情节（事件/伏笔🚩/回收🏁/角色状态）
           4. 使用 store_plot_memory 存储，参数：
              - slug="{slug}"
              - content: 情节描述
              - metadata_json: {"volume": N, "chapter": N, "chapter_type": "...",
                                "type": "event/foreshadowing/payoff/character_state",
                                "characters": [...]}
           5. 完成后报告批次编号和章节数量

           注意：
           - 只处理一个批次即可
           - 如果领取失败，直接报告
           """,
           run_in_background=true
       )
   ```

3. **等待完成：**
   - 系统会自动通知每个 Agent 完成
   - 所有 Agent 完成后，任务结束

**性能对比：**
- 单线程处理：需要多次 `/clear` 续传，容易中断
- Agent Team：自动并行，无需人工干预，速度提升 N 倍

---

## 生成叙事回顾（吟游诗人 / The Bard）

将一系列章节转化为兼具条理性和可读性的叙事回顾，帮助作者快速找回"感觉"。

### 参数
- `volume`（默认：`1`）
- `start_chapter`（可选）
- `end_chapter`（可选）
- `include_interludes`（默认：`true`）：是否包含间章
- `include_extras`（默认：`false`）：是否包含番外
- `job_id`（可选）：断点续传用

### 执行步骤

1. **Job Routing**：同「构建情节记忆」

2. **读取章节**（对 chapters 列表循环）：
   - 解析文件名 → 提取 chapter_type 和 chapter_number
   - `read_chapter_content(volume, chapter=N, chapter_type="...")`
   - 根据 include_interludes / include_extras 参数跳过对应类型

3. **编织时间线**：
   - 格式：`[Chapter.NNN / Interlude.NNN] 时间/地点: 关键事件`
   - 标记伏笔埋藏点（🚩）和回收点（🏁）
   - 间章用 `[Interlude.NNN - 标题]` 标记，与主线有机穿插

4. **撰写叙事梗概**：
   - 读取文风指导书（`project_guides/style_guide.md`）
   - **模仿原书文风**，将时间线改写为连贯的短篇概括
   - 将间章内容有机融入叙事

5. **保存**：
   - 文件名：`recap_vol{V}_ch{S}-{E}.md`（多批次加 `_part1` 后缀）
   - `update_knowledge_file(filename, content, subdir="project_guides")`

6. **循环控制**：
   - 最后一批 → "✅ **全卷回顾生成完毕。**"
   - 非最后一批 → 提示续传命令

### 输出结构示例

```markdown
# 第一卷：xxx（Chapter.001 - Chapter.010 回顾）

## ⏳ 核心时间线
- [Prologue] xxx: 主角苏醒，遭遇xxx。
- [Chapter.003] xxx: 🚩 捡到神秘道具（后续揭示为"关键物品"）。
- [Interlude.000] 第三视角: 远处有人在监视主角的行动。
- [Chapter.005] xxx: 🏁 道具被确认是核心设定的关键凭证。

## 📜 叙事梗概
（模仿原书文风的叙述）
```
