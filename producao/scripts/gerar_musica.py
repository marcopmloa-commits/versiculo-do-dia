"""Vídeo no formato "música": fundo de clipes de paisagem + palavra cantada grande no centro (sem frase embaixo).

Uso: python3 producao/scripts/gerar_musica.py musicas/NNN-nome.json
O JSON tem: {"musica": "caminho.mp3", "referencia": "João 15:13", "buscas": ["sunset silhouette", ...],
             "legenda": "texto do post", "hashtags": [...]}
Saída: videos/NNN-nome.mp4 (+ .jpg, .txt, .json), igual aos outros vídeos.
Requer: PIXABAY_KEY no ambiente, faster-whisper, playwright, ffmpeg.
"""
import json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
W, H, FPS = 1080, 1920, 30
CENA = 5.5          # segundos por clipe de fundo
CACHE = os.path.join(RAIZ, "producao", "cache_clipes")


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


# ---------- 1. letra com o tempo de cada palavra ----------
def palavras(mp3, dica=""):
    from faster_whisper import WhisperModel
    raw = sh("ffmpeg", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "f32le", "-", capture_output=True).stdout
    audio = np.frombuffer(raw, np.float32)
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, initial_prompt=dica or None)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words if w.word.strip()]


def frases(ws):
    """agrupa palavras em frases (quebra em pontuação ou pausa > 0,8 s)"""
    out, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        fim = re.search(r"[.,!?;:]$", w[2]) or (i + 1 < len(ws) and ws[i + 1][0] - w[1] > 0.8) or i + 1 == len(ws)
        if fim: out.append(cur); cur = []
    return out


# ---------- 2. clipes de fundo (Pixabay: uso comercial liberado, sem crédito obrigatório) ----------
def clipes(buscas, n, usados=()):
    os.makedirs(CACHE, exist_ok=True)
    chave = os.environ["PIXABAY_KEY"]; achados = []
    for q in buscas:
        url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": chave, "q": q, "per_page": 20, "safesearch": "true"})
        hits = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["hits"]
        for h in hits:
            if h["duration"] < CENA + 1 or h["id"] in usados or any(h["id"] == a[0] for a in achados): continue
            v = h["videos"].get("medium") or h["videos"]["large"]
            achados.append((h["id"], v["url"], q)); break
        if len(achados) >= n: break
    arquivos = []
    for vid, url, q in achados:
        f = os.path.join(CACHE, f"{vid}.mp4")
        if not os.path.exists(f):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # o CDN recusa pedidos sem User-Agent
            open(f, "wb").write(urllib.request.urlopen(req, timeout=120).read())
        arquivos.append((vid, f, q))
    return arquivos


# ---------- 3. camadas de texto (PNG transparentes desenhados no navegador) ----------
PAGINA = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: F; font-weight: 600; src: url("file://%(fontes)s/fraunces-latin-600.woff2"); }
@font-face { font-family: F; font-weight: 600; src: url("file://%(fontes)s/fraunces-latin-ext-600.woff2"); unicode-range: U+0100-024F; }
@font-face { font-family: F; font-weight: 500; src: url("file://%(fontes)s/fraunces-latin-500.woff2"); }
@font-face { font-family: F; font-weight: 500; src: url("file://%(fontes)s/fraunces-latin-ext-500.woff2"); unicode-range: U+0100-024F; }
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:F,serif;color:#fff}
#grande{position:absolute;left:60px;right:60px;top:780px;height:200px;display:flex;align-items:center;justify-content:center;
  font-weight:600;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap;
  text-shadow:0 0 30px rgba(255,236,200,.55),0 4px 18px rgba(0,0,0,.45)}
#marca{position:absolute;left:0;right:0;top:1000px;text-align:center;opacity:.85}
#marca svg{display:block;margin:0 auto 8px}
#marca div{font-size:22px;font-weight:500;letter-spacing:.3em;text-transform:uppercase;text-shadow:0 2px 8px rgba(0,0,0,.5)}
</style></head><body>
<div id="grande"><span id="g"></span></div>
<div id="marca"><svg width="46" height="70" viewBox="0 0 46 70"><g fill="#fff"><rect x="19" y="0" width="8" height="70" rx="2"/><rect x="0" y="18" width="46" height="8" rx="2"/></g></svg>
<div>Versículo Diário</div></div>
<script>
window.desenhar = async (c) => {
  await document.fonts.ready;
  const g = document.getElementById("g"); g.textContent = c.grande || "";
  let tam = c.tam || 150; g.style.fontSize = tam + "px";
  while (g.offsetWidth > 960 && tam > 40) { tam -= 4; g.style.fontSize = tam + "px"; }
  g.style.filter = c.entrada ? "blur(6px)" : "none";
  g.style.opacity = c.entrada ? .55 : 1;
  g.style.display = "inline-block";
  g.style.transform = c.entrada ? "scale(1.18)" : "none";
};
</script></body></html>"""


def camada_texto(estados, pasta):
    """estados = [(duração, {grande, frase, entrada}), ...] -> vídeo .mov com transparência"""
    pag = os.path.join(pasta, "texto.html")
    open(pag, "w", encoding="utf-8").write(PAGINA % {"fontes": os.path.join(RAIZ, "producao", "fontes")})
    js = os.path.join(pasta, "estados.json")
    json.dump([e for _, e in estados], open(js, "w", encoding="utf-8"), ensure_ascii=False)
    script = os.path.join(pasta, "render_texto.js")
    open(script, "w").write("""
