# -*- coding: utf-8 -*-
import json, os, copy

OUT = "/tmp/opencode/ai-chat/server/uploads/zhongweihan/ppt-output/runs/20260716-141627-zizhujiashi"

# shared style anchors (from style.json)
ACCENT = "#1F6FEB"
ACCENT2 = "#2EA8E0"
TEXT1 = "#1A2230"
TEXT2 = "#5A6573"
BG2 = "#F5F7FA"
CARD_BORDER = "#E4E8EE"

def base(slide_number, page_type, narrative_role, title, page_goal, takeaway,
         visual_weight, density_label, density_reason, layout_hint, layout_variation_note,
         focus_zone, negative_space, text_strategy, rhythm, must_avoid, same_gene,
         diff_prev, mood, spatial, anchor_treat, techniques, prose,
         bg_feel, bg_restraint, bg_tech, float_feel, float_restraint, float_tech,
         accent_feel, accent_restraint, accent_tech, brief_sections, citation, strictness,
         page_template, layout_refs, chart_refs, principle_refs, rationale, cards):
    # deck-level density contract (balanced)
    deck_bias = "balanced"
    # per-label budgets
    budgets = {
        "low": dict(max_cards=2, max_charts=1, min_body_font_px=24, max_lines_per_card=3, image_policy="flexible", decoration_budget="generous", overflow_strategy="rebalance_layout"),
        "mid_low": dict(max_cards=3, max_charts=1, min_body_font_px=20, max_lines_per_card=4, image_policy="flexible", decoration_budget="medium", overflow_strategy="rebalance_layout"),
        "medium": dict(max_cards=4, max_charts=2, min_body_font_px=18, max_lines_per_card=5, image_policy="support_only", decoration_budget="medium", overflow_strategy="tighten_budget"),
        "high": dict(max_cards=6, max_charts=2, min_body_font_px=16, max_lines_per_card=4, image_policy="support_only", decoration_budget="low", overflow_strategy="table_or_microchart"),
        "dashboard": dict(max_cards=8, max_charts=4, min_body_font_px=14, max_lines_per_card=3, image_policy="decorate_only", decoration_budget="minimal", overflow_strategy="rollback_planning"),
    }
    b = budgets[density_label]
    lb, ub = {"low": "low", "mid_low": "mid_low", "medium": "medium", "high": "high", "dashboard": "dashboard"}[density_label], density_label
    # upper bound derived from label
    order = ["low", "mid_low", "medium", "high", "dashboard"]
    idx = order.index(density_label)
    ub_label = order[min(idx + 1, len(order) - 1)]
    contract = {
        "deck_bias": deck_bias,
        "page_lower_bound": density_label,
        "page_upper_bound": ub_label,
        "max_cards": b["max_cards"],
        "max_charts": b["max_charts"],
        "min_body_font_px": b["min_body_font_px"],
        "max_lines_per_card": b["max_lines_per_card"],
        "image_policy": b["image_policy"],
        "decoration_budget": b["decoration_budget"],
        "overflow_strategy": b["overflow_strategy"],
    }
    return {
        "page": {
            "slide_number": slide_number,
            "page_type": page_type,
            "narrative_role": narrative_role,
            "title": title,
            "page_goal": page_goal,
            "audience_takeaway": takeaway,
            "visual_weight": visual_weight,
            "density_label": density_label,
            "density_reason": density_reason,
            "density_contract": contract,
            "layout_hint": layout_hint,
            "layout_variation_note": layout_variation_note,
            "focus_zone": focus_zone,
            "negative_space_target": negative_space,
            "page_text_strategy": text_strategy,
            "rhythm_action": rhythm,
            "must_avoid": must_avoid,
            "variation_guardrails": {
                "same_gene_as_deck": same_gene,
                "different_from_previous": diff_prev,
            },
            "director_command": {
                "mood": mood,
                "spatial_strategy": spatial,
                "anchor_treatment": anchor_treat,
                "techniques": techniques,
                "prose": prose,
            },
            "decoration_hints": {
                "background": {"feel": bg_feel, "restraint": bg_restraint, "techniques": bg_tech},
                "floating": {"feel": float_feel, "restraint": float_restraint, "techniques": float_tech},
                "page_accent": {"feel": accent_feel, "restraint": accent_restraint, "techniques": accent_tech},
            },
            "source_guidance": {
                "brief_sections": brief_sections,
                "citation_expectation": citation,
                "strictness": strictness,
            },
            "resources": {
                "page_template": page_template,
                "layout_refs": layout_refs,
                "block_refs": [],
                "chart_refs": chart_refs,
                "principle_refs": principle_refs,
                "resource_rationale": rationale,
            },
            "cards": cards,
            "workflow_metadata": {
                "stage": "planning",
                "workflow_version": "2026.04.09-v4.1",
                "planning_schema_version": "4.1",
                "planning_packet_version": "4.1",
                "planning_continuity_version": "4.1",
            },
        }
    }

