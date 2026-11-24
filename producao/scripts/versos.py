"""Monta "versos" (2 linhas por tela) a partir de "substituir". Uso: python3 versos.py musicas/NNN.json [solo_idx ...]
solo_idx: índices de linhas de "substituir" que ficam sozinhas na tela (para acertar o pareamento por seção)."""
import json, sys
def meio(t):
    cs = [i for i, ch in enumerate(t) if ch == ","]
    i = min(cs, key=lambda i: abs(i - len(t) / 2)); return t[:i + 1].strip() + "\n" + t[i + 1:].strip()
f = sys.argv[1]; solo = {int(x) for x in sys.argv[2:]}
cfg = json.load(open(f)); L = cfg["substituir"]; V = []; i = 0
longa = lambda t: len(t) > 55 and "," in t
while i < len(L):
    a, b, t = L[i]
    if longa(t): V.append([a, b, meio(t)]); i += 1; continue
    if i not in solo and i + 1 < len(L) and i + 1 not in solo and not longa(L[i + 1][2]) and L[i + 1][0] - b < 2.0:
        V.append([a, L[i + 1][1], t + "\n" + L[i + 1][2]]); i += 2
    else: V.append([a, b, t]); i += 1
cfg["versos"] = V; json.dump(cfg, open(f, "w"), ensure_ascii=False, indent=1)
for a, b, t in V: print(f"{a:6.1f}{b:6.1f} {t.replace(chr(10), ' / ')}")
