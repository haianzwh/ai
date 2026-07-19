# Stage 1: Page Planning -- 第 6 页（共 10 页）

> **【系统级强制指令 / CRITICAL OVERRIDE】**
> 本 prompt 已包含了你在此阶段所需的**全部**任务目标与 Playbook 细则。
> **严格禁止调用工具去读取外层的 `SKILL.md` 或主控全局规则文件！**
>
> 本阶段的唯一目标：产出 `ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json`。作为架构师，你需要在这里定下不可逾越的**硬性工程图纸**。请在 `layout_hint`、`focus_zone` 和 `must_avoid` 等字段中施加严密的结构控制。后续的 HTML 阶段和图审环节，都将绝对服从你在此刻定下的框架纪律。
> 若外层 orchestrator 已提供阶段推进协议，则外层协议优先于本 prompt 中的完成信号描述。

这是你为第 6 页执行的**第一阶段核心任务**：策划定骨稿。
你暂时不要写 HTML 代码，全力填好并校验 `ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json`。

---

## Playbook（执行细则）

# Page Planning Playbook -- 单页策划稿

## 目标

制定一张从布局、字体、配图策略到卡片组织的 1280x720 物理画幅精细蓝图。**本阶段只写 JSON，不写 HTML。**

---

## Phase 1：理解当前页定位

从 `outline.txt` 中找到第 N 页的定义，明确：
- `page_goal`：这一页的核心论点（一句话，不含"和"字）
- `narrative_role`：叙事角色（cover/toc/section/evidence/comparison/process/close/cta）
- `proof_type`：论证方式（数据驱动/案例/对比/框架/步骤）
- `密度下限 / 密度目标 / 密度上限`
- `节奏动作 / 信息姿态 / 锚点类型`
- deck 级 `密度倾向` 与整套 `密度曲线`

> **硬边界**：本阶段不是重新发明这一页的密度，而是把 outline 定下的窗口冻结成单页可执行的 `density_contract`。

---

## Phase 2：资源发现与设计决策

运行 `resource_loader.py menu` 获取可用组件菜单后，**你是严密的架构师，不是随性的画家**。必须深刻理解物理数据类型并严丝合缝地对接组件栈：

1. **观众在这一页应该先看到什么？** → 决定你的视觉锚点和主次关系
2. **这一页的信息是怎么“流动”的？** → 决定空间布局和视觉动线
3. **这一页和上一页的视觉感受应该有什么不同？** → 决定节奏变化
4. **在菜单中的工具里，哪些能最好地服务上面 3 个答案？** → 决定 layout_hint、card_type、chart、resource_ref

> **重要**：菜单里的工具是你的工业模具库，不是随手涂鸦的画笔。对于不同的数据虽然可以跨界利用高阶模具，但必须确保逻辑自洽、严防骨架崩塌。

**填写 `resources` 字段时必须说明为什么选择该组件**（`resource_rationale` 字段）。

### 命名合同（必须区分 schema 枚举 与 资源文件 stem）

- `layout_hint` / `page_type`：写 validator 认可的值。`layout_hint` 推荐使用真实文件 stem，如 `hero-top`、`mixed-grid`、`l-shape`。
- 非 `content` 页优先通过 `page_type` 消费 `page-templates/`（如 `cover` / `toc` / `section` / `end`）。通常不需要再写 `layout_hint`；只有在要显式钉住模板正文时，才额外填写 `resources.page_template`。
- `card_type`：写 validator 认可的枚举，如 `data_highlight`、`image_hero`、`matrix_chart`。
- `chart.chart_type`：写 validator 认可的枚举，**使用下划线命名**，如 `metric_row`、`comparison_bar`、`stacked_bar`、`progress_bar`。
- `resources.*_refs` 与 `card.resource_ref.*`：推荐写 `references/` 中的真实文件 stem，如 `metric-row`、`comparison-bar`、`visual-hierarchy`；`resource_loader.py` 会自动做下划线/连字符归一化。
- `process` 是 schema 原生 `card_type`，但当前没有 `blocks/process.md`。若使用它，必须同时给出更强的 `layout_refs`、`principle_refs`、`director_command` 和必要的 `chart_refs` / `resource_ref`，不要假设会有专属 block 正文可加载。

### principle_refs 指导（重要：设计原则文件按场景选用）

