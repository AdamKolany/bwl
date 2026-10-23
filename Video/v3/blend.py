# wie hybrid.py, aber GPT-Latent = Mischung aus Thorsten (Melodie) und Adam (Klangfarbe/Eigenart)
import os, sys, numpy as np, soundfile as sf
B, lines_f, outdir, ref, adam, alpha = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], float(sys.argv[6])
os.environ["COQUI_TOS_AGREED"] = "1"; os.environ["TTS_HOME"] = os.path.join(B, "modele")
import torch; torch.set_num_threads(8)
from TTS.api import TTS
m = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu").synthesizer.tts_model
lt, _ = m.get_conditioning_latents(audio_path=[ref], gpt_cond_len=30, max_ref_length=60)
la, emb = m.get_conditioning_latents(audio_path=[adam], gpt_cond_len=30, max_ref_length=60)
lat = alpha * lt + (1 - alpha) * la
os.makedirs(outdir, exist_ok=True)
NC = int(sys.argv[7]) if len(sys.argv) > 7 else 1
for i, z in enumerate([l.strip() for l in open(lines_f, encoding="utf-8") if l.strip()], 1):
    for c in range(NC):
        p = os.path.join(outdir, f"{i:02d}c{c}.wav")
        if os.path.exists(p): continue
        w = np.asarray(m.inference(z, "de", lat, emb, temperature=0.7, enable_text_splitting=False)["wav"], np.float32)
        sf.write(p, w, 24000); print(i, c, flush=True)
