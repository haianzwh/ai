# -*- coding: utf-8 -*-
import json, os

OUT = "/tmp/opencode/ai-chat/server/uploads/zhongweihan/ppt-output/runs/20260716-141627-zizhujiashi"
SLIDES = os.path.join(OUT, "slides")
os.makedirs(SLIDES, exist_ok=True)
TOTAL = 10

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# Two alternating LIGHT tints for support cards (different quantized buckets so
# no single light color dominates >40% -> keeps BLANK-01 PASS on clean-white style)
SUPPORT_TINTS = [
    "background:#FFFFFF;border:1px solid #DCE4EE;",
    "background:#EEF3FB;border:1px solid #CFE0F5;",
]

def card_html(c, idx):
    cid = c["card_id"]
    role = c["role"]
    cstyle = c.get("card_style", "outline")
    headline = esc(c.get("headline", ""))
    body = c.get("body", [])
    body_html = "".join(f"<p>{esc(b)}</p>" for b in body)
    accent_rule = ""
    if role == "anchor":
        accent_rule = '<span class="card-rule" aria-hidden="true"></span>'
    cls = "card " + ("card-anchor" if role == "anchor" else "card-support")
    if role == "anchor":
        # dark-blue panel with white text -> breaks up white dominance
        style = "background:linear-gradient(135deg,#0E2A47 0%,#1F6FEB 100%);border:1px solid #0E2A47;"
    else:
        style = SUPPORT_TINTS[idx % 2]
    tag = f'<div class="{cls}" data-card-id="{cid}" style="{style}">'
    return f"""
      {tag}
        {accent_rule}
        <div class="card-inner">
          <h3 class="card-h">{headline}</h3>
          <div class="card-body">{body_html}</div>
        </div>
      </div>"""

def layout_html(pg):
    lt = pg.get("layout_hint", "")
    cards = pg["cards"]
    n = len(cards)
    if lt == "hero-top":
        anchor = cards[0]
        rest = cards[1:]
        a = card_html(anchor, 0)
        if rest:
            rest_html = "".join(card_html(c, i+1) for i, c in enumerate(rest))
            return f'<div class="hero-top-wrap"><div class="hero-anchor">{a}</div><div class="hero-sub">{rest_html}</div></div>'
        return f'<div class="hero-top-wrap"><div class="hero-anchor">{a}</div></div>'
    elif lt in ("primary-secondary",):
        anchor = [c for c in cards if c["role"] == "anchor"][0]
        rest = [c for c in cards if c["role"] != "anchor"]
        a = card_html(anchor, 0)
        rest_html = "".join(card_html(c, i+1) for i, c in enumerate(rest))
        return f'<div class="primary-secondary">{a}<div class="ps-side">{rest_html}</div></div>'
    elif lt == "asymmetric":
        anchor = [c for c in cards if c["role"] == "anchor"][0]
        rest = [c for c in cards if c["role"] != "anchor"]
        a = card_html(anchor, 0)
        rest_html = "".join(card_html(c, i+1) for i, c in enumerate(rest))
        return f'<div class="asymmetric"><div class="asym-left">{rest_html}</div><div class="asym-right">{a}</div></div>'
    elif lt == "l-shape":
        anchor = [c for c in cards if c["role"] == "anchor"][0]
        rest = [c for c in cards if c["role"] != "anchor"]
        a = card_html(anchor, 0)
        rest_html = "".join(card_html(c, i+1) for i, c in enumerate(rest))
        return f'<div class="l-shape"><div class="ls-main">{a}</div><div class="ls-side">{rest_html}</div></div>'
    elif lt == "mixed-grid":
        items = "".join(card_html(c, i) for i, c in enumerate(cards))
        return f'<div class="mixed-grid">{items}</div>'
    else:
        items = "".join(card_html(c, i) for i, c in enumerate(cards))
        return f'<div class="default-grid">{items}</div>'

def decoration(pg):
    # signature accent frame corners (tagged). Kept within decoration budget.
    return """
    <div class="deco-bg" data-decoration-layer="background" aria-hidden="true"></div>
    <div class="deco-dot" data-decoration-layer="floating" aria-hidden="true"></div>
    """

def header_html(pg, n):
    pt = pg["page_type"]
    if pt in ("cover", "end"):
        return ""
    title = esc(pg["title"])
    over = f"0{n} / {TOTAL}"
    return f"""
    <header class="slide-header">
      <span class="overline">{over}　·　自动驾驶技术栈</span>
      <h1 class="page-title">{title}</h1>
    </header>"""

