#!/usr/bin/env python3
"""VFX plate: slow floating dust motes in the courtroom light (rendered once, screen-blended).

Usage: dust.py <out.mp4> [seconds]
Soft, out-of-focus particles drifting upward and sideways, a few in sharp focus, brighter in an
upper-left light shaft - the "dust in a projector beam" feel of old halls. Grey on black.
"""
import subprocess, sys
import numpy as np

OUT = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 10.5
W, H, FPS = 960, 540, 24  # rendered at half size, upscaled (motes are soft anyway)
rng = np.random.default_rng(11)
N = 260
x = rng.uniform(0, W, N); y = rng.uniform(0, H, N)
vx = rng.normal(0.15, 0.25, N); vy = rng.uniform(-0.45, -0.08, N)
size = np.where(rng.random(N) < 0.12, rng.uniform(2.5, 5.0, N), rng.uniform(0.8, 1.8, N))
bright = rng.uniform(0.25, 1.0, N)
phase = rng.uniform(0, 2 * np.pi, N)
yy, xx = np.mgrid[0:H, 0:W]
shaft = np.clip(1.15 - np.abs((xx - 0.35 * W) * 0.9 + (yy - 0.0) * 0.55) / (0.45 * W), 0.25, 1.0)

p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-vf", "scale=1920:1080:flags=bicubic,format=yuv420p",
                      "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", OUT], stdin=subprocess.PIPE)
for f in range(int(DUR * FPS)):
    t = f / FPS
    img = np.zeros((H, W), np.float32)
    px = (x + vx * f + 6 * np.sin(t * 0.7 + phase)) % W
    py = (y + vy * f) % H
    tw = 0.75 + 0.25 * np.sin(t * 2.0 + phase)
    for k in range(N):
        r = size[k]; R = int(r * 3) + 1
        cx, cy = int(px[k]), int(py[k])
        x0, x1 = max(0, cx - R), min(W, cx + R + 1); y0, y1 = max(0, cy - R), min(H, cy + R + 1)
        if x0 >= x1 or y0 >= y1: continue
        gx = xx[y0:y1, x0:x1] - px[k]; gy = yy[y0:y1, x0:x1] - py[k]
        img[y0:y1, x0:x1] += bright[k] * tw[k] * np.exp(-(gx * gx + gy * gy) / (2 * r * r))
    img = np.clip(img * shaft * 255, 0, 255).astype(np.uint8)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait()
print("dust plate:", OUT)
