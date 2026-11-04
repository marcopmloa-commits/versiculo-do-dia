// Uso: node render.js quadros.json pasta_saida
// quadros.json = [{texto, ref, rotulo, tamanho?}, ...] -> pasta_saida/q00.png, q01.png ...
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
(async () => {
  const [arq, saida] = process.argv.slice(2);
  const quadros = JSON.parse(fs.readFileSync(arq, "utf8"));
  fs.mkdirSync(saida, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto("file://" + path.join(__dirname, "card.html"));
  for (let i = 0; i < quadros.length; i++) {
    await p.evaluate((c) => window.desenhar(c), quadros[i]);
    await p.screenshot({ path: path.join(saida, `q${String(i).padStart(2, "0")}.png`) });
  }
  await b.close();
})();
