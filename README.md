# ibge

Ferramenta para coleta de dados públicos do IBGE.

## Execução

```
source .venv/bin/activate
python main.py
python gerar_fontes.py --formato tree   # ou json, csv
```

Dependências gerenciadas com `uv` (veja `pyproject.toml`); use `uv sync` para instalar/atualizar o `.venv`.

## Atualizar os arquivos `json`/`csv` em `fontes/`

Os arquivos `fontes/*.json` e `fontes/*.csv` são derivados do `.html.md` correspondente e **não** são regenerados automaticamente — se o `.html.md` for recapturado, refaça a exportação manualmente:

```
source .venv/bin/activate
python gerar_fontes.py fontes/estimativas-de-populacao.html.md --formato json > fontes/estimativas-de-populacao.json
python gerar_fontes.py fontes/estimativas-de-populacao.html.md --formato csv > fontes/estimativas-de-populacao.csv
```

## Baixar os arquivos da árvore

`download.py` lê `fontes/estimativas-de-populacao.csv` e baixa todos os arquivos, replicando a árvore em `downloads/` (um `.sha256` é gravado ao lado de cada arquivo baixado):

```
source .venv/bin/activate
python download.py
```

Roda sequencialmente (um arquivo por vez, pastas mais recentes primeiro), pula arquivos já baixados, tenta cada download até 3 vezes e para a execução se todas as tentativas falharem. Ajuste as pausas com `--pausa-pastas` e `--pausa-arquivos`, e o destino com `--destino`.

## Contar extensões de arquivo

`identificar_extensoes.py` lê `fontes/estimativas-de-populacao.csv` e imprime no stdout a contagem de cada extensão de arquivo (`.pdf`, `.zip`, etc.), da mais para a menos frequente:

```
source .venv/bin/activate
python identificar_extensoes.py
```
