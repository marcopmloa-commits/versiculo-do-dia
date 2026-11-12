"""Folha de contato dos clipes de um vídeo (miniatura + id do Pixabay), para achar e vetar clipes ruins.
Uso: python3 producao/scripts/folha_clipes.py NNN-nome saida.png"""
import json, os, subprocess, sys, tempfile
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
nome, saida = sys.argv[1], sys.argv[2]
ids = [c.split()[0].split(":")[1] for c in json.load(open(os.path.join(RAIZ, "videos", nome + ".json")))["clipes"]]
tmp = tempfile.mkdtemp(); fs = []
for i, v in enumerate(ids):
    f = os.path.join(tmp, f"{i:02d}.png"); fs.append(f)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", os.path.join(RAIZ, "producao", "cache_clipes", v + ".mp4"), "-frames:v", "1",
                    "-vf", f"scale=110:140:force_original_aspect_ratio=increase,crop=110:140,drawtext=text='{v}':fontcolor=yellow:fontsize=16:x=3:y=3:box=1:boxcolor=black@0.6", f], check=True)
ins = sum([["-i", f] for f in fs], [])
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", f"hstack={len(fs)}", saida], check=True)
