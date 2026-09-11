# -*- coding: utf-8 -*-
"""自前で最終合成（ツールのvideo段は使わない＝高画質1発エンコード）。
 clips(c01..c08) + audio.mp3 + subtitle.srt + BGM  ->  出力/v3
"""
import os, sys, glob, shutil, subprocess

TASK = sys.argv[1] if len(sys.argv) > 1 else None
if not TASK:
    tasks = sorted(glob.glob("storage/tasks/*/subtitle.srt"), key=os.path.getmtime)
    TASK = os.path.dirname(tasks[-1])
print("task:", TASK)

CLIPS = [f"storage/local_videos/c{n:02d}.mp4" for n in range(1, 9)]
AUDIO = os.path.join(TASK, "audio.mp3")
SRT   = os.path.join(TASK, "subtitle.srt")
BGM   = "resource/songs/output003.mp3"
OUTDIR = "出力"
OUT = os.path.join(OUTDIR, "ルートB_犬が子供を助けた3選_v3.mp4")
os.makedirs(OUTDIR, exist_ok=True)

# ASCIIパスの作業場（ffmpeg subtitles フィルタは日本語パス/コロンに弱い）
WD = os.path.join(os.environ.get("TEMP", "."), "mp_assemble")
if os.path.isdir(WD):
    shutil.rmtree(WD)
os.makedirs(WD)
shutil.copy(AUDIO, os.path.join(WD, "narr.mp3"))
shutil.copy(SRT,   os.path.join(WD, "sub.srt"))
shutil.copy(r"C:\Windows\Fonts\meiryob.ttc", os.path.join(WD, "font.ttc"))
with open(os.path.join(WD, "list.txt"), "w", encoding="utf-8") as f:
    for c in CLIPS:
        f.write(f"file '{os.path.abspath(c)}'\n")

# 1) クリップ連結（無劣化 copy）
cat = os.path.join(WD, "video.mp4")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", os.path.join(WD, "list.txt"), "-c", "copy", cat],
               check=True, capture_output=True, text=True)

# 2) 字幕焼き込み + 音声(ナレ+BGM)ミックス + 1発高画質エンコード
style = ("FontName=Meiryo,Bold=1,FontSize=10,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&H00000000,BorderStyle=1,Outline=2.5,Shadow=0,"
         "Alignment=2,MarginV=170,MarginL=60,MarginR=60")
vf = f"subtitles=sub.srt:fontsdir=.:force_style='{style}'"
af = ("[1:a]volume=1.0[nar];"
      "[2:a]volume=0.14,afade=t=in:st=0:d=1.5,afade=t=out:st=45.3:d=2[bg];"
      "[nar][bg]amix=inputs=2:duration=first:dropout_transition=0,dynaudnorm=f=250:g=7[a]")

cmd = [
    "ffmpeg", "-y",
    "-i", "video.mp4",
    "-i", "narr.mp3",
    "-stream_loop", "-1", "-i", "resource_bgm.mp3",
    "-filter_complex", af,
    "-vf", vf,
    "-map", "0:v", "-map", "[a]",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    os.path.abspath(OUT),
]
shutil.copy(BGM, os.path.join(WD, "resource_bgm.mp3"))
r = subprocess.run(cmd, cwd=WD, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-3000:]); raise SystemExit("ffmpeg assemble failed")
print("OK ->", OUT)