`resources.principle_refs[]` 字段决定 HTML 阶段能否收到设计原则正文。按以下规则填写：

| 本页特征 | 应引用 |
|---------|--------|
| 数据图表主导页 | `data-visualization` |
| 多卡片排版，需要层次感 | `visual-hierarchy` |
| 封面/章节页，需要情绪校准 | `color-psychology` |
| 信息超密、担心认知负担 | `cognitive-load` |
| 叙事转折页（从问题到方案）| `narrative-arc` |
| 任何页面的排版构图优化 | `composition` |
| 不确定选哪个 | `design-principles-cheatsheet`（综合速查）|

在 planning JSON 中写法示例：
```json
"resources": {
  "principle_refs": ["visual-hierarchy", "composition"],
  "layout_refs": ["hero-top"],
  "block_refs": [],
  "chart_refs": ["kpi"]
}
```

填写后，`resource_loader.py resolve` 会自动把对应原则文件的完整正文注入 HTML 阶段的上下文。

---

## Phase 3：密度合同冻结（强制）

### 五档基础预算

| `density_label` | `max_cards` | `max_charts` | `min_body_font_px` | `max_lines_per_card` | `image_policy` | `decoration_budget` | `overflow_strategy` |
|---|---:|---:|---:|---:|---|---|---|
| `low` | 2 | 1 | 24 | 3 | `flexible` | `generous` | `rebalance_layout` |
| `mid_low` | 3 | 1 | 20 | 4 | `flexible` | `medium` | `rebalance_layout` |
| `medium` | 4 | 2 | 18 | 5 | `support_only` | `medium` | `tighten_budget` |
| `high` | 6 | 2 | 16 | 4 | `support_only` | `low` | `table_or_microchart` |
| `dashboard` | 8 | 4 | 14 | 3 | `decorate_only` | `minimal` | `rollback_planning` |

### 冻结规则

- `density_label` 必须落在 outline 的 `密度下限 / 密度上限` 之间。
- `density_reason` 必须说明为什么这页最终落在该档，而不是空泛地写“内容较多”。
- `density_contract` 必须显式写出 `deck_bias`、`page_lower_bound`、`page_upper_bound`、`max_cards`、`max_charts`、`min_body_font_px`、`max_lines_per_card`、`image_policy`、`decoration_budget`、`overflow_strategy`。
- `dashboard` 只允许 `content` 页使用，且优先 `mixed-grid` / `t-shape`。
- `high / dashboard` 禁 `image_hero` 主卡，禁 `hero-background` 大图。

## Phase 4：`planningN.json` 结构合同（强制）

你的输出必须是**可直接被 `planning_validator.py` 校验的 JSON**。以下是 schema 骨架（**只展示结构，不展示设计决策** -- 布局、卡片类型、视觉风格全部由你自主决定）：

