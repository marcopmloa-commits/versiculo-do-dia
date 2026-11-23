"""Transcreve a música e encaixa as linhas da letra nos tempos das palavras.
Uso: python3 alinhar.py musicas/NNN-nome.mp3 linhas.json saida.json"""
import json, re, sys, difflib, os
sys.path.insert(0, os.path.dirname(__file__))
from gerar_musica import palavras
mp3, lj, out = sys.argv[1:4]
nome = os.path.splitext(os.path.basename(mp3))[0]
linhas = json.load(open(lj))[nome]
norm = lambda s: re.sub(r"[^a-záàâãéêíóôõúç ]", "", s.lower()).split()
ws = palavras(mp3, linhas[0])
W = [norm(w[2])[0] if norm(w[2]) else "" for w in ws]
res, i = [], 0
while i < len(ws):
    best = (0, None, 0)
    for L in linhas:
        n = len(norm(L))
        for k in range(max(1, n - 2), min(n + 3, len(ws) - i + 1)):
            r = difflib.SequenceMatcher(None, " ".join(W[i:i + k]), " ".join(norm(L))).ratio()
            if r > best[0]: best = (r, L, k)
    if best[0] >= 0.6:
        r, L, k = best; res.append([round(ws[i][0], 2), round(ws[i + k - 1][1], 2), L]); i += k
    else:
        print("sem letra:", round(ws[i][0], 1), ws[i][2]); i += 1
json.dump({"palavras": [[round(a, 2), round(b, 2), t] for a, b, t in ws], "linhas": res}, open(out, "w"), ensure_ascii=False, indent=0)
for a, b, t in res: print(f"{a:6.1f}{b:6.1f} {t}")
