#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def remove_background_rembg(image_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    from rembg import remove

    ok, encoded = cv2.imencode(".png", image_bgr)
    if not ok:
        raise RuntimeError("Failed to encode source image for rembg")
    result = remove(encoded.tobytes())
    rgba = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_UNCHANGED)
    if rgba is None:
        raise RuntimeError("Failed to decode rembg output")

    if rgba.ndim == 3 and rgba.shape[2] == 4:
        alpha = rgba[:, :, 3]
        rgb = rgba[:, :, :3]
        return rgb, alpha

    mask = np.where(cv2.cvtColor(rgba, cv2.COLOR_BGR2GRAY) < 245, 255, 0).astype(np.uint8)
    return rgba, mask


def remove_background_grabcut(image_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h, w = image_bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (int(w * 0.05), int(h * 0.03), int(w * 0.90), int(h * 0.94))
    cv2.grabCut(image_bgr, mask, rect, bgd_model, fgd_model, 8, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.medianBlur(fg, 5)
    return image_bgr, fg


def crop_subject(image_bgr: np.ndarray, alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ys, xs = np.where(alpha > 20)
    if len(xs) == 0 or len(ys) == 0:
        return image_bgr, alpha

    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    margin_x = int((x1 - x0 + 1) * 0.10)
    margin_y = int((y1 - y0 + 1) * 0.12)
    x0 = max(0, x0 - margin_x)
    x1 = min(image_bgr.shape[1] - 1, x1 + margin_x)
    y0 = max(0, y0 - margin_y)
    y1 = min(image_bgr.shape[0] - 1, y1 + margin_y)
    return image_bgr[y0 : y1 + 1, x0 : x1 + 1], alpha[y0 : y1 + 1, x0 : x1 + 1]


def preprocess(image_path: Path, output_path: Path) -> str:
    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    used = "rembg"
    try:
        subject_bgr, alpha = remove_background_rembg(image_bgr)
    except Exception:
        used = "grabcut"
        subject_bgr, alpha = remove_background_grabcut(image_bgr)

    subject_bgr, alpha = crop_subject(subject_bgr, alpha)

    white_bg = np.full_like(subject_bgr, 255, dtype=np.uint8)
    alpha_f = (alpha.astype(np.float32) / 255.0)[:, :, None]
    composited = (subject_bgr.astype(np.float32) * alpha_f + white_bg.astype(np.float32) * (1.0 - alpha_f)).astype(
        np.uint8
    )

    gray = cv2.cvtColor(composited, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8)).apply(gray)
    lifted = cv2.convertScaleAbs(clahe, alpha=1.20, beta=24)
    blended = cv2.addWeighted(lifted, 0.85, np.full_like(lifted, 255), 0.15, 0)

    cv2.imwrite(str(output_path), blended)
    return used


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare profile photo for ASCII conversion.")
    parser.add_argument("image", help="Path to source photo (example: source-photo.jpg)")
    parser.add_argument("--output", default="source-prepped.png", help="Output grayscale PNG path")
    args = parser.parse_args()

    used = preprocess(Path(args.image), Path(args.output))
    print(f"Wrote {args.output} (background removal: {used})")


if __name__ == "__main__":
    main()