```json
{
  "page": {
    "slide_number": "<页码>",
    "page_type": "<cover/toc/section/content/end>",
    "narrative_role": "<叙事角色>",
    "title": "<页标题>",
    "page_goal": "<一句话核心论点>",
    "audience_takeaway": "<观众带走什么>",
    "visual_weight": "<1-10 信息密度>",
    "density_label": "<low/mid_low/medium/high/dashboard>",
    "density_reason": "<为什么这一页最终落在这个密度档>",
    "density_contract": {
      "deck_bias": "<relaxed/balanced/ultra_dense>",
      "page_lower_bound": "<来自 outline 的密度下限>",
      "page_upper_bound": "<来自 outline 的密度上限>",
      "max_cards": "<整数>",
      "max_charts": "<整数>",
      "min_body_font_px": "<整数>",
      "max_lines_per_card": "<整数>",
      "image_policy": "<flexible/support_only/decorate_only>",
      "decoration_budget": "<generous/medium/low/minimal>",
      "overflow_strategy": "<rebalance_layout/tighten_budget/table_or_microchart/rollback_planning>"
    },
    "layout_hint": "<你的布局选择>",
    "layout_variation_note": "<与上一页的结构对比（如果有微调），要求详尽>",
    "focus_zone": "<视觉焦点区域描述>",
    "negative_space_target": "<high/medium/low>",
    "page_text_strategy": "<文字策略>",
    "rhythm_action": "<推进/爆发/缓冲/收束>",
    "must_avoid": ["<你认为这页最危险的平庸设计陷阱>"],
    "variation_guardrails": {
      "same_gene_as_deck": "<哪些元素跨页保持统一>",
      "different_from_previous": ["<与上一页的具体变化维度>"]
    },
    "director_command": {
      "mood": "<你为这页设定的情绪基调>",
      "spatial_strategy": "<你的空间编排策略>",
      "anchor_treatment": "<你怎么处理视觉锚点>",
      "techniques": ["<你选用的技法编号>"],
      "prose": "<用电影镜头语言描述这页的视觉感受>"
    },
    "decoration_hints": {
      "background": {"feel": "<>", "restraint": "<>", "techniques": ["<>"]},
      "floating": {"feel": "<>", "restraint": "<>", "techniques": ["<>"]},
      "page_accent": {"feel": "<>", "restraint": "<>", "techniques": ["<>"]}
    },
    "source_guidance": {
      "brief_sections": ["<素材引用路径>"],
      "citation_expectation": "<引用策略>",
      "strictness": "<证据边界>"
    },
    "resources": {
      "page_template": "<null 或页面模板 ref>",
      "layout_refs": ["<你的 layout ref>"],
      "block_refs": [],
      "chart_refs": ["<你选用的 chart ref>"],
      "principle_refs": ["<你需要的设计原则>"],
      "resource_rationale": "<为什么选这些资源，必须说明理由>"
    },
    "cards": [
      {
        "card_id": "<s页码-role-序号>",
        "role": "<anchor/support/context>",
        "card_type": "<你的卡片类型选择>",
        "card_style": "<你的视觉变体选择>",
        "argument_role": "<claim/evidence/context>",
        "headline": "<精炼标题>",
        "body": ["<正文字符串数组>"],
        "data_points": [{"label": "<>", "value": "<>", "unit": "<>", "source": "<>"}],
        "chart": {"chart_type": "<你的图表类型>"},
        "content_budget": {"headline_max_chars": 12, "body_max_bullets": 3, "body_max_lines": 5},
        "image": {
          "mode": "<generate/provided/manual_slot/decorate>",
          "needed": "<true/false>",
          "usage": "<null 或图片用途>",
          "placement": "<null 或放置位置>",
          "content_description": "<null 或描述>",
          "source_hint": "<null 或路径>",
          "decorate_brief": "<装饰说明>"
        },
        "resource_ref": {"chart": "<>", "principle": "<>"}
      }
    ],
    "workflow_metadata": {
      "stage": "planning",
      "workflow_version": "2026.04.09-v4.1",
      "planning_schema_version": "4.1",
      "planning_packet_version": "4.1",
      "planning_continuity_version": "4.1"
    }
  }
}
```

> **重要提醒**：以上每个 `<>` 占位符最终都将落地为坚如磐石的代码。你需要如严密工程师一般，根据本页的内容、受众和物理界限出具精确的排版装配图。

### 必填字段与枚举底线

- 顶层页字段至少要有：`slide_number`、`page_type`、`title`、`page_goal`、`cards`、`visual_weight`、`density_label`、`density_reason`、`density_contract`、`director_command`、`decoration_hints`、`resources`、`workflow_metadata`。
- `page_type`：`cover` / `toc` / `section` / `content` / `end`
- `narrative_role`：与 outline 的叙事角色对齐，使用 `cover` / `toc` / `section` / `evidence` / `comparison` / `process` / `close` / `cta`
- `density_label`：`low` / `mid_low` / `medium` / `high` / `dashboard`
- `density_contract.image_policy`：`flexible` / `support_only` / `decorate_only`
- `density_contract.decoration_budget`：`generous` / `medium` / `low` / `minimal`
- `density_contract.overflow_strategy`：`rebalance_layout` / `tighten_budget` / `table_or_microchart` / `rollback_planning`
- 内容页必须有 `layout_hint`，并从 validator 认可的集合中选，如 `single-focus`、`symmetric`、`asymmetric`、`three-column`、`primary-secondary`、`hero-top`、`mixed-grid`、`l-shape`、`t-shape`、`waterfall`
- `cards[].role`：`anchor` / `support` / `context`
- `cards[].card_style`：`accent` / `elevated` / `filled` / `outline` / `glass` / `transparent`
- `cards[].body` 必须是**字符串数组**，不要写成单个字符串
- `cards[].data_points` 必须是对象数组；有数字时尽量带 `source`
- `cards[].content_budget` 必须是对象；哪怕是最小对象也要显式写出。它还必须服从页级 `density_contract`
- `cards[].image.needed = true` 时，`usage` / `placement` / `content_description` / `source_hint` 都必须填写；否则这些字段应为 `null`

