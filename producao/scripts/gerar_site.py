"""Monta o index.html (GitHub Pages) com todos os vídeos de videos/, cada um com download e legenda do post."""
import html, json, os, glob, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))

def duracao(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True)
    s = int(float(r.stdout.strip() or 0)); return f"{s//60}:{s%60:02d}"

def gerar():
    itens = []
    for mp4 in sorted(glob.glob(os.path.join(RAIZ, "videos", "*.mp4")), reverse=True):
        nome = os.path.splitext(os.path.basename(mp4))[0]
        ent = os.path.join(RAIZ, "entradas", nome + ".json")
        if not os.path.exists(ent): continue
        d = json.load(open(ent, encoding="utf-8"))
        leg = open(os.path.join(RAIZ, "videos", nome + ".txt"), encoding="utf-8").read().strip()
        mb = os.path.getsize(mp4) / 1e6
        itens.append(f"""
  <article class="card">
    <video src="videos/{nome}.mp4" poster="videos/{nome}.jpg" controls preload="none" playsinline></video>
    <div class="info">
      <h2>{html.escape(d['referencia'])}</h2>
      <p class="meta">{duracao(mp4)} · {mb:.1f} MB</p>
      <a class="btn" href="videos/{nome}.mp4" download="{nome}.mp4">Baixar vídeo</a>
      <label>Legenda do post</label>
      <textarea readonly rows="6">{html.escape(leg)}</textarea>
      <button class="btn sec" onclick="copiar(this)">Copiar legenda</button>
    </div>
  </article>""")
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Versículo do Dia — vídeos</title>
<style>
  @font-face {{ font-family: "Fraunces"; font-weight: 600; src: url("producao/fontes/fraunces-latin-600.woff2") format("woff2"); }}
  @font-face {{ font-family: "Fraunces"; font-weight: 600; src: url("producao/fontes/fraunces-latin-ext-600.woff2") format("woff2"); unicode-range: U+0100-024F; }}
  :root {{ --fundo:#fbf9f4; --papel:#f6efe0; --azul:#5a86c5; --borda:#6f9bd6; --texto:#3d5f91; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--fundo); color:var(--texto); font-family: system-ui, -apple-system, sans-serif; }}
  header {{ max-width: 420px; margin: 32px auto 8px; padding: 0 16px; }}
  .arco {{ background:var(--papel); border:3px solid var(--borda); outline:1px solid var(--borda); outline-offset:-10px;
           border-radius: 210px 210px 6px 6px; padding: 90px 28px 32px; text-align:center; }}
  h1, h2 {{ font-family:"Fraunces", Georgia, serif; font-weight:600; color:var(--azul); margin:0; }}
  h1 {{ font-size: 34px; }}
  header p {{ margin:10px 0 0; font-size:15px; }}
  main {{ max-width: 1100px; margin: 24px auto 60px; padding: 0 16px; display:grid; gap:20px;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
  .card {{ background:#fff; border:1px solid #e3e9f3; border-radius:14px; overflow:hidden; }}
  video {{ width:100%; aspect-ratio:9/16; background:var(--papel); display:block; }}
  .info {{ padding: 14px 16px 18px; display:flex; flex-direction:column; gap:8px; }}
  h2 {{ font-size: 22px; }}
  .meta {{ margin:0; font-size:13px; opacity:.7; }}
  label {{ font-size:13px; font-weight:600; margin-top:6px; }}
  textarea {{ width:100%; font: 14px/1.4 system-ui, sans-serif; color:var(--texto); border:1px solid #dbe3ef; border-radius:8px; padding:8px; resize:vertical; background:var(--fundo); }}
  .btn {{ display:block; text-align:center; text-decoration:none; background:var(--azul); color:#fff; border:0; border-radius:10px;
          padding:12px; font-size:15px; font-weight:600; cursor:pointer; }}
  .btn.sec {{ background:#fff; color:var(--azul); border:1.5px solid var(--azul); }}
  .vazio {{ text-align:center; grid-column: 1/-1; opacity:.7; }}
</style>
</head>
<body>
<header><div class="arco"><h1>Versículo do Dia</h1><p>Vídeos prontos para baixar e postar, com a legenda do post.</p></div></header>
<main>{''.join(itens) or '<p class="vazio">Nenhum vídeo ainda.</p>'}
</main>
<script>
function copiar(b) {{
  const t = b.parentElement.querySelector("textarea");
  const ok = () => {{ b.textContent = "Copiada!"; setTimeout(() => b.textContent = "Copiar legenda", 1500); }};
  if (navigator.clipboard) navigator.clipboard.writeText(t.value).then(ok, () => {{ t.select(); document.execCommand("copy"); ok(); }});
  else {{ t.select(); document.execCommand("copy"); ok(); }}
}}
</script>
</body>
</html>
"""
    open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(pagina)
    print("index.html com", len(itens), "vídeos")

if __name__ == "__main__": gerar()
