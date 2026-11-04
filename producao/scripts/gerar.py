"""Gera o vídeo vertical (TikTok) de um versículo + reflexão.

Uso: python3 producao/scripts/gerar.py entradas/001-efesios-6-13.json [--forcar]
Saída: videos/<nome>.mp4, videos/<nome>.jpg (capa) e videos/<nome>.txt (legenda do post).
"""
import asyncio, json, os, re, subprocess, sys, tempfile, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
VOZES = {"antonio": "pt-BR-AntonioNeural:-6%:-2Hz", "thalita": "pt-BR-ThalitaMultilingualNeural:-6%:+0Hz"}  # nome:velocidade:tom
VOZ = os.environ.get("VOZ", VOZES["antonio"])
SR = 24000
TRANSICAO = 0.6          # segundos do esmaecimento entre quadros
HASHTAGS_PADRAO = ["#versiculododia", "#biblia", "#palavradedeus", "#fe", "#deus"]

# ---------- texto ----------
ORDINAIS_M = {"Reis", "Samuel", "Crônicas", "Cronicas"}
def ref_falada(ref):
    """'Efésios 6:13' -> 'Efésios, capítulo 6, versículo 13'; '1 Coríntios 13:4-7' -> 'Primeira Coríntios, ... versículos 4 a 7'."""
    m = re.match(r"^\s*([123])?\s*([^\d]+?)\s+(\d+)(?::([\d\-–, ]+))?\s*$", ref)
    if not m: return ref
    n, livro, cap, vers = m.groups()
    if n:
        livro = (["Primeiro", "Segundo", "Terceiro"] if livro in ORDINAIS_M else ["Primeira", "Segunda", "Terceira"])[int(n) - 1] + " " + livro
    s = f"{livro}, capítulo {cap}"
    if vers:
        v = vers.replace("–", "-").strip()
        if "-" in v: a, b = v.split("-", 1); s += f", versículos {a.strip()} a {b.strip()}"
        elif "," in v: s += ", versículos " + " e ".join(x.strip() for x in v.split(","))
        else: s += f", versículo {v}"
    return s + "."

def falada(t):
    """Ajustes só para a narração (o texto na tela fica igual ao do app)."""
    return re.sub(r"\bd'?(Ele|Ela)\b", lambda m: "d" + m.group(1).lower(), t)

def frases(t):
    return [f.strip() for f in re.split(r"(?<=[.!?…])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ“\"«—-])", t.strip()) if f.strip()]

def trechos(paragrafos, max_palavras=26):
    """Divide a reflexão em quadros de até ~max_palavras (sem quebrar frase, exceto frases enormes)."""
    out = []
    for p in paragrafos:
        atual = []
        for f in frases(p):
            partes = [f]
            if len(f.split()) > max_palavras + 6:   # frase muito longa: quebra em vírgulas/ponto e vírgula
                partes, buf = [], ""
                for pedaco in re.split(r"(?<=[,;:])\s+", f):
                    if buf and len((buf + " " + pedaco).split()) > max_palavras: partes.append(buf); buf = pedaco
                    else: buf = (buf + " " + pedaco).strip()
                if buf: partes.append(buf)
            for x in partes:
                if atual and len(" ".join(atual + [x]).split()) > max_palavras: out.append(" ".join(atual)); atual = []
                atual.append(x)
        if atual: out.append(" ".join(atual))
    return out

# ---------- voz ----------
def tts(textos, wav, voz=None):
    """Narra os trechos num fluxo só. Devolve (duração, [início de cada trecho em s])."""
    import edge_tts
    nome, rate, pitch = (voz or VOZ).split(":")
    texto = falada(" ".join(textos))
    mp3 = wav[:-4] + ".mp3"; marcas = []
    async def run():
        c = edge_tts.Communicate(texto, nome, rate=rate, pitch=pitch, boundary="WordBoundary",
                                 proxy=os.environ.get("HTTPS_PROXY"))
        with open(mp3, "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio": f.write(ch["data"])
                elif ch["type"] == "WordBoundary": marcas.append((ch["offset"] / 1e7, ch["text"]))
    for t in range(3):
        try: marcas.clear(); asyncio.run(run()); break
        except Exception:
            if t == 2: raise
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav], check=True)
    with wave.open(wav) as w: total = w.getnframes() / w.getframerate()
    norm = lambda s: re.sub(r"[^\w]", "", s.lower())
    inicios, k = [], 0
    for t in textos:
        palavras = [norm(p) for p in t.split() if norm(p)]
        alvo = palavras[0] if palavras else ""
        achou = next((j for j in range(k, min(k + 12, len(marcas))) if norm(marcas[j][1]) == alvo), None)
        if achou is None: achou = min(k, len(marcas) - 1)
        inicios.append(marcas[achou][0] if marcas else 0.0)
        k = achou + max(len(palavras) - 2, 1)
    inicios[0] = 0.0
    for i in range(1, len(inicios)): inicios[i] = min(max(inicios[i], inicios[i - 1] + 0.5), total)
    return total, inicios

def ler(wav):
    with wave.open(wav) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

