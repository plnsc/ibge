"""Extrai a arvore jsTree de fontes/estimativas-de-populacao.html.md e a exibe no stdout."""

import argparse
import csv
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ARQUIVO_PADRAO = Path(__file__).with_name("fontes") / "estimativas-de-populacao.html.md"
URL_BASE_FTP = "https://ftp.ibge.gov.br/"


class JsTreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = {"nome": None, "filhos": []}
        self.pilha_nos = [self.raiz]
        self.dentro_da_arvore = False
        self.profundidade_div = 0
        self.capturando_ancora = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.dentro_da_arvore:
            if tag == "div" and attrs.get("id") == "downloadFTP":
                self.dentro_da_arvore = True
                self.profundidade_div = 1
            return

        if tag == "div":
            self.profundidade_div += 1
        elif tag == "li":
            classes = attrs.get("class", "").split()
            no = {"nome": "", "filhos": [], "folha": "jstree-leaf" in classes}
            self.pilha_nos[-1]["filhos"].append(no)
            self.pilha_nos.append(no)
        elif tag == "a" and "jstree-anchor" in attrs.get("class", "").split():
            self.capturando_ancora = True

    def handle_endtag(self, tag):
        if not self.dentro_da_arvore:
            return
        if tag == "div":
            self.profundidade_div -= 1
            if self.profundidade_div == 0:
                self.dentro_da_arvore = False
        elif tag == "li":
            self.pilha_nos.pop()
        elif tag == "a":
            self.capturando_ancora = False

    def handle_data(self, data):
        if self.dentro_da_arvore and self.capturando_ancora:
            texto = data.strip()
            if texto:
                self.pilha_nos[-1]["nome"] += texto


def extrair_html(caminho: Path) -> str:
    conteudo = caminho.read_text(encoding="utf-8")
    inicio = conteudo.find("```html")
    fim = conteudo.rfind("```")
    if inicio == -1 or fim == -1:
        return conteudo
    return conteudo[inicio + len("```html") : fim]


def montar_caminho(caminho_pai: str, nome: str) -> str:
    if caminho_pai == "" or caminho_pai.endswith("/"):
        return caminho_pai + nome
    return f"{caminho_pai}/{nome}"


def anotar_caminhos_e_urls(no: dict, caminho_pai: str = "") -> None:
    for filho in no["filhos"]:
        filho["caminho"] = montar_caminho(caminho_pai, filho["nome"])
        filho["url"] = URL_BASE_FTP + filho["caminho"]
        anotar_caminhos_e_urls(filho, filho["caminho"])


def montar_arvore(html: str) -> dict:
    parser = JsTreeParser()
    parser.feed(html)
    anotar_caminhos_e_urls(parser.raiz)
    return parser.raiz


def imprimir_arvore(no: dict, prefixo: str = "") -> None:
    filhos = no["filhos"]
    for i, filho in enumerate(filhos):
        eh_ultimo = i == len(filhos) - 1
        conector = "└── " if eh_ultimo else "├── "
        print(f"{prefixo}{conector}{filho['nome']}")
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        imprimir_arvore(filho, novo_prefixo)


def imprimir_json(arvore: dict) -> None:
    print(json.dumps(arvore["filhos"], ensure_ascii=False, indent=2))


def linhas_csv(no: dict) -> list[tuple[str, str, str, str]]:
    linhas = []
    for filho in no["filhos"]:
        tipo = "arquivo" if filho.get("folha") else "pasta"
        linhas.append((filho["caminho"], filho["nome"], tipo, filho["url"]))
        linhas.extend(linhas_csv(filho))
    return linhas


def imprimir_csv(arvore: dict) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["caminho", "nome", "tipo", "url"])
    writer.writerows(linhas_csv(arvore))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai e exibe no stdout a arvore jsTree de um arquivo .html.md do IBGE."
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        type=Path,
        default=ARQUIVO_PADRAO,
        help=f"Caminho do arquivo .html.md (padrao: {ARQUIVO_PADRAO})",
    )
    parser.add_argument(
        "--formato",
        choices=["tree", "json", "csv"],
        default="tree",
        help="Formato de saida: 'tree' (padrao), 'json' ou 'csv'",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    html = extrair_html(args.arquivo)
    arvore = montar_arvore(html)
    if args.formato == "json":
        imprimir_json(arvore)
    elif args.formato == "csv":
        imprimir_csv(arvore)
    else:
        imprimir_arvore(arvore)


if __name__ == "__main__":
    main()
