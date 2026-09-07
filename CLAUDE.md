# CLAUDE.md

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com o código deste repositório.

## Estado do projeto

Este é um projeto em estágio inicial (scaffold) para coletar dados públicos do IBGE (Instituto Brasileiro de Geografia e Estatística), https://www.ibge.gov.br. A pasta `fontes/` guarda capturas brutas de páginas do IBGE — dados de referência/coletados, não código-fonte (detalhes em Arquitetura).

Este repositório **não** faz uso da API SIDRA (https://sidra.ibge.gov.br): a coleta é por scraping direto do site do IBGE, como faria um visitante humano, uma prova de conceito.

Este repositório usa Git LFS: o `.gitattributes` rastreia todo o conteúdo de `datasets/` (`datasets/** filter=lfs diff=lfs merge=lfs -text`) — os arquivos baixados pelo `download.py`, de qualquer extensão. Os `.sha256` gravados ao lado de cada arquivo são explicitamente excluídos dessa regra (`*.sha256 !filter !diff !merge !text`), permanecendo como blobs normais do Git.

## Comandos

Dependências gerenciadas com `uv` (Python >=3.14, veja `pyproject.toml`/`uv.lock`); execução sempre via ambiente virtual (`.venv`), criado com `uv venv` e sincronizado com `uv sync`.

- Ativar o ambiente virtual: `source .venv/bin/activate`
- Executar a aplicação: `python main.py` (com o venv ativado)
- Sincronizar o ambiente/dependências: `uv sync`
- Adicionar uma dependência: `uv add <package>` (atualiza `pyproject.toml`/`uv.lock` e o `.venv`)
- Desativar o ambiente virtual: `deactivate`

Sempre ative o `.venv` antes de rodar comandos Python diretamente (`python`, `pip`, scripts). Ainda não há comandos de lint ou de testes configurados.

## Arquitetura

- `main.py` — ponto de entrada; lê o campo `description` de `pyproject.toml` (via `tomllib`) e o imprime.
- `pyproject.toml` — declara as dependências do projeto:
  - `selenium` e `chromium` — automação de navegador, abordagem de coleta pretendida para as páginas do IBGE (muitas renderizam conteúdo no lado do cliente).
- `uv.lock` — arquivo de lock gerado pelo `uv` a partir do `pyproject.toml`, fixando as versões exatas (e hashes) de todas as dependências, diretas e transitivas; mantido em sincronia com o `.venv` via `uv sync` e não deve ser editado manualmente.
- `fontes/` — diretório com os dados brutos coletados e seus derivados:
  - `*.html.md` — captura bruta da página (HTML dentro de um bloco de código em um arquivo Markdown, com um pequeno frontmatter estilo YAML registrando a `url` de origem e o timestamp de acesso `acessado_em`); entrada para o `extrair_fontes.py`. O HTML é o DOM renderizado, copiado via Ferramentas do desenvolvedor do Chrome (`Elements` → `Copy outerHTML` no `<html>`), não o "ver código-fonte" da página — necessário porque a árvore de pastas é montada em JavaScript no lado do cliente.
  - `*.json` / `*.csv` — saídas geradas manualmente a partir do `.html.md` correspondente via `extrair_fontes.py --formato json|csv > fontes/<nome>.<ext>`; não são geradas automaticamente, então podem ficar desatualizadas em relação ao `.html.md` se este for recapturado.
- `download.py` — lê `fontes/estimativas-de-populacao.csv` (colunas `caminho,nome,tipo,url` geradas pelo `extrair_fontes.py`) e baixa todos os arquivos, replicando a árvore em `datasets/`:
  - percorre as pastas `Estimativas_de_Populacao/Estimativas_*` de baixo para cima (mais recente primeiro) e os arquivos de cada pasta de cima para baixo;
  - baixa um arquivo por vez, com pausa maior entre pastas e menor entre arquivos (`--pausa-pastas`/`--pausa-arquivos`);
  - pula arquivos já existentes;
  - tenta cada download até 3 vezes e **para a execução** se todas falharem;
  - grava um `.sha256` ao lado de cada arquivo.
- `extrair_fontes.py` — lê um arquivo `.html.md` (por padrão, `fontes/estimativas-de-populacao.html.md`, ou o caminho passado como argumento posicional):
  - extrai o HTML do bloco de código e faz o parsing da árvore jsTree (`div#downloadFTP`) usando `html.parser` da stdlib;
  - imprime a árvore de pastas/arquivos no stdout no formato `tree` (padrão), `json` ou `csv` (colunas `caminho`, `nome`, `tipo`, `url`), selecionável via `--formato`;
  - os nós do jsTree têm `href="#"` (sem link real), então a `url` de download é derivada concatenando `https://ftp.ibge.gov.br/` com o caminho hierárquico do nó — abordagem validada contra os links reais de `Estimativas_2026` presentes na própria página.

## Execução de scripts

Não execute os scripts criados neste repositório. Em vez disso, forneça o comando de execução e aguarde a ação do usuário.

## Manutenção deste arquivo

Mantenha este `CLAUDE.md` atualizado: sempre que scripts, comandos ou a estrutura de arquivos mudarem, atualize as seções correspondentes antes de concluir a tarefa.

## Manutenção do README.md

Atualize o `README.md` junto com o `CLAUDE.md`: sempre que um script for criado, renomeado ou tiver comando/opções alterados, ajuste a seção correspondente na mesma tarefa. Divisão de papéis: `README.md` é a documentação de uso (comandos e fluxos, voltada ao usuário); `CLAUDE.md` é o contexto de arquitetura e convenções (voltado ao Claude Code) — evite duplicar detalhes de implementação no `README.md`.