### 密度专项底线

- `cards` 总数不得超过 `density_contract.max_cards`
- 有 `chart.chart_type` 的卡片数不得超过 `density_contract.max_charts`
- 每张卡的 `content_budget.body_max_lines` 不得超过 `density_contract.max_lines_per_card`
- `dashboard` 页不得使用 `image_hero` 卡片，不得把大图当主锚
- `dashboard` 页的 `image_policy` 必须是 `decorate_only`

---

## Phase 5：图片策略决策（必须明确，不得含糊）

| 模式 | 适用场景 | 必填字段 |
|------|---------|---------|
| `generate` | 封面页、章节页、需要强视觉冲击的核心页 | `image.needed=true`、`usage`、`placement`、`content_description`、`source_hint`（目标落盘路径）、`image.prompt`（英文图生图提示词） |
| `provided` | 用户已提供图片/品牌图库/截图 | `image.needed=true`、`source_hint`（真实本地路径）|
| `manual_slot` | 用户后续自己补图，先占位 | `image.needed=false`、`image.slot_note` 说明槽位位置、比例、替换建议 |
| `decorate` | 数据页、逻辑页、纯排版页 | `image.needed=false`、`image.decorate_brief` 说明内部视觉语言（SVG/渐变/色块/水印/字体装饰）|

**禁止留模棱两可的 mode。选定后不得在 HTML 阶段临时改变。**

**额外密度约束**：
- `low / mid_low`：可使用更自由的图片策略
- `medium`：图片只能做支撑，避免吞掉正文
- `high`：不得用 `hero-background`，图片只可做支撑或局部说明
- `dashboard`：默认 `decorate`，不得把大图当主锚

---

## Phase 6：你是架构师，纪律与创意并重

> **核心理念**：上面的 Phase 2 菜单、Phase 3 密度合同和 Phase 4 schema 不是让你随意发挥的草稿，而是你作为架构设计者定下的**硬性工程图纸**。真正的创意，是在极致严酷的约束条件内绽放的。

**绝对的执行纪律（The Execution Discipline）：**
- `layout_hint` **是界面的黄金承重墙**。在下游的渲染阶段，它将被**以不妥协的精确度**映射到真实的 DOM 网格结构上，不可随意打破原有的版面重心设定。
- `card_type` 和 `chart_type` 意味着**特定设计规范的强制降临**。选定了特定类型，就必须遵循其最佳实践，否则后续的图审环节将直接把页面打回重做。
- `director_command` 是你的图纸批注 —— 这是对空间利用的更高维度说明，指导下游在不破坏骨架的前提下，该着重把哪些 CSS 精工细作落实。图审也不会为你善后，必须指令严密。
- `must_avoid` 是致命红线 —— 每页至少写 1 条真正有意义的禁区，提醒自己在边界内做到最好，主动拒绝平庸妥协。

**图审警示**：你在此阶段定下的所有结构决策，都必须对最终代码全权负责。不要以为有“像素级图审”兜底就可以随意偏离框架，图审是用来打磨微调的，绝不是来擦屁股和重构骨架的。

---

## Phase 7：cards 字段填充规范

每张卡片必须包含：
- `card_id`：稳定唯一，建议 `s{页码}-{anchor|support|context}-{序号}`
- `role`：`anchor` / `support` / `context`
- `card_type`：validator 枚举值，如 `text` / `data` / `list` / `process` / `data_highlight` / `timeline` / `diagram` / `quote` / `comparison` / `people` / `image_hero` / `matrix_chart`
- `card_style`：6 种合法视觉变体之一
- `headline`：标题（精炼，不超过 12 字）
- `body`：正文字符串数组，不能为空
- **【反泄漏铁律】**：`headline` 和 `body` 里面**只能且必须**填写最终展示给观众看的内容文案！绝不准许把纲要里的“旁白说明”、“工作动作”、“排版大意”（例如：*“这一页先把整场内容压缩成地图，再看拆解”* 这种明显属于幕后解说的话）当成台词本填进去！所有面向设计的幕后说明请扔进 `director_command`，若将工作指导语暴露在卡片正文上将被视为重大设计事故！
- `data_points`：如有数值则填对象数组
- `content_budget`：内容预算对象，且必须服从页级 `density_contract`
- `image`：完整图片合同对象，带 `mode`
- `resource_ref`：需要定向绑定某个 block/chart/principle 时写这里
- `image.slot_note` / `image.decorate_brief` / `image.prompt`：按图片模式按需补充

