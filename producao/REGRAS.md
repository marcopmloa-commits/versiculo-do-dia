# Regras de produção (leia antes de criar vídeos)

Aprendidas na revisão de 05/11/2026 do lote 015–024 (nota média ~7,4, veredito "postar com ajustes").

## Versículos
- **Fonte:** prints do app "Versículo do Dia" → copiar o texto **exatamente** como está.
  Quando o app não tem mais versículos: `https://bible-api.com/<livro>+<cap>:<v>?translation=almeida`.
  Essa "almeida" é a **Almeida Revisada (IBB)**, em domínio público. Não é a ARC/ACF; diga isso se perguntarem.
  NVI/NAA/NTLH/ARA têm direitos autorais: não use como fonte. Isso vale também para o texto de adesivos e imagens (ex.: o Ef 6:13 "permanecer inabaláveis" é ARA).
- **Ao citar outro versículo na reflexão, use a MESMA tradução (API) e a mesma pessoa verbal.** Erro anterior: Sl 46:2 citado como "não temeria… se transtornasse" (ARA, singular), quando a API diz "não temeremos, ainda que a terra se mude".
- Listas (ex.: peças da armadura, Ef 6:14-17) devem estar completas.
- **Erros conhecidos da API:** às vezes começa com letra minúscula (Is 41:10) ou tem erro de digitação ("estai" → "estais", Mt 11:28). Revise sempre.
- **Evite versículos com linguagem arcaica difícil de entender em voz alta** ("Não to mandei eu?", Js 1:9). Se o versículo for muito conhecido e tiver uma palavra antiga, explique a palavra na reflexão (ex.: "estribar = apoiar-se").
- Tire as aspas do próprio versículo (a legenda do post já coloca as aspas).

## Reflexões escritas por nós (fonte externa)
- **Tamanho:** 90–130 palavras, em 1 a 3 parágrafos (igual ao app).
- **Pronomes divinos em maiúscula:** Ele, Sua, dEle, nEle.
- **A reflexão tem de usar as palavras do versículo mostrado.** Não cite expressões de outra tradução. Erro anterior: o versículo dizia "esforça-te e tem bom ânimo" e a reflexão falava em "ser forte e corajoso".
- **Não enxerte outro versículo sem dizer de onde vem.** Erro anterior: "a Sua força se aperfeiçoa na fraqueza" (2 Co 12:9) dentro da reflexão de Isaías. Se citar, diga: "como os versículos seguintes explicam" ou "como Paulo escreve em…".
- **Contexto histórico preciso:** Jeremias 29 foi enviado aos *exilados de Judá na Babilônia*, não a "Israel". Confira autor, destinatário e situação antes de afirmar.
- **Variedade dentro do lote:** os vícios do lote anterior foram estes:
  - o contraste "não é X, mas Y": no máximo 3 por lote de 10;
  - "Portanto, devemos…" como fechamento: no máximo 2 por lote;
  - "Que possamos…": no máximo 2 por lote;
  - fechamento "podemos + verbo": no máximo 3 por lote; "em oração": no máximo 2;
  - frases repetidas entre reflexões ("não estamos sozinhos", "em cada passo"): cada frase-feita no máximo 1 vez por lote.
  - Alterne as aberturas no estilo do app ("Este/Esse versículo nos lembra / ensina / convida / mostra / orienta…", "A reflexão desse versículo nos leva a…", "A reflexão para este versículo nos remete…") e não repita a mesma abertura em seguida.
- Prefira explicar algo concreto do versículo (o costume do pastor, a lâmpada de óleo, a palavra no original, o versículo seguinte) em vez de frases genéricas.
- Português: "seja bom" (subjuntivo) depois de "não significa que"; "seja… seja"/"tanto… quanto"; dois-pontos antes de uma explicação.

## Hashtags
- Máximo de 5: `#versiculododia #biblia #fe` + 2 do tema.
- **Leia a hashtag sem acento antes de usar.** `#forca` (força) vira "forca", de enforcamento → use `#forcaemcristo`. Cheque também `#graca`, `#paz` e outras.

