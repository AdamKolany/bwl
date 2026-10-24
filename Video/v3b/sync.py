# Sync-Marke finden: letzter fast schwarzer Frame (100 fps) + 1 → Sekunden im Take
import sys, subprocess, numpy as np
W, H = 192, 90
p = subprocess.run(["ffmpeg", "-v", "error", "-t", "30", "-i", sys.argv[1], "-vf", f"fps=100,crop=1920:900:0:200,scale={W}:{H},format=gray",
                    "-f", "rawvideo", "-"], capture_output=True).stdout
f = np.frombuffer(p, np.uint8).reshape(-1, H, W).mean((1, 2))
dark = np.nonzero(f < 20)[0]; print(f"{(dark[-1] + 1) / 100:.2f}")
