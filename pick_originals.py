# -*- coding: utf-8 -*-
"""選定した候補タグの original(フル解像度) を取得して 手動画像/選定/ に配置。"""
import os, sys, json, urllib.request

# scene番号 -> 採用する候補タグ
PICKS = {
    1: "s1_3", 2: "s2_1", 3: "s3_1", 4: "s4_1",
    5: "s5_1", 6: "s6_2", 7: "s7_2", 8: "s8_1",
}

CAND = os.path.join("手動画像", "pexels_candidates")
OUT = os.path.join("手動画像", "選定")
os.makedirs(OUT, exist_ok=True)
man = json.load(open(os.path.join(CAND, "candidates.json"), encoding="utf-8"))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"

for scene, tag in PICKS.items():
    info = man[tag]
    url = info["original"]
    ext = ".jpg"
    dst = os.path.join(OUT, f"{scene:02d}{ext}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    with open(dst, "wb") as f:
        f.write(data)
    print(f"{scene:02d}  <- {tag}  {info['orig_w']}x{info['orig_h']}  {len(data)//1024}KB  ({info['photographer']})")
print("done")
