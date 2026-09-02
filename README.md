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
