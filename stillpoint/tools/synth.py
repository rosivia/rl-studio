# Renders every guidance line with Kokoro-82M (local, offline) into Opus clips + index.json
import sys, os, json, re, time, subprocess, tempfile, numpy as np, onnxruntime as ort, soundfile as sf
from kokoro_onnx import Kokoro
model, voices, texts_path, out, voice = sys.argv[1:6]
speed = float(sys.argv[6]) if len(sys.argv) > 6 else 0.85
only = int(sys.argv[7]) if len(sys.argv) > 7 else 0
SR = 24000
k = Kokoro(model, voices)
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(model, so)
V = np.load(voices)
def tts(text, v):
    toks = k.tokenizer.tokenize(k.tokenizer.phonemize(text, 'en-us'))[:508]
    st = V[v][len(toks)].astype(np.float32)
    a = sess.run(None, {'input_ids': np.array([[0, *toks, 0]], dtype=np.int64), 'style': st, 'speed': np.array([speed], dtype=np.float32)})[0][0]
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0]-600):nz[-1]+2400] if len(nz) else a
def render(text, v):
    parts = [p for p in re.split(r'\s*(?:\.\.\.|…+)\s*', text) if p.strip()]
    sil = lambda s: np.zeros(int(SR*s), dtype=np.float32)
    chunks = [sil(.25)]
    for i, p in enumerate(parts):
        p = p.strip()
        if not re.search(r'[.!?]$', p): p += '.' if i < len(parts)-1 or not p.endswith(',') else ''
        chunks.append(tts(p, v)); chunks.append(sil(1.3 if i < len(parts)-1 else .3))
    a = np.concatenate(chunks); a = a / max(1e-6, np.abs(a).max()) * 0.7
    return a
def encode(a, dst):
    with tempfile.NamedTemporaryFile(suffix='.wav') as f:
        sf.write(f.name, a, SR)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f.name,'-af','highpass=f=60,lowpass=f=11000','-c:a','libopus','-b:a','40k','-ac','1','-ar','48000',dst], check=True)
os.makedirs(out, exist_ok=True)
items = json.load(open(texts_path)); items = items[:only] if only else items
files = {}; t0 = time.time()
for i, it in enumerate(items):
    fn = f"{it['key']}.ogg"; encode(render(it['text'], voice), os.path.join(out, fn)); files[it['key']] = fn
    if i % 10 == 0: print(f"{i+1}/{len(items)} {time.time()-t0:.0f}s", flush=True)
samples = []
for sv, lab in [('am_michael','Michael'),('am_fenrir','Fenrir'),('am_onyx','Onyx'),('bm_george','George (UK)'),('bm_lewis','Lewis (UK)')]:
    fn = f"sample_{sv}.ogg"; encode(render("Close your eyes. Take a slow breath in... and let it go. There is nowhere else to be.", sv), os.path.join(out, fn)); samples.append({'id': sv, 'label': lab, 'file': fn})
label = dict((s['id'], s['label']) for s in samples).get(voice, voice)
json.dump({'voice': voice, 'label': label, 'engine': 'Kokoro-82M', 'speed': speed, 'files': files, 'samples': samples}, open(os.path.join(out, 'index.json'), 'w'))
print('done', len(files), 'clips', f"{time.time()-t0:.0f}s")
