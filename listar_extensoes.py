"""Conta as extensões de arquivo presentes em um CSV gerado pelo extrair_fontes.py."""

import argparse
from pathlib import Path

import pandas as pd

ARQUIVO_CSV_PADRAO = Path(__file__).with_name("fontes") / "estimativas-de-populacao.csv"


def extrair_extensoes(caminho_csv: Path) -> pd.Series:
    df = pd.read_csv(caminho_csv)
    nomes_arquivos = df.loc[df["tipo"] == "arquivo", "nome"]
    extensoes = nomes_arquivos.str.extract(r"\.([^.]+)$", expand=False).dropna().str.lower()
    return extensoes.value_counts()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Conta as extensoes de arquivo presentes em um CSV do extrair_fontes.py."
    )
    parser.add_argument(
        "csv",
        nargs="?",
        type=Path,
        default=ARQUIVO_CSV_PADRAO,
        help=f"Caminho do CSV de entrada (padrao: {ARQUIVO_CSV_PADRAO})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    contagem = extrair_extensoes(args.csv)
    print("Extensões encontradas nos arquivos do IBGE:")
    print("-" * 40)
    for extensao, quantidade in contagem.items():
        print(f"Extensão: .{extensao:<5} | Quantidade: {quantidade}")


if __name__ == "__main__":
    main()