const { chromium } = require("playwright"); const fs = require("fs");
(async () => { const [pag, js, out] = process.argv.slice(2); const est = JSON.parse(fs.readFileSync(js, "utf8"));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto("file://" + pag);
  for (let i = 0; i < est.length; i++) { await p.evaluate(c => window.desenhar(c), est[i]);
    await p.screenshot({ path: `${out}/t${String(i).padStart(4, "0")}.png`, omitBackground: true }); }
  await b.close(); })();""")
    sh("node", script, pag, js, pasta)
    lista = os.path.join(pasta, "texto.txt")
    with open(lista, "w") as f:
        for i, (dur, _) in enumerate(estados):
            f.write(f"file 't{i:04d}.png'\nduration {max(dur, 1 / FPS):.3f}\n")
        f.write(f"file 't{len(estados) - 1:04d}.png'\n")
    mov = os.path.join(pasta, "texto.mov")
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-r", str(FPS),
       "-c:v", "qtrle", "-pix_fmt", "argb", mov)
    return mov


def gerar(cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    nome = os.path.splitext(os.path.basename(cfg_path))[0]
    mp3 = os.path.join(RAIZ, cfg["musica"]) if not os.path.isabs(cfg["musica"]) else cfg["musica"]
    tmp = tempfile.mkdtemp(prefix="musica-")
    if cfg.get("trechos"):  # junta partes da música, ex.: [[0, 53.5], [134, 158]], com transição de 2 s
        ins, filt = [], []
        for i, (a, b) in enumerate(cfg["trechos"]):
            ins += ["-ss", str(a), "-to", str(b), "-i", mp3]
        cad = "[0:a]"
        for i in range(1, len(cfg["trechos"])):
            filt.append(f"{cad}[{i}:a]acrossfade=d=2:c1=tri:c2=tri[x{i}]"); cad = f"[x{i}]"
        cortada = os.path.join(tmp, "musica.wav")
        sh("ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", cad, cortada)
        mp3 = cortada
    dur = float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3, capture_output=True, text=True).stdout)
    ref = cfg["referencia"]

    ws = palavras(mp3, cfg.get("letra", ""))
    json.dump(ws, open(os.path.join(tmp, "palavras.json"), "w"), ensure_ascii=False)
    fr = frases(ws)
    frase_de = {}
    for k, f in enumerate(fr):
        for w in f: frase_de[w] = re.sub(r"[.,;:!?]+$", "", " ".join(x[2] for x in f))

    # estados do texto ao longo do tempo
    eventos = [(0.0, {"grande": ref, "tam": 120, "frase": ""})]
    for i, w in enumerate(ws):
        a, b, txt = w
        prox = ws[i + 1][0] if i + 1 < len(ws) else dur
        palavra = re.sub(r"[.,;:!?…\"“”]+", "", txt)
        eventos.append((a, {"grande": palavra, "frase": frase_de[w], "entrada": True}))
        eventos.append((min(a + 0.09, prox), {"grande": palavra, "frase": frase_de[w]}))
        if prox - b > 1.2:  # pausa longa: volta para a referência
            eventos.append((b + 0.4, {"grande": ref, "tam": 120, "frase": ""}))
    eventos.sort(key=lambda e: e[0])
    estados = [((eventos[i + 1][0] if i + 1 < len(eventos) else dur) - t, e) for i, (t, e) in enumerate(eventos)]
    estados = [(d, e) for d, e in estados if d > 0.001]
    mov = camada_texto(estados, tmp)

    # fundo: clipes de 5,5 s, recortados para 9:16, leve zoom, tom quente e escurecido para o texto
    n = int(np.ceil(dur / CENA))
    fontes = clipes(cfg["buscas"], n)
    if not fontes: raise SystemExit("nenhum clipe encontrado")
    partes = []
    for k in range(n):
        vid, f, q = fontes[k % len(fontes)]
        out = os.path.join(tmp, f"c{k:02d}.mp4")
        sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-t", f"{CENA:.2f}", "-i", f, "-an",
           "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"zoompan=z='1+0.0006*on':d=1:s={W}x{H}:fps={FPS},"
                  "eq=saturation=1.15:brightness=-0.06,colorbalance=rs=.05:bs=-.05,vignette=PI/4,format=yuv420p",
           "-r", str(FPS), out)
        partes.append(out)
    lista = os.path.join(tmp, "fundo.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    fundo = os.path.join(tmp, "fundo.mp4")
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", fundo)

    # junta tudo; áudio no padrão das redes (-14 LUFS)
    pasta_v = os.path.join(RAIZ, "videos"); os.makedirs(pasta_v, exist_ok=True)
    mp4 = os.path.join(pasta_v, nome + ".mp4")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", fundo, "-i", mov, "-i", mp3,
       "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];[2:a]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=%.2f:d=1.5[a]" % (dur - 1.5),
       "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}", "-c:v", "libx264", "-crf", "23", "-preset", "medium",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4)
    sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "3", "-i", mp4, "-frames:v", "1", "-vf", "scale=540:-1", "-q:v", "4", os.path.join(pasta_v, nome + ".jpg"))
    tags = cfg.get("hashtags") or ["#versiculododia", "#musicagospel", "#trapgospel", "#fe", "#biblia"]
    open(os.path.join(pasta_v, nome + ".txt"), "w", encoding="utf-8").write(cfg.get("legenda", "").strip() + "\n\n" + " ".join(tags[:5]) + "\n")
    json.dump({"duracao": round(dur, 1), "clipes": [f"pixabay:{v} ({q})" for v, _, q in fontes]}, open(os.path.join(pasta_v, nome + ".json"), "w"))
    print(f"ok: {mp4} ({dur:.1f}s, {len(ws)} palavras, {len(fontes)} clipes)")


if __name__ == "__main__":
    for c in sys.argv[1:]: gerar(c)
