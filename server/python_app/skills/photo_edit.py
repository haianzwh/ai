"""
=============================================================================
  Photo Edit Skill — 本地 P 图技能
  基于 OpenCV，免 API Key，支持常见图片处理
=============================================================================
"""
import cv2, numpy as np
from pathlib import Path
from fastapi import FastAPI, APIRouter, Query
from fastapi.responses import FileResponse

NAME = "photo-edit"
DESC = "本地 P 图: 换发色 / 美白 / 滤镜 / 裁剪 / 压缩"


class PhotoEditSkill:
    name = NAME
    description = DESC

    async def on_register(self, app: FastAPI):
        router = APIRouter(prefix="/api/skills/photo", tags=["P图"])

        @router.get("/colors")
        async def list_colors():
            return {
                "actions": ["hair_color", "whiten", "filter", "crop", "resize", "compress"],
                "hair_colors": {
                    "棕色":"brown","金色":"blonde","红色":"red","黑色":"black","灰色":"gray",
                    "蓝色":"blue","粉色":"pink","紫色":"purple"
                },
                "filters": ["warm","cool","vintage","bw","brighten"],
                "usage": "GET /api/skills/photo/hair?path=<文件路径>&color=brown"
            }

        @router.get("/hair")
        async def change_hair_color(
            path: str = Query(..., description="图片绝对路径"),
            color: str = Query("brown", description="颜色: brown/blonde/red/black/gray/blue/pink/purple"),
            alpha: float = Query(0.5, description="混合度 0~1"),
        ):
            """
            换发色。
            彩色枚举: brown, blonde, red, black, gray, blue, pink, purple
            alpha: 颜色混合度，越小越自然
            """
            color_map = {
                "brown":  [34, 84, 156],
                "blonde": [80, 200, 255],
                "red":    [40, 40, 220],
                "black":  [30, 30, 30],
                "gray":   [128, 128, 128],
                "blue":   [200, 80, 40],
                "pink":   [180, 100, 220],
                "purple": [180, 50, 150],
            }
            bgr = color_map.get(color)

            if not bgr:
                return {"error": "未知颜色", "colors": list(color_map.keys())}

            img = cv2.imread(path)
            if img is None:
                return {"error": "图片不存在"}

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, hair_mask = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_OPEN, kernel)

            # 只处理上半部
            upper = hair_mask[:int(h * 0.6), :]
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(upper, connectivity=8)
            largest_idx = 0
            largest_area = 0

            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area > largest_area:
                    largest_area = area
                    largest_idx = i

            hair_final = np.zeros((h, w), dtype=np.uint8)

            if largest_idx > 0:
                region = (labels == largest_idx)
                hair_final[:int(h * 0.6), :][region] = 255
                # Flood fill 从头顶扩展
                cv2.floodFill(hair_final, None, (w // 2, 2), 255)

            # 混合染色
            overlay = np.zeros_like(img)
            overlay[:] = bgr

            mask_3ch = cv2.merge([hair_final, hair_final, hair_final]) / 255.0
            result = (img * (1 - alpha * mask_3ch) + overlay * alpha * mask_3ch).astype(np.uint8)

            out = Path(path).parent / f"_{color}_hair.jpeg"
            cv2.imwrite(str(out), result)

            return {
                "success": True,
                "output": str(out),
                "hair_pixels": int(hair_final.sum() / 255),
                "color": color,
            }

        @router.get("/whiten")
        async def whiten_skin(
            path: str = Query(...),
            level: float = Query(1.3, description="美白强度 1.0~2.0"),
        ):
            img = cv2.imread(path)
            if img is None:
                return {"error": "图片不存在"}

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2].astype(np.float32) * level, 0, 255).astype(np.uint8)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.float32) * 0.85, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            out = Path(path).parent / f"_whitened.jpeg"
            cv2.imwrite(str(out), result)
            return {"success": True, "output": str(out), "level": level}

        @router.get("/filter")
        async def apply_filter(
            path: str = Query(...),
            name: str = Query("warm", description="warm/cool/vintage/bw/brighten"),
        ):
            img = cv2.imread(path)
            if img is None:
                return {"error": "图片不存在"}

            if name == "warm":
                result = cv2.addWeighted(img, 1,
                    np.full_like(img, [20, 50, 80], dtype=np.uint8), 0.3, 0)
            elif name == "cool":
                result = cv2.addWeighted(img, 1,
                    np.full_like(img, [80, 40, 10], dtype=np.uint8), 0.3, 0)
            elif name == "vintage":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
                result = cv2.addWeighted(result, 0.7,
                    np.full_like(result, [30, 60, 100], dtype=np.uint8), 0.3, 0)
            elif name == "bw":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            elif name == "brighten":
                result = cv2.convertScaleAbs(img, alpha=1.3, beta=20)
            else:
                return {"error": "未知滤镜", "filters": ["warm","cool","vintage","bw","brighten"]}

            out = Path(path).parent / f"_{name}.jpeg"
            cv2.imwrite(str(out), result)
            return {"success": True, "output": str(out), "filter": name}

        app.include_router(router)

    @classmethod
    def edit_hair(cls, path: str, color: str, alpha: float = 0.5):
        """程序化调用：换发色"""
        import requests
        try:
            r = requests.get(
                f"http://localhost:3001/api/skills/photo/hair",
                params={"path": path, "color": color, "alpha": alpha},
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}
