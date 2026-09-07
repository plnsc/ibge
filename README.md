# IBGE

Ferramenta para coleta de dados públicos do IBGE.

> **Nota:** este projeto não usa a API SIDRA (https://sidra.ibge.gov.br). A coleta é feita por scraping direto do site do IBGE, reproduzindo a navegação de um visitante humano, como prova de conceito.

## Artefatos

- `fontes/*.html.md` — captura bruta de uma página do IBGE (ex.: a página de estimativas de população), guardada como Markdown com um pequeno cabeçalho indicando a `url` de origem e a data de acesso (`acessado_em`).
- `fontes/*.json` / `fontes/*.csv` — versões estruturadas, extraídas manualmente do `.html.md` correspondente, listando as pastas e arquivos disponíveis para download no site do IBGE.
- `datasets/` — pasta de destino dos arquivos baixados do IBGE, com a mesma estrutura de pastas do site de origem; cada arquivo baixado é acompanhado de um `.sha256` para conferência de integridade.

Este repositório usa [Git LFS](https://git-lfs.com) para versionar todo o conteúdo de `datasets/` (`datasets/**` no `.gitattributes`), exceto os arquivos `.sha256`, que são pequenos e ficam como blobs normais do Git. Instale o Git LFS (`git lfs install`) antes de clonar ou baixar novos arquivos, para que eles sejam versionados corretamente em vez de ir direto para o histórico do Git.

### Atualizar `fontes/estimativas-de-populacao.html.md`

Esse arquivo não é o código-fonte da página (`Ver código-fonte`/`view-source:`), e sim o HTML já renderizado pelo navegador (a página do IBGE monta a árvore de pastas via JavaScript). Para recapturar:

1. Abra a URL registrada no cabeçalho `url` do arquivo (https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?=&t=downloads) no Google Chrome e aguarde a árvore de pastas (`Downloads`) carregar por completo.
2. Abra as Ferramentas do desenvolvedor (`⌥⌘I` no macOS, `F12`/`Ctrl+Shift+I` no Windows/Linux) e vá até a aba **Elements**.
3. No elemento `<html>`, no topo da árvore, clique com o botão direito e escolha **Copy → Copy outerHTML** — isso copia o HTML dinâmico (com o DOM já atualizado pelo JavaScript), diferente do "ver código-fonte" do navegador.
4. Cole o HTML copiado dentro de um bloco de código \`\`\`html em `fontes/estimativas-de-populacao.html.md`, mantendo o cabeçalho no topo com a `url` de origem e a data de acesso atual em `acessado_em` (formato `AAAA-MM-DD`).
5. Regenere `fontes/estimativas-de-populacao.json` e `fontes/estimativas-de-populacao.csv` (veja a seção seguinte), já que eles não são atualizados automaticamente.

## Execução

```shell
source .venv/bin/activate
python main.py
python extrair_fontes.py --formato tree   # ou json, csv
```

Dependências gerenciadas com `uv` (veja `pyproject.toml`); use `uv sync` para instalar/atualizar o `.venv`.

## Atualizar os arquivos `json`/`csv` em `fontes/`

Os arquivos `fontes/*.json` e `fontes/*.csv` são derivados do `.html.md` correspondente e **não** são regenerados automaticamente — se o `.html.md` for recapturado, refaça a exportação manualmente:

```shell
source .venv/bin/activate
python extrair_fontes.py fontes/estimativas-de-populacao.html.md --formato json > fontes/estimativas-de-populacao.json
python extrair_fontes.py fontes/estimativas-de-populacao.html.md --formato csv > fontes/estimativas-de-populacao.csv
```

## Baixar árvore de arquivos

`download.py` lê `fontes/estimativas-de-populacao.csv` e baixa todos os arquivos, replicando a árvore de arquivos em `datasets/` (um `.sha256` é gravado ao lado de cada arquivo baixado):

```shell
source .venv/bin/activate
python download.py
```

Roda sequencialmente (um arquivo por vez, pastas mais recentes primeiro), pula arquivos já baixados, tenta cada download até 3 vezes e para a execução se todas as tentativas falharem. Ajuste as pausas com `--pausa-pastas` e `--pausa-arquivos`, e o destino com `--destino`.

## Contar extensões de arquivo

`listar_extensoes.py` lê `fontes/estimativas-de-populacao.csv` e imprime no stdout a contagem de cada extensão de arquivo (`.pdf`, `.zip`, etc.), da mais para a menos frequente:

```shell
source .venv/bin/activate
python listar_extensoes.py
```
