"""Baixa os arquivos listados em fontes/estimativas-de-populacao.csv, replicando a
arvore de pastas no sistema de arquivos e gerando um .sha256 por arquivo baixado."""

import argparse
import csv
import hashlib
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ARQUIVO_CSV_PADRAO = Path(__file__).with_name("fontes") / "estimativas-de-populacao.csv"
DIRETORIO_DESTINO_PADRAO = Path(__file__).with_name("downloads")

PADRAO_PASTA_ANO = re.compile(r"^Estimativas_de_Populacao/Estimativas_[^/]+$")
MAX_TENTATIVAS = 3
TIMEOUT_REQUISICAO = 60
TAMANHO_BLOCO = 64 * 1024
USER_AGENT = "Mozilla/5.0 (compatible; ibge-download-script/1.0)"


def ler_linhas(caminho_csv: Path) -> list[dict]:
    with caminho_csv.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def agrupar_por_pasta_ano(linhas: list[dict]) -> list[tuple[dict, list[dict]]]:
    blocos: list[tuple[dict, list[dict]]] = []
    bloco_atual: tuple[dict, list[dict]] | None = None
    for linha in linhas:
        if linha["tipo"] == "pasta" and PADRAO_PASTA_ANO.match(linha["caminho"]):
            bloco_atual = (linha, [])
            blocos.append(bloco_atual)
        elif linha["tipo"] == "arquivo" and bloco_atual is not None:
            if linha["caminho"].startswith(bloco_atual[0]["caminho"] + "/"):
                bloco_atual[1].append(linha)
    return blocos


def calcular_sha256(caminho_arquivo: Path) -> str:
    sha256 = hashlib.sha256()
    with caminho_arquivo.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(TAMANHO_BLOCO), b""):
            sha256.update(bloco)
    return sha256.hexdigest()


def gravar_sha256(destino: Path) -> None:
    caminho_sha256 = destino.with_suffix(destino.suffix + ".sha256")
    digest = calcular_sha256(destino)
    caminho_sha256.write_text(f"{digest}  {destino.name}\n", encoding="utf-8")


def baixar_arquivo(url: str, destino: Path) -> None:
    requisicao = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    destino_parcial = destino.with_suffix(destino.suffix + ".part")
    sha256 = hashlib.sha256()
    try:
        with urllib.request.urlopen(requisicao, timeout=TIMEOUT_REQUISICAO) as resposta:
            with destino_parcial.open("wb") as saida:
                for bloco in iter(lambda: resposta.read(TAMANHO_BLOCO), b""):
                    saida.write(bloco)
                    sha256.update(bloco)
    except BaseException:
        destino_parcial.unlink(missing_ok=True)
        raise
    destino_parcial.replace(destino)
    destino.with_suffix(destino.suffix + ".sha256").write_text(
        f"{sha256.hexdigest()}  {destino.name}\n", encoding="utf-8"
    )


def baixar_com_retentativas(url: str, destino: Path) -> None:
    ultimo_erro: Exception | None = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            baixar_arquivo(url, destino)
            return
        except (urllib.error.URLError, OSError) as erro:
            ultimo_erro = erro
            print(f"    tentativa {tentativa}/{MAX_TENTATIVAS} falhou: {erro}", file=sys.stderr)
    raise RuntimeError(f"falha ao baixar {url} apos {MAX_TENTATIVAS} tentativas") from ultimo_erro


def processar_arquivo(linha: dict, diretorio_destino: Path) -> None:
    destino = diretorio_destino / linha["caminho"]
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists():
        print(f"  ja existe, pulando: {linha['caminho']}")
        if not destino.with_suffix(destino.suffix + ".sha256").exists():
            gravar_sha256(destino)
        return

    print(f"  baixando: {linha['caminho']}")
    baixar_com_retentativas(linha["url"], destino)


def executar(
    linhas: list[dict],
    diretorio_destino: Path,
    pausa_pastas: float,
    pausa_arquivos: float,
) -> None:
    blocos = agrupar_por_pasta_ano(linhas)
    blocos.reverse()  # entra nos nos Estimativas_* de baixo para cima

    for indice_bloco, (pasta, filhos) in enumerate(blocos):
        print(f"Pasta: {pasta['caminho']}")
        (diretorio_destino / pasta["caminho"]).mkdir(parents=True, exist_ok=True)

        for indice_filho, filho in enumerate(filhos):  # filhos de cima para baixo
            try:
                processar_arquivo(filho, diretorio_destino)
            except RuntimeError as erro:
                print(f"Erro fatal: {erro}", file=sys.stderr)
                sys.exit(1)
            if indice_filho < len(filhos) - 1:
                time.sleep(pausa_arquivos)

        if indice_bloco < len(blocos) - 1:
            time.sleep(pausa_pastas)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os arquivos da arvore do IBGE listados em um CSV gerado pelo gerar_fontes.py."
    )
    parser.add_argument(
        "csv",
        nargs="?",
        type=Path,
        default=ARQUIVO_CSV_PADRAO,
        help=f"Caminho do CSV de entrada (padrao: {ARQUIVO_CSV_PADRAO})",
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=DIRETORIO_DESTINO_PADRAO,
        help=f"Diretorio onde a arvore sera replicada (padrao: {DIRETORIO_DESTINO_PADRAO})",
    )
    parser.add_argument(
        "--pausa-pastas",
        type=float,
        default=5.0,
        help="Pausa em segundos entre pastas Estimativas_* (padrao: %(default)s)",
    )
    parser.add_argument(
        "--pausa-arquivos",
        type=float,
        default=1.0,
        help="Pausa em segundos entre arquivos de uma mesma pasta (padrao: %(default)s)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    linhas = ler_linhas(args.csv)
    executar(linhas, args.destino, args.pausa_pastas, args.pausa_arquivos)


if __name__ == "__main__":
    main()