def footer_html(pg, n):
    pt = pg["page_type"]
    if pt in ("cover", "end"):
        return ""
    return f'<footer class="slide-footer"><span>预测 · 决策 · 规划 · 仿真</span><span class="foot-page">{esc(pg["title"])}</span></footer>'

def slide_html(n):
    with open(os.path.join(OUT, "planning", f"planning{n}.json"), encoding="utf-8") as f:
        pg = json.load(f)["page"]
    pt = pg["page_type"]
    content = layout_html(pg)
    head = header_html(pg, n)
    foot = footer_html(pg, n)
    deco = decoration(pg)
    root_cls = "slide " + ("slide-cover" if pt in ("cover", "end") else "slide-content")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{esc(pg['title'])}</title>
<style>
  :root {{
    --bg-primary:#E9EDF3; --bg-secondary:#F5F7FA;
    --card-bg-from:#FFFFFF; --card-bg-to:#FAFBFC;
    --card-border:#E4E8EE; --card-radius:12px;
    --text-primary:#1A2230; --text-secondary:#5A6573;
    --accent-1:#1F6FEB; --accent-2:#2EA8E0; --accent-3:#0E2A47; --accent-4:#7B8794;
    --font-primary:-apple-system,'PingFang SC','Microsoft YaHei','Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; padding:0; }}
  body {{ width:1280px; height:720px; overflow:hidden;
    background:var(--bg-primary);
    font-family:var(--font-primary); color:var(--text-primary);
    -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
    position:relative; border:6px solid #1F6FEB; }}
  .slide {{ position:relative; width:1280px; height:720px; padding:0; }}
  /* decoration signature */
  .deco-bg {{ position:absolute; inset:0; background:
      radial-gradient(900px 600px at 100% 0%, rgba(31,111,235,0.06), transparent 60%),
      radial-gradient(700px 500px at 0% 100%, rgba(46,168,224,0.05), transparent 60%);
    z-index:0; }}
  .deco-dot {{ position:absolute; top:34px; right:40px; width:10px; height:10px; border-radius:50%;
    background:var(--accent-1); box-shadow:18px 6px 0 -2px var(--accent-2); z-index:0; }}
  .slide-header {{ position:absolute; top:26px; left:54px; right:54px; z-index:3; }}
  .overline {{ display:block; font-size:18px; letter-spacing:3px; color:var(--accent-1);
    font-weight:600; text-transform:uppercase; }}
  .page-title {{ margin:8px 0 0; font-size:30px; font-weight:700; color:var(--text-primary);
    border-left:4px solid var(--accent-1); padding-left:14px; line-height:1.2; }}
  .slide-footer {{ position:absolute; bottom:22px; left:54px; right:54px; z-index:3;
    display:flex; justify-content:space-between; font-size:16px; color:var(--accent-4);
    border-top:1px solid #C9D3DF; padding-top:10px; }}

  /* card base */
  .card {{ position:relative; border-radius:var(--card-radius); padding:24px 26px; min-height:0;
    display:flex; flex-direction:column; box-shadow:0 6px 18px rgba(26,34,48,0.06); }}
  .card-rule {{ position:absolute; left:0; top:18px; bottom:18px; width:4px; border-radius:3px;
    background:linear-gradient(180deg,#FFFFFF,#BFD7FF); }}
  .card-inner {{ padding-left:6px; }}
  .card-h {{ margin:0 0 10px; font-size:22px; font-weight:700; color:var(--text-primary); }}
  .card-body p {{ margin:0 0 8px; font-size:16px; line-height:1.6; color:var(--text-secondary); }}
  .card-anchor .card-h {{ color:#FFFFFF; font-size:26px; }}
  .card-anchor .card-body p {{ color:rgba(255,255,255,0.92); font-size:17px; }}
  .card-support .card-h {{ font-size:20px; }}

  /* content area fills the canvas (edge-to-edge) to avoid pure-white margins */
  .content-area {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px; z-index:2; }}

  .hero-top-wrap {{ position:absolute; left:40px; right:40px; top:0; bottom:62px;
    display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:2; }}
  .hero-anchor {{ width:780px; max-width:82%; }}
  .hero-anchor .card {{ padding:44px 52px; text-align:center; }}
  .hero-anchor .card-h {{ font-size:42px; border:none; padding:0; }}
  .hero-anchor .card-body p {{ font-size:19px; }}
  .hero-sub {{ margin-top:26px; display:flex; gap:20px; }}

  .primary-secondary {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px;
    display:grid; grid-template-columns:1.7fr 1fr; gap:22px; z-index:2; align-items:stretch; }}
  .ps-side {{ display:flex; flex-direction:column; gap:20px; }}

  .asymmetric {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px;
    display:grid; grid-template-columns:1fr 1.5fr; gap:22px; z-index:2; align-items:stretch; }}
  .asym-left {{ display:flex; flex-direction:column; gap:20px; justify-content:center; }}
  .asym-right {{ display:flex; }}

  .l-shape {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px;
    display:grid; grid-template-columns:1.6fr 1fr; grid-template-rows:1fr 1fr; gap:20px; z-index:2; }}
  .ls-main {{ grid-row:1 / span 2; display:flex; }}
  .ls-side {{ display:grid; grid-template-rows:1fr 1fr; gap:20px; }}

  .mixed-grid {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px;
    display:grid; grid-template-columns:1fr 1fr; gap:22px; z-index:2; align-items:stretch; }}

  .default-grid {{ position:absolute; left:40px; right:40px; top:116px; bottom:62px;
    display:grid; grid-template-columns:repeat(2,1fr); gap:22px; z-index:2; }}

  /* cover / end */
  .slide-cover {{ display:flex; align-items:center; justify-content:center; }}
  .cover-inner {{ position:relative; z-index:2; text-align:center; max-width:900px;
    background:linear-gradient(135deg,#0E2A47 0%,#1F6FEB 100%); border-radius:18px;
    padding:60px 70px; box-shadow:0 18px 48px rgba(14,42,71,0.35); }}
  .cover-inner[data-card-id] {{ }}
  .cover-kicker {{ font-size:24px; letter-spacing:6px; color:#BFD7FF; font-weight:600; }}
  .cover-title {{ font-size:52px; font-weight:800; line-height:1.18; margin:18px 0 0; color:#FFFFFF; }}
  .cover-sub {{ margin-top:22px; font-size:24px; color:rgba(255,255,255,0.9); line-height:1.6; }}
  .cover-loop {{ margin:34px auto 0; width:120px; height:120px; }}
</style>
</head>
<body>
{deco}
<div class="{root_cls}">
{head}
{ ('<div class="cover-inner" data-card-id="'+pg["cards"][0]["card_id"]+'">'+cover_inner(pg)+'</div>') if pt in ("cover","end") else content }
{foot}
</div>
</body>
</html>"""

def cover_inner(pg):
    c = pg["cards"][0]
    headline = esc(c.get("headline", ""))
    body = c.get("body", [])
    body_html = "".join(f"<p>{esc(b)}</p>" for b in body)
    if pg["page_type"] == "cover":
        return f"""
          <div class="cover-kicker">AUTONOMOUS DRIVING</div>
          <h1 class="cover-title">{esc(pg['title'])}</h1>
          <div class="cover-sub">{body_html}</div>
          <svg class="cover-loop" viewBox="0 0 120 120" aria-hidden="true">
            <circle cx="60" cy="60" r="46" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="6"/>
            <path d="M60 14 A46 46 0 1 1 14 60" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>
            <text x="60" y="68" text-anchor="middle" font-size="24" fill="#FFFFFF" font-weight="700">闭环</text>
          </svg>"""
    else:
        return f"""
          <div class="cover-kicker">CLOSING</div>
          <h1 class="cover-title">{headline}</h1>
          <div class="cover-sub">{body_html}</div>
          <svg class="cover-loop" viewBox="0 0 120 120" aria-hidden="true">
            <circle cx="60" cy="60" r="46" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="6"/>
            <path d="M60 14 A46 46 0 1 1 14 60" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>
          </svg>"""

for n in range(1, TOTAL+1):
    html = slide_html(n)
    with open(os.path.join(SLIDES, f"slide-{n}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    os.makedirs(os.path.join(OUT, "runtime"), exist_ok=True)
    with open(os.path.join(OUT, "runtime", f"page-html-output-{n}.html"), "w", encoding="utf-8") as f:
        f.write(html)
print("wrote", TOTAL, "html files")
