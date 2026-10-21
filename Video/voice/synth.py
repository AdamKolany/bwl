import os, sys, time, numpy as np
B = sys.argv[1]; V = sys.argv[2]
os.environ["COQUI_TOS_AGREED"] = "1"; os.environ["TTS_HOME"] = os.path.join(B, "modele")
import torch, soundfile as sf
torch.set_num_threads(8)
from TTS.api import TTS
m = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu").synthesizer.tts_model
lat, emb = m.get_conditioning_latents(audio_path=[os.path.join(B, "probki/pl.wav")], gpt_cond_len=30, max_ref_length=60)
lines = [l.strip() for l in open(os.path.join(V, "lines.txt"), encoding="utf-8") if l.strip()]
t0 = time.time()
for i, z in enumerate(lines, 1):
    p = os.path.join(V, f"{i:02d}.wav")
    if os.path.exists(p): continue
    w = np.asarray(m.inference(z, "de", lat, emb, enable_text_splitting=False)["wav"], dtype=np.float32)
    sf.write(p, w, 24000)
    print(f"{i}/{len(lines)} {len(w)/24000:.1f}s audio, elapsed {time.time()-t0:.0f}s", flush=True)
print("DONE", flush=True)