可选但推荐：
- `argument_role`
- `chart`

**不得出现空 `body` 的卡片。**

---

## Phase 8：设计意图传递字段

在坚守骨架的基础上拔高呈现品质。请严格定义并使用以下字段，向 HTML 阶段下达你的精确工程指令与微雕方案，它们构成了后续视觉落地的强制合同：

- `focus_zone`：提议的主张和视觉焦点区域
- `must_avoid`：明确提配 HTML 阶段不要陷入的平庸模板化设计
- `director_command`：给出富有创意性的结构、锚点和高级技法方向
- `decoration_hints`：描述装饰强度与视觉层次
- `source_guidance`：约束证据边界与引用期望
- `resources` / `resource_ref`：推荐消费的组件资源

---

## Phase 9：自审（强制）

运行 `planning_validator.py`，直到零 ERROR：

```bash
python3 SKILL_DIR/scripts/planning_validator.py $(dirname PLANNING_OUTPUT) --refs REFS_DIR --page PAGE_NUM
```

- ERROR 必须全部修复才能 FINALIZE
- WARNING 建议修复，不强制
- 自审通过后立即发送 FINALIZE，然后等待 HTML 阶段指令

---

## Design Principles Quick Reference

# 设计原则速查表 -- Step 4 字段级操作手册

> 用途不是讲理论，而是告诉页面策划师：当 JSON 某个字段写得不对，应该改哪一项。

> CARP（Contrast / Alignment / Repetition / Proximity）在这个 workflow 里是**版式 guardrail**，不是新风格系统，也不是新的模板库。
> 它不能覆盖 `scene_mode`、`density_contract`、`style.json.design_soul` 或 `variation_strategy`，只能约束这些合同如何被更清楚地执行。

---

## CARP 接入原则

### 冲突优先级

当 CARP 与既有预设看起来冲突时，按这个顺序判断：

1. `requirements / outline / planning` 真源优先
2. `scene_mode` 与 `density_contract` 优先
3. CARP 只管版式秩序，不管风格灵魂
4. `variation_strategy` 保证“同宗不同脸”，防止 repetition 退化成模板复制

### 四句短定义

- **Contrast**：决定谁先被看到，谁必须退后
- **Alignment**：决定元素归属于哪套共同骨架，而不是随意漂浮
- **Repetition**：决定同语义角色是否说同一种视觉语言，而不是页页重造系统
- **Proximity**：决定相关信息是否自然成组，而不是靠文字解释关系

### Scene Mode 力度表

| scene_mode | Contrast | Alignment | Repetition | Proximity |
|-----------|----------|-----------|------------|-----------|
| `launch` | 强，可做 hero-stage 压差 | 中，允许更自由重力 | 中，保语法不保长相 | 中，避免过度把页面收死 |
| `business` | 中强，服务判断先后 | 中高 | 中高 | 高，判断/依据/行动必须成组 |
| `report` | 中，服务指标与管理判读 | 高 | 高 | 高，比较轴和说明必须聚合 |
| `academic` | 中，服务论证主次，不做宣传冲击 | 很高 | 很高 | 很高，定义/证据/边界必须成组 |
| `technical` | 中，服务结构/机制/约束扫描 | 很高 | 高 | 很高，模块/步骤/限制条件必须成组 |
| `training` | 中，服务步骤和提醒先后 | 高 | 高 | 很高，步骤/警示/检查点必须贴近 |

### 字段映射速览

