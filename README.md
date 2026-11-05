# Versículo do Dia: vídeos

> Antes de produzir, leia `producao/REGRAS.md`.

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
- Voz: `pt-BR-AntonioNeural` em todos os vídeos. A Thalita (multilíngue) foi abandonada porque às vezes lia trechos em espanhol.
- Trilha: um fundo de acordes suaves sintetizado no próprio script (sem direitos autorais), bem baixo, abaixo da voz.
- Visual: `producao/scripts/card.html` (fonte Fraunces, licença OFL, em `producao/fontes/`).
- Sem data por enquanto.

## "Já postei"
No site, o botão "Já postei" cria a issue `postado: NNN-nome`. O workflow `.github/workflows/ja-postei.yml` então apaga `videos/NNN.mp4`/`.jpg`, anota o nome em `postados.txt` (assim o `gerar.py` não recria esse vídeo) e atualiza o `index.html`. Só issues abertas pelo dono do repositório disparam a remoção.
- **Automático:** em "⚙ Conectar ao GitHub", cole uma vez uma chave fine-grained com acesso **somente a este repositório** e permissão **Issues: Read and write**. A chave fica no **link favorito** (`…/#chave=github_pat_…`; o trecho depois do `#` nunca é enviado a servidor) e, se der, no `localStorage`. Assim funciona no modo anônimo: abra o site sempre pelo favorito.
- **Sem chave (padrão):** o botão só esconde o vídeo neste celular (`localStorage`), sem login. O arquivo continua no repositório até alguém limpar.

## Perfil
Nome: **Versículo Diário**. A foto de perfil é `perfil.png`, gerada a partir de `producao/arte/perfil.html`.
