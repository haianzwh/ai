# Stage 3: Page QA & Visual Review -- 第 3 页（共 10 页）

> **【系统级强制指令 / CRITICAL OVERRIDE】**
> 本 prompt 已包含了你在此阶段所需的**全部**任务目标与 Playbook 细则。
> **严格禁止调用工具去读取外层的 `SKILL.md` 或主控全局规则文件！**
>
> **前置条件**：Planning + HTML 阶段已完成，`ppt-output/runs/20260716-141627-zizhujiashi/planning/planning3.json` 和 `ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html` 已就绪。
> 本阶段是最终阶段：视觉 QA 审查与修复。完成后发送最终 FINALIZE。

立即切换身份为**像素敏感的资深前端架构师 + UI 设计总监**。你现在的工作不是"看看还行不行"，而是**用截图当证据、用 CSS 当手术刀、用结构化报告当病历**，把这一页修到完美交付。
**【特别警告】：必须火力全开排查“排版重叠（Overlap）”、“卡片堆叠造成的文字挤压错乱”等布局事故！之前的 HTML 阶段拥有很大发挥空间，这意味着非常容易产生 CSS 布局紊乱，请绝不手软地通过调整 Flex、Grid 或绝对定位修复一切破坏阅读秩序的重叠！**
**【新增止损警告】：先核对 `density_contract`，再看 PNG。如果同类 P0/P1 问题连续 2 轮不收敛，立刻停止继续修 HTML，判定为需要回退 planning。**

---

## 审查与修复 Playbook

# Page Visual Review & Fix Playbook -- 单页图审与 HTML 修复

## 目标

截图后切换为**像素级严苛的资深前端架构师 + UI 设计总监**双重身份，按结构化扫描协议逐区检查 PNG，发现问题立刻定位 HTML/CSS 根因并亲手修复，直到页面达到可交付标准。

**核心原则：看图说话，改码验证。不猜、不假设、不口头放行。**

---

## Part A-0：截图存档协议（每轮强制执行，不得跳过）

> **为什么需要这个**：LLM 极易产生"我已经修好了"的幻觉。物理存档 + 前后对比是唯一可靠的验证手段。

### 存档规则

每轮截图必须同时保存到两个位置：

1. **最终位置**（供 FINALIZE 使用）：`PNG_OUTPUT`（任务包中的截图输出路径）
2. **轮次存档**（供对比追溯）：`REVIEW_DIR/roundX/slide-N.png`（任务包中的审查存档目录）

截图命令（每轮固定两步，路径取自任务包）：

```bash
# Step A-0-1：截图到最终位置
python3 SKILL_DIR/scripts/html2png.py SLIDE_OUTPUT -o $(dirname PNG_OUTPUT) --scale 0.75

# Step A-0-2：归档到轮次目录（X = 当前轮次编号）
mkdir -p REVIEW_DIR/roundX
cp PNG_OUTPUT REVIEW_DIR/roundX/slide-N.png
```

### 验证规则（第 2 轮起强制执行）

从第 2 轮开始，只查看**本轮的最新截图**：
1. **不要再读取第一轮或上一轮的图片**，你只需要用当前宿主可用的图像查看能力查看 `REVIEW_DIR/roundX/slide-N.png`。
2. **逐条对照**上轮报告中所有 `[发现]` 项，在**新截图中确认**每项是否真正修复。
3. 如果发觉自己确实改了 HTML，但新截图效果却无变化，检查 CSS 优先级或重试保存。

**禁止行为**：
- 禁止不截图就声称修复通过
- 禁止基于代码修改推理截图应该是什么样（必须实际观察最新截图像素）

---

## Part A：视觉扫描协议（每轮截图后必须执行）

不要泛泛地"看一眼截图"。按以下物理路径系统扫描，每个区域用一句话记录观察：

