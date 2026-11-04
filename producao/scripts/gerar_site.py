"""Monta o index.html (GitHub Pages): lista dos vídeos com download, legenda e botão "Já postei"."""
import html, json, os, glob, re
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
REPO = "marcopmloa-commits/versiculo-do-dia"
NOME = "Inabaláveis"

def gerar():
    itens = []
    for mp4 in sorted(glob.glob(os.path.join(RAIZ, "videos", "*.mp4"))):
        nome = os.path.splitext(os.path.basename(mp4))[0]
        ent = os.path.join(RAIZ, "entradas", nome + ".json")
        if not os.path.exists(ent): continue
        d = json.load(open(ent, encoding="utf-8"))
        leg = open(os.path.join(RAIZ, "videos", nome + ".txt"), encoding="utf-8").read().strip()
        meta = os.path.join(RAIZ, "videos", nome + ".json")
        s = int(json.load(open(meta))["duracao"]) if os.path.exists(meta) else 0
        num = int(re.match(r"\d+", nome).group()) if re.match(r"\d+", nome) else ""
        itens.append(f"""
<article id="{nome}"><div class="n">{num}</div><div class="c">
 <h2>{html.escape(d['referencia'])}</h2>
 <div class="meta">{s//60}:{s%60:02d}</div>
 <a class="btn dl" href="videos/{nome}.mp4" download="{nome}.mp4">⬇ Baixar vídeo</a>
 <pre>{html.escape(leg)}</pre>
 <button class="btn cp" onclick="cp(this)">📋 Copiar legenda</button>
 <button class="btn ok" onclick="postei('{nome}', this)">✔ Já postei</button>
</div></article>""")
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{NOME} — vídeos para postar</title>
<link rel="icon" href="perfil.png"><link rel="apple-touch-icon" href="perfil.png">
<style>
  @font-face {{ font-family: "Fraunces"; font-weight: 600; src: url("producao/fontes/fraunces-latin-600.woff2") format("woff2"); }}
  @font-face {{ font-family: "Fraunces"; font-weight: 600; src: url("producao/fontes/fraunces-latin-ext-600.woff2") format("woff2"); unicode-range: U+0100-024F; }}
  :root {{ --fundo:#fbf9f4; --papel:#f6efe0; --azul:#5a86c5; --borda:#d9e3f1; --texto:#3d5f91; --suave:#8a9ab3; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--fundo); color:var(--texto); font-family: system-ui, -apple-system, sans-serif; }}
  .w {{ max-width: 680px; margin: 0 auto; padding: 20px 16px 60px; }}
  header {{ display:flex; gap:14px; align-items:center; }}
  header img {{ width:64px; height:64px; border-radius:50%; }}
  h1, h2 {{ font-family:"Fraunces", Georgia, serif; font-weight:600; color:var(--azul); margin:0; }}
  h1 {{ font-size: 24px; }}
  .sub {{ color:var(--suave); font-size:14px; }}
  article {{ display:flex; gap:14px; background:#fff; border:1px solid var(--borda); border-radius:12px; padding:16px; margin-top:16px; }}
  .n {{ font-family:"Fraunces", Georgia, serif; font-size:30px; font-weight:600; color:var(--azul); min-width:34px; }}
  .c {{ flex:1; min-width:0; }}
  h2 {{ font-size: 20px; margin-bottom: 2px; }}
  .meta {{ color:var(--suave); font-size:13px; margin-bottom:8px; }}
  .btn {{ display:block; width:100%; text-align:center; padding:12px; border-radius:8px; font-size:16px; font-weight:600;
          border:0; margin:8px 0; cursor:pointer; text-decoration:none; font-family:inherit; }}
  .dl {{ background:var(--azul); color:#fff; }}
  .cp {{ background:var(--papel); color:var(--texto); }}
  .ok {{ background:#fff; color:var(--suave); border:1.5px solid var(--borda); }}
  pre {{ white-space:pre-wrap; background:var(--fundo); border-radius:8px; padding:10px; font-size:14px; font-family:inherit; margin:8px 0 0; }}
  .vazio {{ text-align:center; margin-top:40px; }}
</style>
</head>
<body><div class="w">
<header><img src="perfil.png" alt=""><div><h1>{NOME}</h1><div class="sub">Vídeos para postar · <span id="qtd">{len(itens)}</span> na fila</div></div></header>
{''.join(itens)}
<p class="sub vazio" id="vazio" {'' if not itens else 'hidden'}>Nenhum vídeo na fila. Tudo postado! 🙌</p>
<p class="sub" style="margin-top:24px">Se o download abrir o vídeo em vez de baixar: toque e segure no vídeo → Baixar/Salvar.<br>
"Já postei" tira o vídeo da lista e abre o GitHub para confirmar: toque em <b>Create</b> e o vídeo é apagado do site em ~1 minuto.</p>
</div>
<script>
const CHAVE = "postados";
function lista() {{ try {{ return JSON.parse(localStorage.getItem(CHAVE) || "[]"); }} catch (e) {{ return []; }} }}
function some(id) {{
  const a = document.getElementById(id); if (a) a.remove();
  const n = document.querySelectorAll("article").length;
  document.getElementById("qtd").textContent = n;
  document.getElementById("vazio").hidden = n > 0;
}}
lista().forEach(some);
function cp(b) {{
  const t = b.parentElement.querySelector("pre").innerText;
  const ok = () => {{ b.textContent = "✔ Copiada"; setTimeout(() => b.textContent = "📋 Copiar legenda", 1500); }};
  if (navigator.clipboard) navigator.clipboard.writeText(t).then(ok);
  else {{ const r = document.createRange(); r.selectNodeContents(b.parentElement.querySelector("pre"));
         getSelection().removeAllRanges(); getSelection().addRange(r); document.execCommand("copy"); ok(); }}
}}
function postei(id, b) {{
  if (!confirm("Marcar como postado? O vídeo será apagado do site.")) return;
  try {{ const l = lista(); l.push(id); localStorage.setItem(CHAVE, JSON.stringify(l)); }} catch (e) {{}}
  const url = "https://github.com/{REPO}/issues/new?title=" + encodeURIComponent("postado: " + id) +
              "&body=" + encodeURIComponent("Toque em Create para apagar este vídeo do site.");
  window.open(url, "_blank");
  some(id);
}}
</script>
</body>
</html>
"""
    open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(pagina)
    print("index.html com", len(itens), "vídeos")

if __name__ == "__main__": gerar()
