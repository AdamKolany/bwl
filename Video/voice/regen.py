import os, sys, numpy as np
B, V = sys.argv[1], sys.argv[2]; idx = [int(x) for x in sys.argv[3].split(",")]
os.environ["COQUI_TOS_AGREED"] = "1"; os.environ["TTS_HOME"] = os.path.join(B, "modele")
import torch, soundfile as sf
torch.set_num_threads(8)
from TTS.api import TTS
m = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu").synthesizer.tts_model
lat, emb = m.get_conditioning_latents(audio_path=[os.path.join(B, "probki/pl.wav")], gpt_cond_len=30, max_ref_length=60)
lines = [l.strip() for l in open(os.path.join(V, "lines.txt"), encoding="utf-8") if l.strip()]
for i in idx:
    z = lines[i-1]; exp = len(z) / 14.0  # ~14 chars/s
    for k in range(4):
        w = np.asarray(m.inference(z, "de", lat, emb, enable_text_splitting=False, temperature=0.6)["wav"], dtype=np.float32)
        d = len(w) / 24000
        sf.write(os.path.join(V, f"{i:02d}c{k}.wav"), w, 24000)
        print(f"{i} cand{k} {d:.1f}s (expected ~{exp:.1f}s)", flush=True)
print("DONE", flush=True)