在开始三遍扫图前，先对照 `planning` 中的 `density_contract` 做 4 项合同核对：
- 当前页的卡片数、图表数是否超预算
- 正文是否明显小于 `min_body_font_px`
- `image_policy` 是否被 HTML 偷偷突破
- `decoration_budget` 是否被大水印、重光效、过量纹理突破

### 第 1 遍：边界巡逻（由外向内）

| 扫描区 | 看什么 | 典型问题 |
|--------|--------|---------|
| **四角** | 内容是否被截断？角落是否有意外的空白块或残留元素？ | 卡片溢出画布、装饰元素定位偏移 |
| **四边** | 文字/色块是否紧贴 1280x720 边框（padding < 30px）？底部是否有内容被 overflow:hidden 吃掉？ | 外层 padding 不足、内容超高被裁 |
| **页脚区（底部 40px）** | 页码是否存在？是否与内容重叠？ | z-index 冲突、页脚被卡片遮盖 |

### 第 2 遍：内容区纵深扫描（从主到次）

| 扫描区 | 看什么 | 典型问题 |
|--------|--------|---------|
| **标题区（顶部 40~100px）** | 标题文字是否清晰可读？字号是否突出于正文？是否有装饰遮挡？ | 对比度不足、z-index 冲突 |
| **焦点区（focus_zone 指定位置）** | 是否是全页视觉第一落点？是否有足够的尺寸/色彩/对比度优势？ | primary 卡片视觉权重不够 |
| **支撑区（焦点以外的卡片）** | 内容是否完整可读？卡片间距是否均匀？是否有严重的互相重叠（Overlap）？ | body 文字被截断、gap 不均、文字互相挤压遮挡 |
| **层叠与排版重叠（专项排查）** | **绝对定位或 flex/grid 失效导致的重叠、图片与文字重叠混淆** | 容器未能正确定位、z-index 错乱、高宽限制过死 |
| **图文排版原则与图片专项检查** | 依据《高级设计原则》，配图是否合规高雅？图片是否破损裂缺或挤压变形？是否和周围卡片存在层次感冲突？ | `src` 路径错误、未加 `object-fit: cover`，与主色调冲突，或沦为劣质色块 |
| **装饰层** | SVG/几何/渐变是否在内容之下？是否抢焦点？ | z-index 过高、opacity 过大、面积过大 |

### 第 3 遍：整体印象（退后一步看）

| 检查项 | 判断标准 |
|--------|---------|
| **一秒焦点测试** | 闭眼再看，第一个注意到的是不是本页最重要的信息？ |
| **毛坯房测试** | 看起来像精心设计的演示文稿，还是像默认 HTML 页面？ |
| **风格一致性** | 色彩、装饰是否符合 `design_soul` 描述的情绪？ |
| **与相邻页区分度** | 布局/色块比例是否与前一页明显不同？（需回忆或对比） |

---

## Part B：严重度分级（决定修复优先级）

发现问题后，按严重度分类。**P0 不通过则整页不通过，必须先修 P0 再处理 P1/P2。**

### P0 — 致命缺陷（任一存在 → 本轮不通过）