## Vídeo
- **Cores:** três paletas (azul, verde claro, rosa claro) revezando pelo número do vídeo; campo `"tema"` na entrada fixa uma. Arabescos discretos (floreio no topo, divisor, volutas, raminhos) sempre com o filtro `leve`; o estilo continua minimalista.
- **Voz: só Antonio, com +10% de velocidade e tom -12 Hz (opção B, escolhida pelo dono).** A `pt-BR-ThalitaMultilingualNeural` às vezes lê trechos em espanhol. Se quiser voz feminina, use a `pt-BR-FranciscaNeural`, que só fala português (teste antes).
- **Nada de esmaecer a partir do preto no começo:** o TikTok usa o 1º quadro como capa, e ela ficava escura. O 1º quadro precisa ser o arco nítido com o versículo.
- Revisão: antes de publicar um lote escrito por nós, peça a um agente independente para revisar (texto bíblico, contexto, repetição, português, hashtags).

## Formato música (aprovado pelo dono em 11/11/2026, vídeos 027 e 028)
- Só a **palavra grande** que muda no ritmo do canto + cruz e "Versículo Diário"; **sem frase embaixo**.
- Fundo: clipes do Pixabay ligados ao tema da letra (ex.: águia em "asas"), tom quente; confira o mosaico e troque clipes fora do clima (cidade, objetos aleatórios).
- Áudio em -14 LUFS (o `gerar_musica.py` já faz).
- **Tamanho ideal: ~45 s a 1min15.** O Suno costuma esticar letras com refrão repetido (a de "Asas" deu 2min40): use `"trechos"` para juntar partes (ex.: 1º verso + refrão + final) com transição de 2 s, cortando no fim de uma frase.
- Letra: intro com a referência, verso em 1ª pessoa, refrão com o versículo, final curto; estilo "trap gospel, 86 bpm, emotional piano, soft 808, male vocals, light autotune, brazilian portuguese".
- Legenda: versículo (Almeida IBB) + chamada para comentar + "🎵 Título (feito com Suno)" enquanto for o plano grátis.
- Texto bíblico: se a bible-api.com estiver fora, use `raw.githubusercontent.com/thiagobodruk/biblia/master/json/aa.json` (mesma Almeida Revisada IBB).
- **Confira a letra na tela** (`letra_na_tela` em `videos/NNN.json`) e quadros do final: o reconhecimento pode "inventar" um trecho com frases da dica (029: mostrou "fidelidade" onde cantava "Cada manhã"). Corrija com `"correcoes"` (palavra errada → certa) e `"substituir"` ([início, fim, "texto"]; texto vazio apaga, ex.: "oh oh oh").
- O Suno **ignora `[End]`** e inventa estrofes; conte sempre com o corte por `"trechos"`. Comece direto na voz (pule a introdução instrumental).
- Clipes: evite pessoas em close de corpo/pernas e cenas noturnas com carros; prefira paisagem, silhueta, objeto (xícara, Bíblia, janela).
- **Temas:** a música não precisa ser de um versículo. Pode ser **oração de gratidão** a Deus (acordar, fôlego, família, livramento, paz), sempre no mesmo estilo: 1ª pessoa, íntima, trap gospel. Sem versículo, use como `"referencia"` uma frase curta (ex.: "Obrigado, Senhor"), que aparece no começo e nas pausas. Letras sempre originais: nada de copiar frases de outros perfis.
- **Clipes reais, nada de IA** (o TikTok estava rotulando como IA): o `gerar_musica.py` só aceita clipes do Pixabay com id ≤ 185000 (enviados até o fim de 2023) e recusa etiquetas de IA/3D/animação e temas impróprios (cigarro, bebida, armas, celular). O clipe 253345 (janela com Bíblia e moinho) era "ai generated": não use.
- A música do Suno também é IA. Se o TikTok rotular por causa do áudio, o rótulo está correto: não tente esconder (é regra do TikTok sinalizar conteúdo de IA).
- **O vídeo começa na voz:** o primeiro trecho de `"trechos"` começa ~0,25 s antes da 1ª palavra cantada (transcreva a música inteira primeiro para achar). Nada de introdução só instrumental: não prende no TikTok.
- **Ritmo do vídeo:** o clipe de fundo troca a cada compasso da música (o `gerar_musica.py` mede o andamento; se o compasso for < 2,2 s, usa 2 compassos). Dá ~20–25 clipes por vídeo: coloque **12 ou mais buscas** variadas (o gerador alterna 1º, 2º... resultado de cada busca). Pode forçar com `"cena": 3.0`.
- **Letras que prendem:** começar pelo **refrão/gancho** (frase que fala com quem assiste: "Se você tá vendo isso…", "Três da manhã…"), temas de identificação (mãe que orou, choro escondido, livramento), refrão repetido no fim.