SAME = "科技蓝细竖线锚点、白底、字体角色、圆角与全 deck 一致"
BRIEF_TOTAL = ["总览：四大模块的闭环关系"]
BRIEF_PRED = ["预测模块（洞悉他人的未来）"]
BRIEF_DP = ["决策与规划（自车的行动指南）"]
BRIEF_SIM = ["仿真模块（虚拟世界里的实战演练）"]

def tcard(cid, role, ctype, cstyle, arg, headline, body, budget, decorate=None, chart=None, data_points=None, decorate_brief=None):
    c = {
        "card_id": cid,
        "role": role,
        "card_type": ctype,
        "card_style": cstyle,
        "argument_role": arg,
        "headline": headline,
        "body": body,
        "data_points": data_points or [],
        "chart": {"chart_type": chart} if chart else {"chart_type": None},
        "content_budget": budget,
        "image": {
            "mode": "decorate", "needed": False, "usage": None, "placement": None,
            "content_description": None, "source_hint": None,
            "decorate_brief": decorate_brief or decorate or "浅灰描边卡片内用科技蓝小图标点缀",
        },
        "resource_ref": {"chart": None, "principle": "visual-hierarchy"},
    }
    return c

pages = {}

# ---- Page 1: cover ----
pages[1] = base(1, "cover", "cover", "自动驾驶的预测、规划、决策与仿真",
    "点题四大模块构成思考-行动-验证闭环", "记住预测/决策/规划/仿真四者构成闭环",
    3, "low", "封面页聚焦标题与一句话定位，低密度留出呼吸感",
    "hero-top", "封面居中 hero 聚焦，与后续内容页左对齐网格形成反差",
    "画面中心偏上：主标题 + 副标题", "high", "主标题一句话点题，副标题一句定位",
    "铺垫", ["避免把四大模块拆成并排卡片，封面应保持极简聚焦"], SAME,
    ["居中构图而非左对齐", "呼吸页留白强度远高于内容页"],
    "克制、专业、可信", "中心轴线对称，主标题为视觉重心，下方细线引导一行定位语",
    "主标题大字重科技蓝，副标题灰色弱化", ["center-axis", "thin-blue-rule", "generous-whitespace"],
    "干净白光里标题如路牌稳立画面中央，四周大量留白",
    "纯净通透", "仅极淡蓝灰渐变角", ["soft-corner-gradient"], "几乎无", "高", ["single-blue-dot"],
    "科技蓝细竖线", "中", ["left-blue-rule"], BRIEF_TOTAL, "封面不引用具体数据", "仅用原文总览句做副标题",
    "cover", ["hero-top"], [], ["color-psychology", "composition"],
    "封面需情绪校准与构图稳定，选用 cover 模板与 hero-top 布局",
    [tcard("s1-anchor-1", "anchor", "text", "accent", "claim", "思考-行动-验证闭环",
           ["预测、决策、规划、仿真", "让车辆在复杂交通中安全行驶"],
           {"headline_max_chars": 12, "body_max_bullets": 2, "body_max_lines": 2},
           decorate_brief="右侧极淡科技蓝环形箭头示意闭环")])