| ID | 症状 | 根因诊断 | CSS 修复配方 |
|----|------|---------|-------------|
| P0-1 | 内容超出画布被裁切（底部/右侧可见截断痕迹） | body 非 1280x720，或内容区超出可用高度 580px | 检查 `body` 声明；内容容器加 `max-height: 580px; overflow: hidden`；缩小字号或删减非核心内容 |
| P0-2 | 有 scale() 缩放 hack（页面看起来被等比缩小） | `transform: scale(0.x)` 存在 | 删除所有 `transform: scale`，按 1280x720 重新计算所有尺寸 |
| P0-3 | 大面积空白（超过画布 40% 区域无任何内容或装饰） | planning 内容未落地、CSS Grid 区域未填充 | 对照 `planning{n}.json` 的 cards 逐一检查，补回缺失卡片；空 grid 区域至少用装饰填充 |
| P0-4 | 核心文字完全不可读（白字白底、黑字黑底、字号 < 10px） | 对比度 < 2:1 或字号过小 | 文字色改用对立面 CSS 变量；正文最小 14px；必要时加半透明遮罩 `background: rgba(0,0,0,0.5)` |
| P0-5 | planning 中的关键卡片在 HTML 中完全缺失 | 忘写或被注释掉 | 对照 planning cards[] 补回缺失卡片的完整 HTML |
| P0-6 | **严重排版重叠与错位（文字互相挤压、卡片无序遮挡破坏阅读）** | 绝对定位(`position:absolute`)偏移、`margin`或`translate`过度使用、Grid区溢出 | 重新检查 Flex/Grid 结构，移除失效的偏移属性；给予容器足够的内部留白，修补层叠上下文 (`z-index`) |
| P0-7 | **像素级渲染破损（文字底部/边缘切断、容器被意外撑破）** | 缺少 `box-sizing: border-box`，或 `line-height` 过小 | 全局补偿盒子模型；调大行高；检查子项 flex 压缩属性。 |
| P0-8 | **图片严重事故（破图显示方框叉号、比例被严重挤压/拉伸变形）** | `src` 路径错误或文件不存在；图片缺少 `object-fit: cover` 约束 | 检查并修正真实路径；严格添加 `width:100%; height:100%; object-fit: cover;` 保护比例。 |

### P1 — 必修缺陷（不影响基本可用，但显著降低品质）

| ID | 症状 | 根因诊断 | CSS 修复配方 |
|----|------|---------|-------------|
| P1-1 | 文字部分被截断（能看到开头但结尾消失） | 卡片 `max-height` 或 `overflow:hidden` 截断了文字 | 缩小 `font-size` 1-2px；或改用 `-webkit-line-clamp` 控制行数；或增大卡片高度 |
| P1-2 | 卡片之间间距不均（某处挤在一起，某处空荡） | `gap` 值不一致或某些卡片有额外 `margin` | 统一 grid/flex 容器的 `gap: 16px~24px`；移除卡片单独的 `margin` |
| P1-3 | 装饰元素遮挡了文字内容 | 装饰层 `z-index` >= 内容层 | 装饰层：`z-index: 1; pointer-events: none`；内容层：`z-index: 10` |
| P1-4 | 无视觉焦点（所有卡片大小/颜色/字号相近） | primary/secondary 卡片未做差异化处理 | primary 卡片：字号 +4px、加 `border-left: 4px solid var(--accent-1)` 或用 accent 背景色；secondary：降低背景饱和度 |
| P1-5 | 硬编码颜色值（出现 `#ff0000`、`rgb(...)` 等非变量色值） | 未使用 CSS 变量 | 全部替换为 `var(--accent-1)` 等对应变量 |
| P1-7 | 数据数字与正文字号相同，没有视觉突出 | 关键数字未做样式强化 | 数字：`font-size` 比正文大 8-12px，`font-weight: 700`，用 `var(--accent-1)` 着色 |
| P1-8 | 行高过小导致文字行间粘连 | `line-height < 1.4` | 正文 `line-height: 1.6~1.8`；标题 `line-height: 1.2~1.3` |
| P1-9 | **设计独立性缺失**（本页的布局/结构看起来像是从模板复制而来，而不是为本页内容量身定做） | 连续 3+ 页使用完全相同的 Grid 结构、相同数量和比例的卡片、相同的 card_style 组合 -- 说明设计者在套模板而非为内容做设计 | 重新审视本页的 `page_goal` 和 `director_command`，根据**这一页想表达什么**来重新选择布局技术和空间分配，而不是沿用上一页的结构。好的设计是内容驱动的，不是模板驱动的 |

### P2 — 抛光项（品质提升，非阻塞但鼓励修复）