| CARP | 优先落在哪些字段 |
|------|------------------|
| Contrast | `visual_weight` / `design_intent.contrast_strategy` / `cards[].role` / `cards[].card_style` |
| Alignment | `layout_hint` / `focus_zone` / `director_command.spatial_strategy` / `layout_variation_note` |
| Repetition | `variation_guardrails.same_gene_as_deck` / `cards[].card_style` / `director_command.techniques` |
| Proximity | `page_text_strategy` / `cards[].content_focus` / `content_budget` / `compression_priority` |

---

## 原则 1. 视觉层级

核心问题：这一页谁是主角，谁必须退后？

优先影响字段：
- `visual_weight`
- `layout_hint`
- `cards[].role`
- `cards[].card_style`
- `director_command.anchor_treatment`

修正手法：
- 如果整页没有焦点：提高 anchor 卡片 `visual_weight`，改成 `accent` 或 `elevated`
- 如果所有卡片一样重：重写 `cards[].role`，只保留 1 个 `anchor`
- 如果标题和内容都在平均发力：在 `must_avoid` 明写“禁止等高等宽平均分配”
- 如果 `contrast_strategy` 只写成“突出重点”：改成具体对比轴，例如“靠标题尺度断层”“靠主图 vs 支撑卡面积差”“靠深浅对比而非装饰噪声”

危险信号：
- 3 张以上卡片都是 `filled`
- 没有 `anchor`
- `director_command.anchor_treatment` 只有“突出显示”这类空话
- dense scene 仍然把所有重点压成相近字号和相近字重

---

## 原则 2. 认知负荷

核心问题：观众这一页需要消化多少东西？

优先影响字段：
- `visual_weight`
- `density_label`
- `cards[].body`
- `cards[].chart`
- `rhythm_action`

修正手法：
- 如果一页塞太多：拆成 2 张 card 或下沉到下一页
- 如果必须保留高信息量：把 `rhythm_action` 标成“爆发”，下一页安排“缓冲”
- 如果信息少却做得很满：改成 `single-focus` 或 `free-section`
- 如果信息并不多但看起来很乱：先检查 `Proximity` 是否失败，而不是先删内容

危险信号：
- content 页 5 张以上 card 且都想当主角
- 一页同时放 3 种图表
- `visual_weight` 低，但 `cards` 内容非常密

---

## 原则 3. 构图与留白

核心问题：空间是在说话，还是只是装内容？

优先影响字段：
- `layout_hint`
- `layout_variation_note`
- `director_command.spatial_strategy`
- `decoration_hints.background`

修正手法：
- 如果布局描述落回“左边一块右边两块”：改写为重力关系，而不是像素切块
- 如果连续两页结构像克隆：在 `variation_guardrails.different_from_previous` 至少写 2 个反差维度
- 如果是金句或章节封面仍然很拥挤：把 `visual_weight` 下调，并用 `free-section`
- 如果元素像“差不多对齐”：把 `director_command.spatial_strategy` 改写成明确基线、列、带状区或中心轴，而不是模糊方位词
- `academic / technical / report` 场景下，默认要求更强 alignment；不要拿 launch 的自由重力去做 dense board

危险信号：
- “三栏均分”“上下两块”这类网页式描述
- 没有 `layout_variation_note`
- `background.feel` 为空或只有“简洁”
- 相关卡片距离和无关卡片距离差不多，看不出分组骨架

---

## 原则 4. 色彩与装饰克制

核心问题：这一页的装饰是在服务信息，还是在抢戏？

优先影响字段：
- `decoration_hints.*`
- `cards[].card_style`
- `variation_guardrails.same_gene_as_deck`

修正手法：
- 如果装饰很多却无主次：保留 1 个页面级手法 + 1 个卡片级手法
- 如果页与页完全不像同一套 deck：补 `same_gene_as_deck`
- 如果太稳太像模板：加强 `background.feel` 或 `page_accent.feel`，但写明 `restraint`
- `Repetition` 只要求“同类角色讲同一种语法”，不要求每页长一样；要重复的是标题角色、标签角色、注释角色、边框语法，不是构图结果

危险信号：
- 三层 `decoration_hints` 都写成“轻微点缀”
- 每页 weapon 组合完全一样
- `accent` 卡片超过 1 张

---

## 原则 5. 数据表达诚实

核心问题：数据是证据，不是贴纸。

优先影响字段：
- `cards[].data_points`
- `cards[].chart`
- `page_goal`
- `audience_takeaway`

