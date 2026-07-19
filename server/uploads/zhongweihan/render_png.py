# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright

OUT = "/tmp/opencode/ai-chat/server/uploads/zhongweihan/ppt-output/runs/20260716-141627-zizhujiashi"
SLIDES = os.path.join(OUT, "slides")
PNG = os.path.join(OUT, "png")
REVIEW = os.path.join(OUT, "review")
os.makedirs(PNG, exist_ok=True)
os.makedirs(REVIEW, exist_ok=True)
TOTAL = 10
scale = float(os.environ.get("SCALE", "3"))

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu", "--force-color-profile=srgb"])
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=scale)
    for n in range(1, TOTAL + 1):
        path = os.path.join(SLIDES, f"slide-{n}.html")
        page.goto("file://" + os.path.abspath(path), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        out = os.path.join(PNG, f"slide-{n}.png")
        page.screenshot(path=out, clip={"x": 0, "y": 0, "width": 1280, "height": 720})
        # round archive
        rdir = os.path.join(REVIEW, "round1")
        os.makedirs(rdir, exist_ok=True)
        page.screenshot(path=os.path.join(rdir, f"slide-{n}.png"), clip={"x": 0, "y": 0, "width": 1280, "height": 720})
    browser.close()
print("rendered", TOTAL, "png at scale", scale)