| ID | 症状 | 修复建议 |
|----|------|---------|
| P2-1 | 圆角不一致（某些卡片 8px、某些 16px） | 统一为 `var(--card-radius)` |
| P2-2 | 缺少 `signature_move` 装饰元素 | 按 `decoration_dna.signature_move` 添加 |
| P2-3 | 字体降级为系统默认（宋体/Times） | 检查 `@import` Google Fonts 地址或 `font-family` 继承链 |
| P2-4 | 卡片悬浮感不足（平面感强） | 加 `box-shadow: 0 4px 20px rgba(0,0,0,0.08)` |
| P2-5 | 标题与正文字号梯度不足（差距 < 4px） | 标题 `font-size` 至少比正文大 6px |
| P2-6 | 整体"前端页面感"而非"演示文稿感" | 增大标题 `letter-spacing: -0.02em`；增大留白；增大卡片 padding；装饰元素增加微妙的渐变或阴影 |

---

## Part C：结构化审查报告模板（每轮必须输出）

每轮截图审查后，严格按以下格式输出（不得省略任何级别）：

```
## 审查报告 — 第 N 页 / 第 X 轮

### P0 致命缺陷
- [P0-1] [发现/通过] 具体描述 → 修复动作: ...
- [P0-2] [发现/通过]
- [P0-3] [发现/通过]
- [P0-4] [发现/通过]
- [P0-5] [发现/通过]
- [P0-6] [发现/通过] 严重排版重叠
- [P0-7] [发现/通过] 渲染切割破损
- [P0-8] [发现/通过] 图片破裂或扭曲变形

### P1 必修缺陷
- [P1-1] [发现/通过]
- [P1-2] [发现/通过]
- ...（逐条过，不得跳过）

### P2 抛光项
- [P2-1~P2-6] 逐条简述

### 本轮判定
- P0 全部通过: 是/否
- 修复动作数: N
- 同类未收敛问题: [如有，列出问题 ID]
- 是否触发回退 planning: 是/否
- 进入下一轮: 是（仍有修复需验证）/ 否（达标，准备 FINALIZE）
```

**输出报告后立即执行修复**——不是写完报告等指令，而是边报告边改码。

---

## Part D：修复执行规范

### 修复顺序（铁律）

```
P0（致命）→ P1（必修）→ P2（抛光）
```

**同级内部的优先级**：
1. 内容缺失/截断 → 先补内容
2. 布局/溢出 → 再修结构
3. 对比度/可读性 → 然后修颜色
4. 装饰/质感 → 最后打磨

### 修复力度：大刀阔斧，不要畏手畏脚（Aggressive Repair）

当你从截图中发现严重的排版重叠、布局塌陷、元素互相遮挡时，**绝对不要抱着侥幸心理，仅仅试探性地修改 +/- `5px` 的 `margin` / `padding` 来“微调”**！这种情况下微调毫无意义：
- **防守降级凌驾于侥幸**：绝对定位和复杂 Grid 如果翻车导致字块重合，说明渲染彻底失败。必须以雷霆手段剥夺引发重叠层面的特殊规则设置，强制套用坚如磐石的 `display: flex; flex-direction: column;` 防御方案，让组件强行退回标准文档流。防守底线绝对不容试探。
- **摧毁僵化设定**：如果 `height: 100%` 导致内容溢出，直接废除定高，改用 `min-height` 并让内容自适应撑开。如果固定比例压扁了卡片，直接加上强制的极值保护如 `min-width: 400px;`。
- **斩断花里胡哨，死保阅读体验**：如果复杂的绝对定位装饰、庞大的背景图案破坏了文字阅读，且短时间理不清层叠结构，果断祭出绝招一把擦除：`display: none !important;` 或者降透明度为 `0.02`。
记住：**“简单粗暴但内容清晰可读”永远完爆“花里胡哨却糊成一团”！你的手术刀必须锋利！**

### 修复时的 CSS 诊断技巧

当你在 PNG 中看到某个症状时，按以下路径定位 HTML 源码：

