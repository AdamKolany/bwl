# XTTS: Sprechmelodie/Akzent aus Thorsten (Piper), Klangfarbe (speaker embedding) aus Adams Probe
import os, sys, numpy as np, soundfile as sf
B, lines_f, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ["COQUI_TOS_AGREED"] = "1"; os.environ["TTS_HOME"] = os.path.join(B, "modele")
import torch; torch.set_num_threads(8)
from piper import PiperVoice
from TTS.api import TTS
lines = [l.strip() for l in open(lines_f, encoding="utf-8") if l.strip()]
ref = sys.argv[4]
if not os.path.exists(ref):
    pv = PiperVoice.load(os.path.join(B, "modele/piper/de_DE-thorsten-high.onnx")); zd = []
    for l in open(sys.argv[5], encoding="utf-8"):
        if l.strip():
            for ch in pv.synthesize(l.strip()): zd += [ch.audio_float_array, np.zeros(int(ch.sample_rate*0.3), np.float32)]
    sf.write(ref, np.concatenate(zd), ch.sample_rate)
m = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu").synthesizer.tts_model
lat, _ = m.get_conditioning_latents(audio_path=[ref], gpt_cond_len=30, max_ref_length=60)
_, emb = m.get_conditioning_latents(audio_path=[sys.argv[6]], gpt_cond_len=30, max_ref_length=60)
os.makedirs(outdir, exist_ok=True)
for i, z in enumerate(lines, 1):
    for c in range(int(sys.argv[7]) if len(sys.argv) > 7 else 1):
        p = os.path.join(outdir, f"{i:02d}c{c}.wav")
        if os.path.exists(p): continue
        w = np.asarray(m.inference(z, "de", lat, emb, temperature=0.7, enable_text_splitting=False)["wav"], np.float32)
        sf.write(p, w, 24000); print(i, c, f"{len(w)/24000:.1f}s", flush=True)
