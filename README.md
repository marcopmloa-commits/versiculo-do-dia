# Versículo do Dia: vídeos

Gera vídeos verticais (1080x1920, formato TikTok). Cada vídeo traz o versículo e a reflexão narrados, no estilo do cartão em arco: creme e azul claro, simples e sem imagens. Os vídeos ficam no site (GitHub Pages, `index.html`) com botão de download e a legenda do post.

## Como adicionar um vídeo

1. Crie `entradas/NNN-livro-cap-vers.json` (o número define a ordem):
   ```json
   {"referencia": "Efésios 6:13",
    "versiculo": "Portanto, tomai toda a armadura de Deus, ...",
    "reflexao": ["1º parágrafo da reflexão.", "2º parágrafo."],
    "hashtags": ["#versiculododia", "#biblia", "#palavradedeus", "#fe", "#deus"]}
   ```
   `hashtags` é opcional (máximo de 5). `volume_musica` é opcional (padrão 0.085).
   O texto deve vir exatamente como está no app.
2. Gere os vídeos e o site:
   ```bash
   pip install -q edge-tts numpy
   python3 producao/scripts/gerar.py entradas/*.json    # pula os que já existem (--forcar para refazer)
   python3 producao/scripts/gerar_site.py
   ```
3. Faça o commit e o push. Saídas: `videos/NNN.mp4`, `videos/NNN.jpg` (capa) e `videos/NNN.txt` (legenda: versículo + referência + hashtags).

## Detalhes
- Voz: alterna por vídeo. Os números ímpares usam Antonio (`pt-BR-AntonioNeural`) e os pares usam Thalita (`pt-BR-ThalitaMultilingualNeural`). Para forçar uma das duas, coloque `"voz": "antonio"` ou `"voz": "thalita"` na entrada.
- Trilha: um fundo de acordes suaves sintetizado no próprio script (sem direitos autorais), bem baixo, abaixo da voz.
- Visual: `producao/scripts/card.html` (fonte Fraunces, licença OFL, em `producao/fontes/`).
- Sem data por enquanto.
