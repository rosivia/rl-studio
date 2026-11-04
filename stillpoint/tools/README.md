# Studio voice pipeline

English guidance is pre-recorded with **Kokoro-82M** (Apache-2.0), an open neural TTS model, run locally. No API key and no cloud.
The app plays `audio/en/<key>.ogg` when a clip exists for a line, and falls back to the phone's voice otherwise.

## Re-record after editing scripts
1. `node tools/texts.js /tmp/texts.json`: exports every English line with its key (FNV-1a hash of the text).
2. Get the model: Kokoro-82M fp16 ONNX (`kokoro-fp16-shards` on npm: concatenate `part0..9`) and the voice `.bin` files (`kokoro-local-runtime` on npm, `voices/`).
3. `python tools/prep.py <voices_dir> voices.npz`
4. `python tools/synth.py kokoro-fp16.onnx voices.npz /tmp/texts.json audio/en am_michael 0.85`
   Arguments: model, voices, texts, output dir, voice id, speed. Needs `pip install kokoro-onnx soundfile` and ffmpeg.
5. `./build.sh` and commit. Bump `CACHE` in `sw.js` so phones fetch the new clips.

Voices: `am_michael` (default), `am_fenrir`, `am_onyx`, `bm_george`, `bm_lewis`.