# ---------- trilha: tapete de acordes suave, sintetizado (sem direitos autorais) ----------
def trilha(dur, semente=0):
    hz = lambda n: 440 * 2 ** ((n - 69) / 12)
    # Ré maior: I – V – vi – IV (D, A, Bm, G), vozes em região média-grave
    acordes = [[50, 57, 62, 66], [45, 57, 61, 64], [47, 54, 62, 66], [43, 55, 59, 62]]
    rot = semente % 4; acordes = acordes[rot:] + acordes[:rot]
    passo = 7.0
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    rng = np.random.default_rng(semente)
    i = 0
    while i * passo < dur + passo:
        ini = i * passo - 1.5
        env = np.clip((t - ini) / 2.5, 0, 1) * np.clip((ini + passo + 3.0 - t) / 2.5, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        msk = env > 0
        for n in acordes[i % 4]:
            f = hz(n)
            for det in (-0.12, 0.12):
                ph = rng.uniform(0, 2 * np.pi)
                tt = t[msk]
                out[msk] += env[msk] * (np.sin(2 * np.pi * (f + det) * tt + ph) + 0.18 * np.sin(4 * np.pi * (f + det) * tt + ph))
        i += 1
    out *= 1 + 0.08 * np.sin(2 * np.pi * 0.11 * t)        # respiração lenta
    out /= np.max(np.abs(out)) + 1e-9
    fade = np.clip(t / 2.0, 0, 1) * np.clip((dur - t) / 2.5, 0, 1)
    return out * fade

# ---------- montagem ----------
def gerar(entrada, forcar=False):
    d = json.load(open(entrada, encoding="utf-8"))
    nome = os.path.splitext(os.path.basename(entrada))[0]
    pasta_v = os.path.join(RAIZ, "videos"); os.makedirs(pasta_v, exist_ok=True)
    mp4 = os.path.join(pasta_v, nome + ".mp4")
    legenda = os.path.join(pasta_v, nome + ".txt")
    tags = d.get("hashtags") or HASHTAGS_PADRAO
    open(legenda, "w", encoding="utf-8").write(f"“{d['versiculo'].strip()}”\n— {d['referencia']}\n\n" + " ".join(tags[:5]) + "\n")
    if os.path.exists(mp4) and not forcar:
        print("já existe:", mp4); return mp4
    tmp = tempfile.mkdtemp(prefix="vdd-")
    ref = d["referencia"]

    # quadros do versículo (um só, ou vários se for muito longo)
    v_trechos = trechos([d["versiculo"]], max_palavras=48)
    ref_txt = ref_falada(ref)
    # reflexão
    r_trechos = trechos(d["reflexao"] if isinstance(d["reflexao"], list) else [d["reflexao"]])

    # voz: campo "voz" da entrada (antonio/thalita); se faltar, alterna pelo número do arquivo
    num = int(re.match(r"\d+", nome).group()) if re.match(r"\d+", nome) else 1
    voz = VOZES.get(d.get("voz") or ("antonio" if num % 2 else "thalita"), VOZ)
    dv, iv = tts(v_trechos + [ref_txt], os.path.join(tmp, "v.wav"), voz)
    dr, ir = tts(r_trechos, os.path.join(tmp, "r.wav"), voz)

    INICIO, PAUSA, FIM = 0.5, 1.4, 3.2
    quadros, tempos = [], []
    for k, tx in enumerate(v_trechos):
        quadros.append({"texto": tx, "ref": ref, "rotulo": "", "tamanho": 96 if len(tx.split()) > 12 else 130})
        tempos.append(0.0 if k == 0 else INICIO + iv[k] - 0.25)
    off_r = INICIO + dv + PAUSA
    for k, tx in enumerate(r_trechos):
        quadros.append({"texto": tx, "ref": ref, "rotulo": "reflexão", "tamanho": 76})
        tempos.append(off_r + ir[k] - 0.35)
    fim_voz = off_r + dr
    quadros.append({"texto": d["versiculo"], "ref": ref, "rotulo": "", "tamanho": 96 if len(d["versiculo"].split()) > 12 else 130})
    tempos.append(fim_voz + 0.5)
    total = fim_voz + FIM

    # áudio: voz + trilha bem baixa
    voz = np.zeros(int(total * SR) + SR, np.float32)
    a = ler(os.path.join(tmp, "v.wav")); s = int(INICIO * SR); voz[s:s + len(a)] += a
    a = ler(os.path.join(tmp, "r.wav")); s = int(off_r * SR); voz[s:s + len(a)] += a
    voz = voz[:int(total * SR)]
    musica = trilha(total, semente=sum(map(ord, nome)))
    mix = voz * 0.92 + musica * float(d.get("volume_musica", 0.085))
    mix = np.clip(mix, -1, 1)
    wav = os.path.join(tmp, "mix.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # quadros -> PNG
    jq = os.path.join(tmp, "quadros.json"); json.dump(quadros, open(jq, "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.run(["node", os.path.join(AQUI, "render.js"), jq, tmp], check=True)

    # vídeo: quadros parados com esmaecimento entre eles
    n = len(quadros)
    dur = [(tempos[i + 1] if i + 1 < n else total) - tempos[i] for i in range(n)]
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for i in range(n):
        L = dur[i] + (TRANSICAO if i + 1 < n else 0)
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{L:.3f}", "-i", os.path.join(tmp, f"q{i:02d}.png")]
    cmd += ["-i", wav]
    filtros, ult = [], "[0:v]"
    for i in range(1, n):
        filtros.append(f"{ult}[{i}:v]xfade=transition=fade:duration={TRANSICAO}:offset={tempos[i]:.3f}[x{i}]")
        ult = f"[x{i}]"
    filtros.append(f"{ult}format=yuv420p,fade=t=in:st=0:d=0.4[vout]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "[vout]", "-map", f"{n}:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-r", "30", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", mp4]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "q00.png"), "-vf", "scale=540:-1", "-q:v", "4",
                    os.path.join(pasta_v, nome + ".jpg")], check=True)
    print(f"ok: {mp4} ({total:.1f}s, {n} quadros)")
    return mp4

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for e in args: gerar(e, forcar="--forcar" in sys.argv)