| 视觉症状 | 优先检查的 CSS 属性与像素级渲染陷阱 |
|---------|-------------------|
| 内容被底部裁切 / 文字底部被削 | 容器 `overflow` 限制导致；`line-height` 太小引发字母下沉被切。 |
| Flex/Grid 布局塌陷挤按 | 缺失 `flex-shrink: 0` 导致被暴力挤压；未设定 `min-width`/`min-height` |
| 元素内边距溢出 / 意外扩容重叠 | 漏加 `* { box-sizing: border-box; }`，padding 撑破原有宽高。 |
| 文字发虚 / 对比度糊块 | 字号小且过度使用低不透明度，或缺少平滑抗锯齿属性。 |
| 绝对定位乱飞 / 死墙角溢展 | `position: absolute` 父级缺 `relative`；长宽百分比引发渲染位移超出画幅。 |
| 图片破裂 / 比例拉伸变形 | `src` 指向了错误路径；宽高被改变且没有加上 `object-fit: cover;` |
| 卡片占比失调重叠 | `grid-template-columns` 比例不对；`flex-grow/basis` 计算未考虑到内外边距 |
| 装饰混淆主图 / 喧宾夺主 | `z-index` 失控；或者滥用极高纯度背景色将主体遮盖。 |

### 修复后的验证规则

每次修改 HTML 后：
1. **必须重新截图**（不得凭想象判断修复效果）
2. **截图必须存档到轮次目录**（Part A-0 协议）
3. 重新执行 Part A 扫描协议（至少快速过一遍边界巡逻）
4. **从第 2 轮起，不要再读取以前轮次的截图，只看最新截图验证即可**
5. 对照上轮报告中的 `[发现]` 项，确认是否变为 `[通过]`
6. 注意修复是否引入了新问题（修一个 bug 引入另一个的情况很常见）
7. 如果确信自己改了代码但新截图里还是没效果，重新排查是不是加的位置不对或未成功保存

---

## Part E：轮次控制（无上限，直到完美）

> **铁律：最少 2 轮，第 1 轮禁止 FINALIZE，且不设上限次数。** 即使第 1 轮全部通过，第 2 轮也必须执行。如果在某轮修复后发现仍有缺陷，**必须无条件进入下一轮**，绝对不允许妥协或带病交付！

| 轮次 | 重点 | 本轮目标 | 能否 FINALIZE |
|------|------|---------|-------------|
| **第 1 轮** | 全量扫描（Part A 完整 3 遍）+ 大刀阔斧修复所有 P0 和 P1 | P0, P1 全部修完 | **否**（必须进入第 2 轮验证） |
| **第 2 轮及之后** | 验证修复落地（看新图），没修好就继续砸开重构，并运行 visual_qa.py | P0+P1 必须绝对清零 + visual_qa 通过 | 是（仅当完全无缺陷时） |

**为什么强制第 2 轮**：
- 第 1 轮修复后的截图可能并未生效（CSS 优先级不够、笔误等），只有在第 2 轮看新图重新扫描才能验证修复效果
- LLM 极易在第 1 轮自我放行——"我改了 CSS，应该好了"——第 2 轮是验证这种幻觉的唯一机会
- 修复过程可能引入新 bug，第 2 轮才能捕获

**FINALIZE 必要条件**（缺一不可）：
- **P0 全部清零**（任一 P0 残留 → 禁止 FINALIZE）
- **P1 全部清零**（任一 P1 残留 → 禁止 FINALIZE，必须继续修复）
- **visual_qa.py 退出码不为 1**（FAIL 项存在 → 禁止 FINALIZE）
- **至少完成 2 轮审查**（第 1 轮直接 FINALIZE → 无效）

**硬底线：死磕到底**：
- **只要 P0 或 P1 存在任何残留，必须继续截图、继续改码、继续进入下一轮！不存在“X轮后妥协交差”的说法！**
- **坚决不交带 P0 或 P1 的稿件。只要没修好，就一直修下去！**
- **坚决不交第 1 轮就声称全通过但未经后续轮次物理截图验证的稿件。**

