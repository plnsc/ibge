# CLAUDE.md

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com o código deste repositório.

## Estado do projeto

Este é um projeto em estágio inicial (scaffold) para coletar dados do IBGE (Instituto Brasileiro de Geografia e Estatística), https://www.ibge.gov.br. O `main.py` ainda é o placeholder gerado pelo uv. A pasta `fontes/` contém capturas brutas de páginas (HTML envolvido em Markdown com um cabeçalho de frontmatter `url`/`acessado_em`) obtidas de páginas do IBGE, como a página de estimativas de população — esses são dados de referência/coletados, não código-fonte.

## Comandos

Este projeto usa o `uv` para gerenciamento de dependências (Python >=3.14, veja `pyproject.toml` / `uv.lock`), mas a execução deve ser feita através do ambiente virtual (`.venv`) já presente no repositório.

- Ativar o ambiente virtual: `source .venv/bin/activate`
- Executar a aplicação: `python main.py` (com o venv ativado)
- Sincronizar o ambiente/dependências: `uv sync`
- Adicionar uma dependência: `uv add <package>` (atualiza `pyproject.toml`/`uv.lock` e o `.venv`)
- Desativar o ambiente virtual: `deactivate`

Sempre ative o `.venv` antes de rodar comandos Python diretamente (`python`, `pip`, scripts). Ainda não há comandos de lint ou de testes configurados.

## Arquitetura

- `main.py` — ponto de entrada; lê o campo `description` de `pyproject.toml` (via `tomllib`) e o imprime.
- `pyproject.toml` — declara `selenium` e `chromium` como dependências, indicando que a automação de navegador é a abordagem de coleta pretendida para as páginas do IBGE (muitas páginas do IBGE renderizam conteúdo no lado do cliente).
- `fontes/` — diretório de saída para o conteúdo coletado das páginas, salvo em arquivos `.html.md` (HTML dentro de um bloco de código em um arquivo Markdown, com um pequeno frontmatter estilo YAML registrando a `url` de origem e o timestamp de acesso `acessado_em`).
- `gerar_fontes.py` — lê um arquivo `.html.md` (por padrão, `fontes/estimativas-de-populacao.html.md`, ou o caminho passado como argumento posicional), extrai o HTML do bloco de código, faz o parsing da árvore jsTree (`div#downloadFTP`) usando `html.parser` da stdlib e imprime a árvore de pastas/arquivos no stdout no formato `tree` (padrão), `json` ou `csv` (colunas `caminho`, `nome`, `tipo`, `url`), selecionável via `--formato`. Os nós do jsTree têm `href="#"` (sem link real), então a `url` de download é derivada concatenando `https://ftp.ibge.gov.br/` com o caminho hierárquico do nó — abordagem validada contra os links reais de `Estimativas_2026` presentes na própria página.

## Execução de scripts

Não execute os scripts criados neste repositório. Em vez disso, forneça o comando de execução e
aguarde a ação do usuário.

## Manutenção deste arquivo

Mantenha este `CLAUDE.md` atualizado com o estado corrente do repositório. Sempre que scripts,
comandos de execução ou a estrutura de arquivos mudarem, atualize as seções correspondentes acima
antes de concluir a tarefa.