# ---- Page 2: overview closed loop ----
pages[2] = base(2, "content", "comparison", "四大模块的“思考-行动-验证”闭环",
    "预测到仿真构成相互反馈的完整闭环", "一眼看懂四模块首尾相接的关系",
    7, "high", "总览页需承载环形链路与四模块说明共5卡，提升至 high 密度以容纳",
    "l-shape", "总览用 L 型：左上主体关系链 + 右侧四模块说明 + 底部一句定位",
    "主体左侧：预测→决策→规划→仿真 的环形链路", "medium", "以关系链为锚，模块说明为辅助",
    "铺垫", ["避免四模块做成平均四宫格，必须体现流向与闭环"], SAME,
    ["增加关系链主锚", "用环形而非并列"],
    "清晰、系统、有结构感", "L 形主体承载环形链路，右侧列四模块一句话定位，底部收束",
    "环形链路用 accent 强调，模块卡片 outline 弱化", ["loop-diagram", "l-shape", "flow-arrows"],
    "四条线索首尾相扣成环，像仪表盘的中心结构图",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "科技蓝环形箭头", "中", ["loop-accent"], BRIEF_TOTAL, "用原文四模块定义做卡片文案", "严格基于原文",
    None, ["l-shape"], [], ["visual-hierarchy", "composition"],
    "L 型适合核心论证+侧面佐证+底部总结的三段式",
    [
      tcard("s2-anchor-1", "anchor", "diagram", "accent", "claim", "闭环链路",
            ["预测 → 决策 → 规划 → 仿真", "仿真反馈优化前三者，形成闭环"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2},
            decorate_brief="四节点环形箭头，节点用科技蓝"),
      tcard("s2-support-1", "support", "text", "outline", "evidence", "预测",
            ["“猜”他车与行人动向", "决策的依据"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s2-support-2", "support", "text", "outline", "evidence", "决策",
            ["决定下一步做什么", "跟车、变道等宏观行为"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s2-support-3", "support", "text", "outline", "evidence", "规划",
            ["把决策变可执行路径", "生成轨迹与速度曲线"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s2-support-4", "support", "text", "outline", "evidence", "仿真",
            ["虚拟训练场与考场", "高效安全测试优化算法"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 3: prediction intro ----
pages[3] = base(3, "content", "evidence", "预测——洞悉他人的未来",
    "预测是决策与规划的基础，精度决定可靠性", "理解预测的定位与核心价值",
    5, "medium", "解释页，定位+价值两要点，medium 密度",
    "primary-secondary", "主次结合：左侧大卡讲定位，右侧两小卡讲价值与精度",
    "左侧大卡：预测是决策与规划的基础", "medium", "主卡定调，小卡补价值与约束",
    "推进", ["避免把预测讲成方法罗列，本页聚焦定位而非方法"], SAME,
    ["主卡放大为 anchor", "改用主次结合而非对比"],
    "严谨、基础、明了", "左大右小，左卡为 anchor 占据 2/3，右两小卡堆叠",
    "左卡 accent 强调，右卡 outline 弱化", ["primary-secondary", "left-anchor"],
    "左侧一块重墨定调，右侧轻点两点支撑",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "左侧科技蓝标题竖线", "中", ["left-blue-rule"], BRIEF_PRED, "用原文定义与精度论述", "严格基于原文",
    None, ["primary-secondary"], [], ["visual-hierarchy", "composition"],
    "主次结合版式适合 1 核心 + 2 辅助",
    [
      tcard("s3-anchor-1", "anchor", "text", "accent", "claim", "预测的定位",
            ["推断周边交通参与者的未来轨迹", "是决策与规划的基础"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s3-support-1", "support", "text", "outline", "evidence", "核心目标",
            ["预测精度直接影响后续决策可靠性", "基础不牢，上层全崩"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s3-support-2", "support", "text", "outline", "evidence", "为什么难",
            ["交通参与者高度交互", "存在显著不确定性"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 4: prediction methods comparison ----
pages[4] = base(4, "content", "comparison", "预测的两种方法：拟合 vs AI",
    "传统拟合简单但弱交互，AI 模型擅复杂交互", "对比两类预测方法的取舍",
    6, "medium", "对比页，两列方法对比，medium 密度",
    "asymmetric", "非对称两栏：左传统拟合，右 AI 模型，右为 anchor",
    "右侧 AI 模型卡为视觉重点", "medium", "两列并列对比，右列强调为主",
    "推进", ["避免两列完全等重，需突出 AI 为主流方向"], SAME,
    ["改用对比两栏", "右列 accent 强调"],
    "对比、清晰、有倾向", "左右两栏对比，右栏 AI 用 accent 强调为锚",
    "右卡 accent，左卡 outline", ["two-column-compare", "right-anchor"],
    "左右两栏像天平，右侧明显更重",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "中间对比分隔线", "中", ["divider"], BRIEF_PRED, "用原文两类方法论述", "严格基于原文",
    None, ["asymmetric"], [], ["visual-hierarchy", "composition"],
    "非对称两栏适合 1 核心论点 + 1 辅助佐证",
    [
      tcard("s4-support-1", "support", "text", "outline", "evidence", "传统多项式拟合",
            ["基于历史轨迹数学拟合", "简单，但复杂交互适应性不足"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s4-anchor-1", "anchor", "text", "accent", "claim", "AI 模型预测",
            ["深度学习捕捉复杂交互与不确定性", "先预测意图再生成轨迹，输出多轨迹及概率"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 3}),
    ])

# ---- Page 5: decision & planning intro ----
pages[5] = base(5, "content", "evidence", "决策与规划——自车的行动指南",
    "决策定宏观行为，规划生成可行轨迹", "区分决策与规划的职责边界",
    5, "medium", "解释页，决策+规划两要点，medium 密度",
    "primary-secondary", "主次结合：左大卡讲决策，右两小卡讲规划与约束",
    "左侧大卡：决策是行为逻辑层", "medium", "主卡定调，小卡补规划与约束",
    "推进", ["避免把决策与规划混为一谈，须明确分层"], SAME,
    ["主卡放大为 anchor", "换内容侧重"],
    "严谨、分层、清晰", "左大右小，左卡 anchor 占 2/3，右两小卡堆叠",
    "左卡 accent，右卡 outline", ["primary-secondary", "left-anchor"],
    "左侧重墨定行为逻辑，右侧轻点路径与约束",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "左侧科技蓝标题竖线", "中", ["left-blue-rule"], BRIEF_DP, "用原文决策与规划定义", "严格基于原文",
    None, ["primary-secondary"], [], ["visual-hierarchy", "composition"],
    "主次结合版式适合 1 核心 + 2 辅助",
    [
      tcard("s5-anchor-1", "anchor", "text", "accent", "claim", "决策：行为逻辑层",
            ["依预测与目标做宏观决策", "左转/直行、超车或礼让"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s5-support-1", "support", "text", "outline", "evidence", "规划：变路径",
            ["把决策变成现实可执行路径", "生成轨迹与速度曲线"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s5-support-2", "support", "text", "outline", "evidence", "四重约束",
            ["安全性、舒适性、高效性", "与运动学约束（车辆能执行）"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 6: planning methods comparison ----
pages[6] = base(6, "content", "comparison", "规划的两种方法：Frenet vs 搜索",
    "Frenet 高效适结构化路，搜索采样善交互", "对比两类规划方法的适用场景",
    6, "medium", "对比页，两列方法对比，medium 密度",
    "asymmetric", "非对称两栏：左 Frenet，右 搜索/采样 MCTS，右为 anchor",
    "右侧搜索采样卡为视觉重点", "medium", "两列并列对比，右列强调为主",
    "推进", ["避免两列完全等重，需突出交互场景方法"], SAME,
    ["改用对比两栏", "右列 accent 强调"],
    "对比、清晰、有倾向", "左右两栏对比，右栏用 accent 强调为锚",
    "右卡 accent，左卡 outline", ["two-column-compare", "right-anchor"],
    "左右两栏对比，右侧明显更重",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "中间对比分隔线", "中", ["divider"], BRIEF_DP, "用原文两类规划方法论述", "严格基于原文",
    None, ["asymmetric"], [], ["visual-hierarchy", "composition"],
    "非对称两栏适合 1 核心论点 + 1 辅助佐证",
    [
      tcard("s6-support-1", "support", "text", "outline", "evidence", "基于 Frenet 坐标系",
            ["轨迹拆为横向/纵向独立优化", "计算高效，适高速公路等结构化道路"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s6-anchor-1", "anchor", "text", "accent", "claim", "搜索 / 采样 (MCTS)",
            ["蒙特卡洛树搜索模拟探索未来", "选出最优方案，更善交互场景"],
            {"headline_max_chars": 12, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 7: simulation intro ----
pages[7] = base(7, "content", "evidence", "仿真——虚拟世界里的实战演练",
    "仿真以低成本闭环验证算法尤其长尾场景", "理解仿真为何不可或缺",
    5, "medium", "解释页，价值+长尾两要点，medium 密度",
    "primary-secondary", "主次结合：左大卡讲价值，右两小卡讲平台与长尾",
    "左侧大卡：仿真提供闭环测试环境", "medium", "主卡定调，小卡补平台与长尾",
    "推进", ["避免把仿真讲成工具罗列，本页聚焦价值"], SAME,
    ["主卡放大为 anchor", "换内容侧重"],
    "务实、可靠、必要", "左大右小，左卡 anchor 占 2/3，右两小卡堆叠",
    "左卡 accent，右卡 outline", ["primary-secondary", "left-anchor"],
    "左侧重墨定价值，右侧轻点平台与长尾",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "左侧科技蓝标题竖线", "中", ["left-blue-rule"], BRIEF_SIM, "用原文仿真价值论述", "严格基于原文",
    None, ["primary-secondary"], [], ["visual-hierarchy", "composition"],
    "主次结合版式适合 1 核心 + 2 辅助",
    [
      tcard("s7-anchor-1", "anchor", "text", "accent", "claim", "仿真的价值",
            ["真实路测成本高、风险大", "虚拟环境快速安全低成本验证算法"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s7-support-1", "support", "text", "outline", "evidence", "平台实例",
            ["小鹏自研模拟器、华为 SMARTS", "提供闭环测试环境"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s7-support-2", "support", "text", "outline", "evidence", "长尾场景",
            ["难在现实路测中遇到", "仿真可重复验证危险场景"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 8: simulation frontier ----
pages[8] = base(8, "content", "evidence", "仿真技术前沿",
    "模仿学习与 AI 对抗诱导推动仿真更真实", "了解仿真两大前沿方向",
    7, "medium", "证据页，两前沿方向，medium 密度偏高",
    "mixed-grid", "混合网格：两前沿卡片并列，各带价值说明",
    "两张前沿卡并列为主", "medium", "两卡并列，均为主级证据",
    "爆发", ["避免两前沿写成流水账，须突出‘更像真实世界’"], SAME,
    ["改用并列网格", "密度略升体现前沿信息量"],
    "前沿、活跃、智能", "两卡并列，同济大学与 AI 对抗各占一格",
    "两卡均 accent 弱化边框，标题科技蓝", ["two-grid", "equal-emphasis"],
    "两格并排像研究看板，信息密度略高",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "网格科技蓝分隔", "中", ["grid-rule"], BRIEF_SIM, "用原文前沿研究论述", "严格基于原文",
    None, ["mixed-grid"], [], ["visual-hierarchy", "composition"],
    "混合网格适合多证据并列展示",
    [
      tcard("s8-anchor-1", "anchor", "text", "accent", "claim", "模仿学习造流",
            ["同济大学研究用模仿学习", "让虚拟交通流具人类合作/竞争策略"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s8-support-2", "support", "text", "elevated", "claim", "AI 对抗诱导",
            ["用 AI 控制其他车辆", "主动诱导被测车进入特定场景"],
            {"headline_max_chars": 10, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 9: closed loop summary ----
pages[9] = base(9, "content", "comparison", "闭环关系与价值总结",
    "四模块首尾反馈形成持续优化的闭环", "收束整套 deck 的核心结论",
    6, "medium", "结论页，环形关系 + 价值收束，medium 密度",
    "l-shape", "L 型：主体环形关系，底部一句价值收束",
    "主体环形链路回顾", "medium", "关系为锚，价值收束于底",
    "收束", ["避免与第2页总览完全雷同，本页加价值升华"], SAME,
    ["底部加价值收束带", "比总览更凝练"],
    "收束、升华、通透", "L 形主体回顾环路，底部一条 accent 价值带收束",
    "环形 accent，底部带强调", ["loop-diagram", "bottom-summary-band"],
    "环路再次浮现，底部一句点透价值",
    "极淡分区底色", "低", ["section-tint"], "弱", "高", ["none"],
    "科技蓝环形箭头", "中", ["loop-accent"], BRIEF_TOTAL, "用原文闭环与价值论述", "严格基于原文",
    None, ["l-shape"], [], ["visual-hierarchy", "composition"],
    "L 型适合核心论证 + 底部总结",
    [
      tcard("s9-anchor-1", "anchor", "diagram", "accent", "claim", "闭环回顾",
            ["预测→决策→规划→仿真", "仿真反馈优化，循环不止"],
            {"headline_max_chars": 8, "body_max_bullets": 2, "body_max_lines": 2},
            decorate_brief="四节点环形箭头浓缩版"),
      tcard("s9-support-1", "support", "text", "outline", "evidence", "预测为基",
            ["精度决定决策可靠性", "基础模块"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
      tcard("s9-support-2", "support", "text", "outline", "evidence", "仿真为场",
            ["低成本验证长尾场景", "闭环考场"],
            {"headline_max_chars": 6, "body_max_bullets": 2, "body_max_lines": 2}),
    ])

# ---- Page 10: end ----
pages[10] = base(10, "end", "cta", "闭环思维，守护每一次安全行驶",
    "闭环思维是自动驾驶安全的核心方法论", "带走一句话：闭环即安全",
    3, "low", "结尾页一句话收束，低密度留出呼吸感",
    "hero-top", "结尾居中聚焦一句话，与封面呼应",
    "画面中心：一句收束语", "high", "一句话点题，不堆要点",
    "收束", ["避免结尾又列要点，应保持极简呼应封面"], SAME,
    ["居中构图呼应封面", "呼吸页留白"],
    "克制、余韵、可信", "中心轴线，一句话为重心，下方细线",
    "收束语大字重科技蓝", ["center-axis", "thin-blue-rule", "generous-whitespace"],
    "与封面同构的白光里，一句话稳稳落地",
    "纯净通透", "仅极淡蓝灰渐变角", ["soft-corner-gradient"], "几乎无", "高", ["single-blue-dot"],
    "科技蓝细竖线", "中", ["left-blue-rule"], BRIEF_TOTAL, "不引用具体数据", "仅用原文闭环意涵",
    "end", ["hero-top"], [], ["color-psychology", "composition"],
    "结尾需情绪校准，选用 end 模板与 hero-top 布局",
    [tcard("s10-anchor-1", "anchor", "text", "accent", "claim", "闭环即安全",
           ["预测、决策、规划、仿真", "闭环驱动每一次安全行驶"],
           {"headline_max_chars": 12, "body_max_bullets": 2, "body_max_lines": 2},
           decorate_brief="极淡科技蓝环形箭头呼应封面")])

for n, obj in pages.items():
    path = os.path.join(OUT, "planning", f"planning{n}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
print("wrote", len(pages), "planning files")