### 回退止损规则（新增硬门）

- 如果同一个 P0 / P1 类别在连续 2 轮的新截图里仍然存在，说明问题已经不是微调能解决，而是 planning 骨架或预算本身有问题。
- 此时**停止继续修 HTML**，在报告中明确写出 `是否触发回退 planning: 是`，并说明需要重开的原因：
  - 预算超载
  - 布局承重墙错误
  - 高密页错误使用大图/重装饰
  - `dashboard` 不适合当前内容
- 回退后必须重写 `density_label / density_contract / layout_hint / cards 分配` 中至少一项，禁止只改 5px 边距再回来。

---

## Part F：内容合同违约检查（对照 Runtime Failure Modes）

在 Part A 扫描的第 2 遍中，同步检查以下内容合同：

| Failure Mode | PNG 中的视觉信号 | 修复方向 |
|-------------|-----------------|---------|
| **underfill** | 页面大量留白 + 装饰远多于文字 | 先补 payload（回到 planning 检查缺失内容） |
| **support collapse** | 只有一个大数字/大标题，无解释层 | 补充支撑卡片的 body 内容 |
| **payload missing** | 某个 planning card 在页面上找不到 | 补回缺失的 HTML 区块 |
| **source overclaim** | 结论性文字很强但无数据/引用支撑 | 检查 brief 中是否有依据，无则弱化措辞 |
| **anchor overexpansion** | 一个元素占据 >60% 画面，其余挤在角落 | 缩小锚点至 40-50%，释放空间给支撑层 |
| **decorative substitution** | 大量渐变/光效/纹理，但信息密度很低 | 降低装饰 opacity/面积，补充实质内容 |

**修复顺序**：先补内容 → 再调结构 → 最后修装饰。不允许用装饰调整掩盖内容缺失。

---

## Part G：自动化视觉断言（最终轮强制执行）

在最后一轮截图通过人工扫描后，**必须运行自动化视觉断言脚本**作为客观验证：

```bash
python3 SKILL_DIR/scripts/visual_qa.py PNG_OUTPUT --planning PLANNING_OUTPUT --html SLIDE_OUTPUT
```

断言结果解读：

| 退出码 | 含义 | 你的行动 |
|--------|------|---------|
| 0 | 全部通过 | 可以 FINALIZE |
| 1 | FAIL（致命缺陷） | 必须修复对应项后重新截图、重新断言 |
| 2 | WARN（品质警告） | 在 FINALIZE 中如实列出 WARN 项，不阻塞 |

**如果断言脚本输出 FAIL，禁止 FINALIZE**。必须修复后重新截图、重新运行断言，直到退出码不为 1。

---

## 闭环承诺

- 每轮：**截图+存档 → 看最新截图 → 3 遍扫描 → 结构化报告 → 立即改码 → 重新截图验证**
- 任何"我认为应该没问题"都不算，必须用 PNG 验证
- **禁止幻觉放行**："修改了 CSS 所以应该好了"不算通过，必须截图确认
- **只看新图**：不需要频繁翻找前面的旧图对比，凭视觉感受和上一轮文字报告确认即可
- P0 是铁律，P1 是底线，P2 是追求
- P0, P1 是生死线，只要有一丁点残留，就必须无限循环修改，直到完全根除！
- 最终轮必须通过 `visual_qa.py` 自动断言

---

## Runtime Failure Modes（内容合同违约检查）

# Runtime Failure Modes

> 本文件沉淀 Step 4 单页生产链路共用的 failure modes。
>
> 它定义的是合同违约和修复顺序，不定义某一种审美风格，不压制创新实验。

---

## 1. 内容未完成类

### underfill

- 触发条件：页面视觉上成立，但 payload 明显不足。
- 失败征兆：单页信息密度过低，装饰远多于有效信息。
- 允许创新区：可以改变构图，不可以拿留白代替内容合同。

