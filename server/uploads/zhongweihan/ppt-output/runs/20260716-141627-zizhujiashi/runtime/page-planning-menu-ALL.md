### layouts/

#### asymmetric
**非对称两栏版式 (2/3 + 1/3)**
> 2-3张卡片。
> 空间划分建议：2fr 1fr 列。主次鲜明 -- anchor 占 2/3 大区，support 在 1/3 侧翼。
> 适用数据：有1个核心论点+1个辅助佐证的页面。
> 主区域用 elevated/accent card_style，辅助区用 outline/transparent -- 禁止两侧都用 filled。

#### hero-top
**顶部英雄式版式**
> 2-4张卡片。
> 空间划分建议：1fr 行 + auto 行。顶部大横幅占50-60%高度+底部小卡片横排。
> 适用数据：1个 headline 数据/大图 + 多个辅助指标。常见于 metrics 汇总页。
> 顶部 anchor 用 elevated/accent，底部 supports 用 outline/transparent 横排。

#### l-shape
**L 型版式 (主体 + 侧翼 + 底部)**
> 3张卡片。
> 空间划分建议：L形（主体60%+侧翼40% 第一行，底部100% 第二行）。
> 适用数据：核心论证+侧面佐证+底部总结的三段式页面。
> 视线轨迹：从主体深潜 -> 滑向侧面 -> 沉入底部锚定。底部卡片常做 summary/source_guidance。

#### mixed-grid
**混合网格版式**
> 4-6张卡片。
> 空间划分建议：多行多列不等大格子。信息密集仪表盘式。
> 适用数据：status_dashboard / 多指标并列展示的高密度页面。
> 注意：卡片数多时每张内容必须精炼（content_budget 严控），否则认知过载。

#### primary-secondary
**主次结合版式 (大 + 两小)**
> 3张卡片。
> 空间划分建议：左侧大卡 2/3 高度 + 右侧2个小卡堆叠。
> 适用数据：1个核心展示+2个辅助数据。常见于 big_number+支撑指标 的页面。
> 大卡用 elevated/accent，两小卡用 outline/transparent。

#### single-focus
**单一焦点版式**
> 1-2张卡片。
> 空间划分建议：单格居中，四周大量留白。
> 适用数据：单个图表/架构图/金句需要绝对聚焦的页面。visual_weight 建议 <=5。
> 留白本身就是设计语言 -- 对内容稀疏做留白压迫，制造仪式感。

#### symmetric
**对称双栏版式 (50/50)**
> 2张卡片。
> 空间划分建议：1fr 1fr 列。左右50/50等量对峙。
> 适用数据：before_after / pros_cons / A方案 vs B方案。
> 两侧必须用不同 card_style（如 filled+outline），禁止两个都用 filled。

#### t-shape
**T 型版式 (顶部横贯 + 底部偏心)**
> 3张卡片。
> 空间划分建议：T形（第一行100%横跨总览 + 第二行 1fr 1fr 两个深潜区）。
> 适用数据：总分结构 -- 1个总论/标题/KPI 横跨顶部 + 2个分论在底部。
> 顶部用 accent/elevated 制造横贯力量感，底部两格用 filled+outline 制造分区。

#### three-column
**三栏等宽版式**
> 3张卡片。
> 空间划分建议：1fr 1fr 1fr 列。三栏等宽并列。
> 适用数据：parallel_items / pricing_plans / team_profiles（3个等重并列元素）。
> 每列 card_style 必须至少用2种（如 filled+accent+outline），禁止3个全 filled。

#### waterfall
**瀑布流版式 (3 列不等高)**
> 3-5张卡片。
> 空间划分建议：多列不等高。参差高度差制造节奏。
> 适用数据：process_flows / timelines / journey_map（需要视觉节奏的序列内容）。
> 交替高低制造瀑布落差感。高列用 filled/elevated，矮列用 outline/transparent。

### blocks/

#### card-styles
**卡片视觉变体（card_style）-- PPTX 演讲设计语言**
> card_style 决策表：6种视觉存在感 -- filled(实体基底) / transparent(无界悬浮) / outline(虚境描边) / accent(灼焰核心) / glass(雾中幻影) / elevated(悬崖浮岩)。
> 规则：每页 >=2 种混用打破单调，accent 和 elevated 各最多1个/页。
> card_type 与 card_style 的内在共鸣：data_highlight 用 transparent/accent、quote 用 transparent、timeline/diagram 用 transparent（自带骨架不需方块）、comparison 用 outline、data/text/list 用 filled/outline。
> 极致反差组合：accent+transparent+filled（燃烧vs虚空vs大地）、elevated+outline+transparent（浮岩vs气泡vs幽灵）。

