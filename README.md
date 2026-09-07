# IBGE

Ferramenta para coleta de dados públicos do IBGE.

> **Nota:** sem API SIDRA (https://sidra.ibge.gov.br). A coleta é feita por scraping direto do site do IBGE, como faria um visitante humano, uma prova de conceito.

## Artefatos

- `fontes/*.html.md`, captura bruta de uma página do IBGE (ex.: estimativas de população), em Markdown com cabeçalho `url`/`acessado_em`.
- `fontes/*.json` / `fontes/*.csv`, versões estruturadas, extraídas manualmente do `.html.md`, listando pastas e arquivos disponíveis para download.
- `datasets/`, destino dos arquivos baixados do IBGE, espelhando a árvore de pastas do site; cada arquivo vem com um `.sha256` ao lado.

Este repositório usa [Git LFS](https://git-lfs.com) para todo o conteúdo de `datasets/` (`datasets/**` no `.gitattributes`), exceto os `.sha256`, que ficam como blobs normais do Git. Instale o Git LFS (`git lfs install`) antes de clonar ou baixar novos arquivos.

## Configuração

Crie o `.venv` após clonar o repositório:

```shell
uv venv
source .venv/bin/activate
uv sync
```

- `uv venv`, cria o `.venv` com a versão de Python do `pyproject.toml` (`>=3.14`).
- `source .venv/bin/activate`, ativa o ambiente na sessão do shell.
- `uv sync`, instala/atualiza dependências conforme `pyproject.toml`/`uv.lock`.

## Atualizar `fontes/estimativas-de-populacao.html.md`

O arquivo guarda o HTML **renderizado** pelo navegador, não o código-fonte (`view-source:`), porque a árvore de pastas é montada em JavaScript:

1. Abra a URL do cabeçalho `url` do arquivo (https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html?=&t=downloads) no Chrome e aguarde a árvore `Downloads` carregar.
2. Abra as Ferramentas do desenvolvedor (`⌥⌘I` no macOS, `F12`/`Ctrl+Shift+I` no Windows/Linux), aba **Elements**.
3. No elemento `<html>`, clique com o botão direito -> **Copy** -> **Copy outerHTML**.
4. Cole o HTML em um bloco \`\`\`html em `fontes/estimativas-de-populacao.html.md`, atualizando `acessado_em` (formato `AAAA-MM-DD`).
5. Exporte novamente `fontes/estimativas-de-populacao.json` e `.csv` (seção seguinte), eles não se atualizam sozinhos.

## Atualizar arquivos em fontes/

`fontes/*.json` e `.csv` são derivados do `.html.md` e não se atualizam sozinhos, após recapturar o `.html.md`, refaça a exportação:

```shell
python extrair_fontes.py fontes/estimativas-de-populacao.html.md --formato json > fontes/estimativas-de-populacao.json
python extrair_fontes.py fontes/estimativas-de-populacao.html.md --formato csv > fontes/estimativas-de-populacao.csv
```

## Baixar arquivos em datasets/

`download.py` lê `fontes/estimativas-de-populacao.csv` e baixa os arquivos para `datasets/`, gravando um `.sha256` ao lado de cada um:

```shell
python download.py
```

- Ordem: pastas mais recentes primeiro, arquivos de cada pasta em sequência.
- Pula arquivos já baixados, tenta cada um até 3 vezes, para a execução se todas falharem.
- Flags: `--pausa` (padrão: 3s), `--destino`.