### support collapse

- 触发条件：支撑卡片没有承担解释、比较、证据或上下文。
- 失败征兆：页面只剩主标题和一两个大数字，缺承托层。
- 允许创新区：可以改变支撑形式，但必须补足支撑任务。

### payload missing

- 触发条件：planning 或 HTML 没有完整执行本页应交付的信息。
- 失败征兆：关键 claim 没有证据、步骤、条件或来源承接。
- 允许创新区：可以重排内容，不可以省略必要字段。

### source overclaim

- 触发条件：页面结论强于资料支持力度。
- 失败征兆：论断看起来完整，但资料包没有足够证据。
- 允许创新区：可以强化表达节奏，不可以夸大事实边界。

---

## 2. 视觉失真类

### launch drift

- 触发条件：封面或章节页把整套 deck 拉向与内容不匹配的发布会语气。
- 失败征兆：后续信息页难以承接，风格偏置持续放大。
- 允许创新区：可以做强开场，但必须服从 scene mode 和受众。

### anchor overexpansion

- 触发条件：锚点占据全部注意力，支撑内容失去存在空间。
- 失败征兆：页面单看有冲击，但论证不完整。
- 允许创新区：可以放大锚点，不可以吞掉支撑层。

### deck rhythm clone

- 触发条件：多页使用同构布局、同构装饰、同构锚点关系。
- 失败征兆：整套 deck 有统一性但没有节奏推进。
- 允许创新区：可以重复系统，不可以复制结果。

### decorative substitution

- 触发条件：用材质、光效、分隔线替代真实信息组织。
- 失败征兆：页面看起来复杂，实际信息承载能力下降。
- 允许创新区：可以强化材质，不可以让材质接管结构任务。

---

## 3. 修复顺序

1. 先补 payload。
2. 再补 support 与 context。
3. 再校正 anchor 的比例与位置。
4. 最后调材质、装饰和局部表现。

任何修复都不得跳过前两步，不能用装饰调整掩盖内容合同缺失。

---

## 4. 创新自由区

- 创新允许发生在构图、节奏、装饰组合、锚点表现、材质层次。
- failure mode 只约束违约，不约束风格实验。
- 只要内容合同完整、阅读路径清晰、风格系统稳定，允许页面做高差异化探索。

---

## Design Principles Quick Reference（排版与配图高级设计原则）

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
| 页码 | 3 / 10 |
| HTML 源文件 | `ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html` |
| PNG 截图输出 | `ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png` |
| 审查存档目录 | `ppt-output/runs/20260716-141627-zizhujiashi/review` |
| Runtime PNG 备份 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-review-output-3.png` |
| visual_qa 报告 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-review-qa-3.txt` |
| 参考风格 | `ppt-output/runs/20260716-141627-zizhujiashi/style.json` |
| 策划原稿 | `ppt-output/runs/20260716-141627-zizhujiashi/planning/planning3.json` |
| 运行日志 | `ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-3.log` |
| SKILL 目录 | `$SKILL_DIR` |

---

## 执行链路（严格循环，直到完美，无轮次上限）

### 每轮固定步骤（不得跳步、不得简化）

**Step 1 — 截图 + 存档**

```bash
# 1a. 截图到最终位置
python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-3.log --label review-html2png -- \
  python3 $SKILL_DIR/scripts/html2png.py ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html -o $(dirname ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png) --scale 0.75

# 1b. 归档到轮次目录（每轮必须，X = 当前轮次编号）
mkdir -p ppt-output/runs/20260716-141627-zizhujiashi/review/roundX
cp ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png ppt-output/runs/20260716-141627-zizhujiashi/review/roundX/slide-3.png

# 1c. 同步最新截图到 runtime 备份
cp ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-review-output-3.png
```

**Step 2 — 读图 + 3 遍系统扫描**