#### comparison
**comparison（对比块）-- 碰撞的擂台**
> 适用数据类型：before_after / pros_cons / scenario_comparison / competitive_matrix。
> 结构：双面板正面对比，left+right各含label、points[]、accent色设定，底部可选verdict总结句。
> 设计要点：右侧推荐方案用更强accent色+更大字号+更丰满内容，左侧中性色+克制排版 -- 视觉上引导结论。
> 推荐 card_style：outline（轻轻分隔两面板）。推荐布局：symmetric。

#### diagram
**diagram（图解块）-- 结构的星图**
> 适用数据类型：hierarchies / architecture_diagram / cycle_flow / decision_tree / pyramid_layers / stakeholder_map。
> 结构：nodes[]节点 + edges[]连线，支持 layered/radial/tree/flowchart 四种布局模式。
> 实现方式不限：CSS Grid嵌套盒子、内联SVG节点连线、Flexbox+伪元素连接线。
> 推荐 card_style：transparent（自带视觉骨架，方块包裹会干扰）。推荐布局：single-focus / t-shape。

#### image-hero
**image_hero（大图+叠加文字块）-- 画面的沉浸**
> 适用数据类型：image_candidates。全幅图片+叠加文字，制造情感冲击。
> 结构：需指定 image.usage(hero-background/inline-illustration) + image.placement(full-bleed/left-half) + image.content_description。
> 推荐 card_style：transparent/glass（大图不需边框束缚，或毛玻璃让文字浮在图上）。
> 适用页面类型：cover / section 等氛围页。一页最多1个 image_hero。

#### matrix-chart
**matrix_chart（象限矩阵块）-- 象限的定位**
> 适用数据类型：matrix_data / swot / competitive_matrix。2x2象限坐标定位。
> 结构：axes(x_label, y_label) + quadrants[4]({label, items[], color})。
> 设计要点：每象限独立色块，items用定位圆点标记，适合战略分析和多维评估。
> 推荐布局：single-focus / primary-secondary。

#### people
**people（人物组块）-- 面孔的力量**
> 适用数据类型：team_profiles / user_testimonials。
> 结构：persons[]({name, title, avatar_desc, quote?})，3-6人一组。
> 设计要点：圆形头像占位+姓名+职位，引述用斜体+小字号。无真实照片时用渐变色块+首字母。
> 推荐 card_style：filled/outline。推荐布局：symmetric / three-column。

#### quote
**quote（引用/金句块）-- 灵魂的锚点**
> 适用数据类型：expert_quotes / user_testimonials。大引号+金句独立悬浮。
> 结构：quote_text + attribution(name, title, organization)。
> 设计要点：超大装饰引号(font-size:120px, opacity:0.1)、引文 font-size:28-36px、来源 font-size:14px。
> 推荐 card_style：transparent（文字靠自身重力撑住画面），1页最多1个 quote 卡。

#### timeline
**timeline（时间线块）-- 时间的河流**
> 适用数据类型：timelines / journey_map / gantt_data。横向/纵向轴线+节点。
> 结构：orientation(horizontal/vertical) + nodes[]({time, title, description, highlight})。
> 设计要点：highlight 节点用 accent 实心+更大尺寸，普通节点描边+小尺寸。4-8节点为宜，超过8个拆页。
> 推荐 card_style：transparent（自带轴线骨架）。推荐布局：l-shape / waterfall。

### charts/

#### comparison-bar
**对比柱（两项对比）**
> 适用数据类型：before_after / scenario_comparison。两根柱子高度差=结论。
> 数据需求：2组数据，每组需有 label + value。柱宽 >=40px，间距16px，总宽度自适应容器。
> PPTX 友好实现：纯 CSS div 高度百分比（不用 canvas/chart.js），柱体直接用 var(--accent-1) 和 var(--accent-2)。

#### funnel
**漏斗图 Funnel（转化流程）**
> 适用数据类型：funnel_data。逐层收窄色块=转化流失。
> 数据需求：3-6层，每层需有 label + value + conversion_rate。宽度按比例递减。
> PPTX 友好实现：梯形 div（clip-path或border），色彩从深到浅渐变，每层之间留 4px 间隙。