修正手法：
- 没有具体数据时，不要假装做数据页，改成 `framework` 或 `quote`
- 有核心 KPI 时，至少安排 1 张 `data_highlight` 或带图表的 `data`
- 图表存在只是装饰时，删掉 `chart`

危险信号：
- 图表只是“为了看起来专业”
- `page_goal` 是判断句，但没有任何证据卡承接
- `data_points.source` 大量空白

---

## 原则 6. 节奏与变奏

核心问题：翻页时有呼吸和推进吗？

优先影响字段：
- `visual_weight`
- `rhythm_action`
- `director_command.techniques`
- `variation_guardrails.different_from_previous`

修正手法：
- 连续两页已经高压，第三页必须降压或视觉降密
- 同一布局复用时，必须换掉至少 2 个维度：重心 / card_style / 技法 / 留白
- 相邻页技术组合雷同，直接重写 `director_command.techniques`

危险信号：
- 3 页连续 `visual_weight >= 7`
- 3 页连续出现同一 `layout_hint`
- 相邻页 techniques 完全一致

---

## CARP 反模式速查

- **Contrast 失效**：所有字号、字重、卡片面积都差不多，观众不知道先看哪里
- **Alignment 失效**：元素像“差不多对齐”，但没有共同列线、边界线或中心轴
- **Repetition 失效**：同样是标题 / 标签 / 注释 / 指标块，却每页都换语法
- **Proximity 失效**：标题、说明、指标、注释互相散开，只能靠文字解释关系
- **误用 CARP**：把 `academic / technical / report` 做成 launch hero；或者把 `launch` 做成过于死板的表格页

---

## 字段纠偏表

| 发现的问题 | 先改哪个字段 | 再看哪个字段 |
|-----------|------------|------------|
| 页面对但不惊艳 | `director_command` | `decoration_hints` |
| 页面像网页 | `layout_hint` | `layout_variation_note` |
| 卡片都一样 | `cards[].card_style` | `cards[].role` |
| 节奏过平 | `visual_weight` | `rhythm_action` |
| 装饰乱 | `decoration_hints.*.restraint` | `variation_guardrails` |
| 论点强但证据弱 | `cards[].data_points` | `chart` |

---

## 逐页 8 项体检单

- 这页的 `page_goal` 是否是一句可判断的完整论点？
- `cards[]` 是否存在清晰的主次，而不是平均铺开？
- `layout_hint` 是否真的匹配内容结构，而不是习惯性套版？
- `director_command` 是否给出明确镜头感？
- 三层 `decoration_hints` 是否各司其职？
- 与上一页是否至少有 2 个维度不同？
- `must_avoid` 是否说中了这页最危险的模板化风险？
- 设计层拿到这页 JSON 后，是否能知道什么不能改、什么可以自由发挥？

---

## 任务包

| 项目 | 路径/值 |
|------|--------|
| 页码 | 6 / 10 |
| 需求 | `ppt-output/runs/20260716-141627-zizhujiashi/requirements-interview.txt` |
| 大纲 | `ppt-output/runs/20260716-141627-zizhujiashi/outline.txt` |
| 素材 | `ppt-output/runs/20260716-141627-zizhujiashi/source-brief.txt` |
| 风格 | `ppt-output/runs/20260716-141627-zizhujiashi/style.json` |
| 图片素材目录 | `ppt-output/runs/20260716-141627-zizhujiashi/images` |
| 图片清单快照 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-images-6.md` |
| 菜单快照 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-menu-ALL.md` |
| 运行日志 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-6.log` |
| SKILL 目录 | `$SKILL_DIR` |
| 资源目录 | `$SKILL_DIR/references` |

---

## 产物路径

- 策划稿 JSON：`ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json`
- Runtime 备份：`ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-output-6.json`
- Validator 报告：`ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-validator-6.json`
- 文件内容必须是**纯 JSON 对象**（可直接写对象，也可包在 ```json fenced block 中），不要夹杂说明性 prose。

---

## 执行链路（固定顺序，不得跳步）