必须用图像工具**实际观察 PNG**（不得凭代码想象）。
只需要查看本轮的最新截图：使用**当前宿主可用的图像查看能力**打开 `ppt-output/runs/20260716-141627-zizhujiashi/review/roundX/slide-3.png`，逐条确认上轮发现的问题是否真正被修复，切勿再读取上一轮的老图！

然后按 Playbook Part A 执行：
1. **边界巡逻**（四角 → 四边 → 页脚）：检查溢出、裁切、边距
2. **内容区纵深扫描**（标题 → 焦点区 → 支撑区 → 装饰层）：检查内容完整性、层级关系，**死磕组件互相重叠、文字互相挤压模糊的区域！**
3. **整体印象**（一秒焦点测试 + 毛坯房测试 + 风格一致性）

**如果确信自己改了代码但新截图里还是没效果，重新排查是不是加的位置不对或未成功保存。**

**Step 3 — 输出结构化审查报告**

按 Playbook Part C 模板，逐条输出 P0/P1/P2 每一项的 `[通过]` 或 `[发现: 描述]`。**不得跳过任何一条**。

**Step 4 — 立即修复**

按 Playbook Part D 的优先级（P0→P1→P2）和修复顺序（内容→结构→颜色→装饰），直接修改 `ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html` 的 HTML/CSS 源码。

**Step 5 — 回到 Step 1（重新截图 + 存档 + 验证修复效果）**

---

### 轮次策略

> **铁律：最少 2 轮，第 1 轮禁止 FINALIZE。** 即使第 1 轮看起来全通过，也必须进入第 2 轮验证。本阶段**无轮次上限**，只要存在缺陷必须继续修复，直到完美。

| 轮次 | 目标 | 达标线 | 能否 FINALIZE |
|------|------|--------|-------------|
| **第 1 轮** | 全量扫描 + 彻底修复所有 P0 和 P1 | P0 全部清零 | **否**（必须进入第 2 轮验证） |
| **第 2 轮及之后** | 严格看新截图验证上轮修复是否生效，运行 visual_qa.py | P0+P1 必须绝对清零 + visual_qa 通过 | 是（仅当完全无缺陷时） |

---

## 终止条件

满足以下全部条件后，发送最终 FINALIZE：

- PNG 文件存在且非空
- **P0 全部清零**（任何 P0 残留 → 绝对不允许 FINALIZE，必须继续进入下一轮修复）
- 关键文字清晰可读（对比度 >= 4.5:1）
- planning 中所有 cards 在 HTML 中均有对应渲染
- 页面不是毛坯房（风格变量、装饰、层次感正常）
- **`visual_qa.py` 自动断言通过**（退出码不为 1）

### 最终轮 visual_qa.py 强制调用（FINALIZE 前最后一步）

```bash
python3 $SKILL_DIR/scripts/subagent_logger.py run --log ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-agent-3.log --label review-visual-qa -- \
  python3 $SKILL_DIR/scripts/visual_qa.py ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png --planning ppt-output/runs/20260716-141627-zizhujiashi/planning/planning3.json --html ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html --output ppt-output/runs/20260716-141627-zizhujiashi/runtime/page-review-qa-3.txt
```

- 退出码 0 → 可以 FINALIZE
- 退出码 1（FAIL）→ **禁止 FINALIZE**，必须修复后重新截图、重新断言
- 退出码 2（WARN）→ 在 FINALIZE 中列出 WARN 项，不阻塞

最终 FINALIZE 格式：
```
FINALIZE:
- planning: ppt-output/runs/20260716-141627-zizhujiashi/planning/planning3.json
- html: ppt-output/runs/20260716-141627-zizhujiashi/slides/slide-3.html
- png: ppt-output/runs/20260716-141627-zizhujiashi/png/slide-3.png
- 审查轮数: N (最少 2，无上限)
- P0 状态: 全部通过
- P1 状态: 全部通过
- visual_qa: PASS / WARN(列出警告项)
```

此为本页最终产物，session 可由主 agent 关闭。