#### kpi
**KPI 指标卡（数字+趋势箭头+标签）**
> 适用数据类型：metrics / number_highlights / milestone_results。
> 数据需求：单个核心数字 + 趋势方向(up/down/flat) + 变化百分比 + 标签。
> 结构：大数字 font-size:40-64px font-weight:800 + SVG三角箭头(16x16) + 变化值 + 标签。
> PPTX 友好实现：纯 HTML+CSS，箭头用内联SVG polygon，tabular-nums 对齐数字。

#### metric-row
**指标行（数字+标签+进度条 组合）**
> 适用数据类型：metrics / kv_pairs。横向一行=一个指标故事。
> 数据需求：3-5个指标，每个需有 value + label + 可选 progress(0-100)。
> 结构：flex 横排，每项内部 value(大字号) + label(小字号) + progress-bar(可选)。

#### progress-bar
**进度条（百分比/完成度）**
> 适用数据类型：progress_tracker。填充长度=完成度。
> 数据需求：percentage(0-100) + label + 可选 milestone_markers[]。
> PPTX 友好实现：外层 div(background:轨道色) + 内层 div(width:N%, background:渐变)，高度 8-12px 圆角。

#### radar
**雷达图 / 蜘蛛网图（多维度对比）**
> 适用数据类型：score_card。多边形面积=综合实力。
> 数据需求：3-6个维度，每维度需有 dimension_name + value(0-100)。
> PPTX 友好实现：内联 SVG polygon，网格线用 stroke-dasharray，数据多边形用 fill-opacity:0.3。不用 canvas。

#### rating
**评分指示器（5分制）**
> 适用数据类型：score_card / ranked_list。实心vs空心=已达到vs未达到。
> 数据需求：score(1-5) + label。
> PPTX 友好实现：5个内联SVG圆点(r=6)，实心用 accent 色 fill，空心用 stroke-only + fill:none。

#### ring
**环形百分比（推荐用内联 SVG）**
> 适用数据类型：pie_data / cost_breakdown。圆弧饱满度=占比。
> 数据需求：value + total（或 percentage），可选 label。
> PPTX 友好实现：内联 SVG circle + stroke-dasharray 计算弧长，圆心大数字叠加。不用 canvas。

#### sparkline
**迷你折线图 Sparkline（趋势方向）**
> 适用数据类型：trend_series。一条折线=趋势方向。
> 数据需求：5-12个数据点序列，不需Y轴标签。适合嵌入卡片内的迷你趋势图。
> PPTX 友好实现：内联 SVG polyline，stroke-width:2，无网格线，可选渐变 fill 下方区域。

#### stacked-bar
**堆叠条形图（多分类占比对比）**
> 适用数据类型：distribution_data / cost_breakdown。一根柱子内的成分分析。
> 数据需求：2-5个分类，每分类需有 label + value + color。多根并排时可对比不同类别。
> PPTX 友好实现：flex 横排 div，每段宽度按比例，用 var(--accent-N) 配色。

#### timeline
**时间轴 Timeline（水平版）**
> 适用数据类型：timelines。水平节点串联=时间河流。
> 数据需求：3-8个节点，每节点需有 time + title + 可选 description。
> 纯图表样式（比 blocks/timeline 更轻量），适合嵌入内容页的时间进度条。

#### treemap
**矩形树图 Treemap（层级结构占比）**
> 适用数据类型：distribution_data / cost_breakdown。面积大小=重要性大小。
> 数据需求：4-12个项目，每项需有 label + value。
> PPTX 友好实现：CSS Grid 计算面积占比，每格用不同 accent 色+白色标签。不用 D3。

#### waffle
**点阵图 Waffle Chart（百分比直觉化）**
> 适用数据类型：distribution_data / progress_tracker。100格点阵亮灭=百分比。
> 数据需求：percentage(0-100)。适合单指标直觉呈现。
> PPTX 友好实现：10x10 CSS Grid，每格 8x8px gap:2px，亮格用 accent 色，暗格用 opacity:0.15。

### styles/

#### blue-white
**蓝白商务 (blue_white) -- 最通用的默认风格**
> 适用场景：企业介绍、培训课件、教育材料、医疗/金融行业、一般性汇报、未明确指定风格的大多数场景

#### dark-tech
**暗黑科技 (dark_tech) -- "发布会"感**
> 适用场景：技术产品发布、开发者工具演示、AI/ML 模型展示。注意：仅当主题**明确**是技术产品展示、开发者工具、深度技术架构讲解时才选用。