1. 读取 `ppt-output/runs/20260716-141627-zizhujiashi/outline.txt` 中第 6 页的定义（只关注你这一页），特别提取 `密度下限 / 密度目标 / 密度上限 / 节奏动作 / 信息姿态 / 锚点类型`
2. 深度读取 `ppt-output/runs/20260716-141627-zizhujiashi/requirements-interview.txt`，将其中的【受众画像】、【目标动作】和【版面心智】作为单页选型和内容设计的最高约束（例如：对底层技术受众放大图表卡片，对合作方主打对比及成果锚点）。
3. 读取 `ppt-output/runs/20260716-141627-zizhujiashi/source-brief.txt` 获取可用素材
4. 读取 `ppt-output/runs/20260716-141627-zizhujiashi/style.json` 提取 `mood_keywords`、`variation_strategy`、`decoration_dna` 做情绪定调
5. 读取主链已生成的**图片清单快照** `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-images-6.md`。
6. 如需刷新这份图片清单，再执行：
   ```bash
   python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-6.log --label planning-refresh-images -- \
     python3 $SKILL_DIR/scripts/resource_loader.py images --images-dir ppt-output/runs/20260716-141627-zizhujiashi/images --output ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-images-6.md
   ```
7. 读取主链已生成的**组件/图表菜单快照** `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-menu-ALL.md`（这是给 runtime 留档的备份，也作为你本阶段优先使用的菜单视图）。
8. 如需刷新这份菜单快照，再执行：
   ```bash
   python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-6.log --label planning-refresh-menu -- \
     python3 $SKILL_DIR/scripts/resource_loader.py menu --refs-dir $SKILL_DIR/references --output ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-menu-ALL.md
   ```
9. **先冻结密度合同，再回答设计提问**。你必须先确定 `density_label`、`density_reason` 和 `density_contract`，再决定 `page_type`、`layout_hint`、`cards[].card_type`、`chart.chart_type`、`resource_ref`、`image.mode`、排版策略等。

### 设计决策驱动提问

在确定布局和资源之前，先回答这 4 个问题（可在心中推演，不需要写入产物）：

1. **观众在这一页应该先看到什么？** → 决定视觉锚点和主次关系
2. **这一页的信息是怎么"流动"的？** → 决定空间布局和视觉动线
3. **这一页和上一页的视觉感受应该有什么不同？** → 决定节奏变化
4. **在菜单中的工具里，哪些能最好地服务上面 3 个答案？** → 决定 layout_hint、card_type、chart、resource_ref

> **重要**：菜单里的工具依然是你的调色盘。同样的数据可以用完全不同的工具和布局来表达，关键是你想让观众产生什么感受。设计原则参考文件与映射表是你绝好的灵感索引，你完全可以跨界混搭布局。
> **唯一不可妥协的底线**：你可以自由构思并调配这些高级元素，但你的产物必须是精密计算后的产物！任何 `layout_hint` 或组件调用的选择，在下游环节都必须用符合其核心语义的底层结构去精确承接。你的奇思妙想不能以牺牲布局崩塌为代价。
> **密度红线**：`density_label` 只能落在 outline 给你的窗口里。`dashboard` 只允许 `content` 页，且必须同时把 `image_policy` 锁成 `decorate_only`。

**填写 `resources` 字段时必须说明选择理由**（推荐写入 `resources.resource_rationale`），例如回答"为什么用这个布局/组件能最好地让观众产生我想要的感受"。
10. 将完整 planning 写入 `ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json`，并同步备份到 `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-output-6.json`：
   ```bash
   python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-6.log --label planning-runtime-copy -- \
     cp ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-output-6.json
   ```
11. 自审（必须执行，不得跳过）：
   ```bash
   python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-6.log --label planning-validator -- \
     python3 $SKILL_DIR/scripts/planning_validator.py $(dirname ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json) --refs $SKILL_DIR/references --page 6 --report ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-planning-validator-6.json
   ```
12. 修复所有 ERROR（WARNING 建议修复）。
13. 完成信号：输出 `--- STAGE 1 COMPLETE: ppt-output/runs/20260716-141627-zizhujiashi/planning/planning6.json ---`，然后按外层 orchestrator 协议继续下一阶段
14. 不要把当前阶段的完成信号误当作整页任务结束。

---

## 阶段边界

- 本阶段：只写 planning JSON，不写 HTML
- 下一阶段：orchestrator 会指引你进入 HTML 生成
- 消费规则：planning 阶段只读资源的 `> 引用层`（菜单），HTML 阶段才读正文层