#### fresh-green
**清新自然 (fresh_green) -- "有机"感**
> 适用场景：环保/可持续发展、健康/医疗/养生、食品/农业、美妆/护肤

#### luxury-purple
**紫金奢华 (luxury_purple) -- "高定"感**
> 适用场景：时尚/奢侈品、高端服务/地产、设计/创意行业、品牌发布会

#### minimal-gray
**极简灰白 (minimal_gray) -- "学术论文"感**
> 适用场景：学术/研究报告、法务/合规、咨询/顾问报告、数据分析

#### royal-red
**朱红宫墙 (royal_red) -- "国风"感**
> 适用场景：文化/历史主题、政务汇报、品牌故事、中国风

#### vibrant-rainbow
**活力彩虹 (vibrant_rainbow) -- "创意"感**
> 适用场景：社交/娱乐平台、营销/推广材料、年轻品牌、创意方案

#### warm-earth
**暖色大地 (warm_earth) -- "精品咖啡馆"感**
> 适用场景：消费品/生活方式、创业路演、文化创意、餐饮/零售、人文社科

### principles/

#### cognitive-load
**认知负荷与信息密度**
> 观众的工作记忆有限（7 +/- 2 个信息块）。超出容量的信息不是"丰富"，而是"噪音"。
> 影响字段：`visual_weight`、`cards[].content_budget`、`rhythm_action`、`negative_space_target`。
> 当一页卡片 >= 4 张或同时出现 >= 2 种图表时，必须引用此原则并严控内容预算。

#### color-psychology
**色彩心理与运用**
> 色彩不是装饰，它是无声的语言。选错颜色比选错字体危害更大。
> 影响字段：`cards[].card_style`、`decoration_hints.page_accent`、`director_command.mood`。
> 封面页、章节页、需要情绪校准的转折页必须引用此原则；涵盖 60-30-10 法则和对比度安全。

#### composition
**构图与留白**
> 留白不是"浪费空间"，而是信息的呼吸。好的构图引导视线，差的构图让视线迷路。
> 影响字段：`layout_hint`、`layout_variation_note`、`director_command.spatial_strategy`、`focus_zone`、`negative_space_target`。
> 任何页面的排版构图优化都应引用此原则；涵盖格式塔、三分法、留白三层级。

#### data-visualization
**数据可视化原则**
> 数据可视化的目标不是"展示数据"，而是"让数据讲故事"。一个好图表让观众 3 秒内理解结论。
> 影响字段：`cards[].chart.chart_type`、`cards[].data_points`、`resources.chart_refs`。
> 数据图表主导页必须引用此原则；涵盖 Tufte 数据墨水比、图表类型选择、数据诚实。

#### design-principles-cheatsheet
**设计原则速查表 -- Step 4 字段级操作手册**
> 用途不是讲理论，而是告诉页面策划师：当 JSON 某个字段写得不对，应该改哪一项。

#### narrative-arc
**叙事结构与节奏**
> PPT 不是信息的堆砌，而是一段有起承转合的叙事旅程。观众的注意力是一条曲线，好的设计顺着它走。
> 影响字段：`narrative_role`、`rhythm_action`、`variation_guardrails.different_from_previous`。
> 叙事转折页（从问题到方案）必须引用此原则；涵盖三幕式结构、情绪曲线、节奏控制。

#### visual-hierarchy
**视觉层级与 CRAP 原则**
> 人眼不是逐字阅读，而是按视觉权重跳跃扫描。设计的核心任务是用视觉手段控制阅读顺序。
> 影响字段：`visual_weight`、`cards[].role`、`cards[].card_style`、`director_command.anchor_treatment`。
> 多卡片排版、需要层次感的页面必须引用此原则；涵盖 CRAP 四原则、对比、对齐、重复、亲密。

### page-templates/

#### cover
**封面页 -- 演讲的第一声呼吸**
> 封面决定了观众在接下来 30 分钟里是带着期待还是带着懒散听下去。一张让人"屏息一秒"的封面，等于赢了演讲的前 10%。
> 必须元素：主标题（唯一硬约束）。可选：副标题、演讲者、机构、日期、背景图/装饰。
> 1-2 张卡片为宜（quote/text/image_hero），visual_weight <= 5，大量留白制造仪式感。
> 禁止信息过载；禁止 mixed-grid；推荐 single-focus 或不设 layout_hint 让模板自由发挥。

#### end
**结束页 -- 演讲的最后一个视觉印记**
> 结束页是观众离开前看到的最后一帧。它决定了观众带走的是"印象深刻"还是"终于结束了"。
> 必须元素：CTA（行动号召）或总结金句。可选：联系方式、二维码、致谢词、品牌锚点。
> 1-2 张卡片（quote/text），visual_weight <= 4，留白比封面更大。
> 禁止塞数据图表；禁止出现新论点；推荐 single-focus。

#### section
**章节封面页 -- 演讲中的呼吸**
> 章节封面是"呼吸页"，它的存在不是为了传达信息，而是为了**让观众的大脑在信息密集区之间获得片刻松弛**。
> 必须元素：章节标题。可选：章节编号、一句话导语、背景装饰。
> 1 张卡片（text），visual_weight <= 3，全页留白最高的页面类型。
> 禁止放数据卡片；禁止多于 2 张卡片；推荐 single-focus。

#### toc
**目录页 -- 演讲的地图俯瞰**
> 目录页不是"白纸上列了几行字"。它是整场演讲的**空间全景** -- 让观众在正式深入之前，先从高空俯瞰整个旅程的轮廓。
> 必须元素：章节标题列表（3-6 项）。可选：章节编号、页码范围、进度指示、当前章节高亮。
> 1-2 张卡片（list/text），visual_weight <= 4。用编号或图标区分章节，用 accent 色高亮当前章节。
> 禁止放数据图表；推荐 single-focus 或 asymmetric（标题+列表）。

### design-runtime/

#### css-weapons
**CSS 高级武器库（W1-W12）**
> 由 `scripts/resource_loader.py` 根据每页 `decoration_hints`（含 W 编号）按需注入到 prompt-ready 文件中。
> 每页只注入被引用的武器代码，不灌全量。相邻页的武器组合应该不同。
> 策划阶段在 `decoration_hints` 中用 W 编号引用武器：如 `W1 渐变文字 | 标题用 accent-1 → accent-2 135deg`。

#### data-type-decoration-mapping
**数据类型 -> 装饰灵感参考索引**
> 本表提供不同数据类型极其高级的装饰意图参考（T 技法与 W 武器）。
> 你不必机械地被其束缚，完全可以跨界调用（例如给文本加上数据类型的铺衣）。但一旦你选定了特定组合，它就不再是儿戏，而会变成向下游强制下达的工程执行契约，绝不允许在最终呈现上打折扣。
>
> **使用原则**：
> - 不要每次都用同样的 T 和 W 组合。
> - 不要照抄清单。如果本页表达的是"突围"，即便数据类型是表格，也可以使用斜切（T5）和出血（W9c）。
> - 同一页面存在多种数据类型时，不要机械混合所有武器，而是选择 1-2 个核心武器放大使用。

#### data-type-visual-mapping
**数据类型 -> 视觉呈现参考索引**
> 本表将 brief 中的核心数据类型（metrics、timelines、before_after 等 40+ 种）严格映射到工程上的 `card_type`、`layout_hint` 和最佳 CSS 实现参考。
> **铁血纪律**：本表是架构引擎的刚性映射组件库，绝非供人随意弃用的“灵感”。Planning sub-agent 在设定好“视觉焦点与动线”后，遇到特定的数据类型，**必须首选在此表内选取最优解去承接**。自由的代价就是质量崩塌与结构散乱，请严格向最佳实践收敛。
> 覆盖 8 大类：数据展示、商业分析、对比论证、流程结构、叙事内容、技术学术、进度状态、团队与地理。

#### design-specs
**设计规格书（A/B/C/D/E -- 稳定参考，由 `scripts/resource_loader.py` 自动注入 GLOBAL_RESOURCES）**
> 本文件包含画布规范、排版阶梯、卡片规则、色彩装饰、页面类型设计和输出规范。
> 内容稳定且不需要每次都在 LLM 上下文中占位，由 assembler 机械化注入。

#### director-command-examples
**Director Command 示例库（10 种页面类型 * 2 个示例）**
> 非默认资料。human-only calibration library。
>
> 本文件不进入 planning runtime preload，不应整包注入子代理上下文。它只用于人工校准、调试和对照分析，不作为默认主链参考。

#### director-command-rules
**Director Command Runtime Rules**
> 本文件是 Step 4 runtime 主链专用的 `director_command` 规则文档。
>
> 它只定义字段职责、写法边界、选择规则和失败模式，不提供示例库，不提供成品镜头脚本。