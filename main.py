import tomllib
from pathlib import Path


def main():
    pyproject = tomllib.loads(Path(__file__).with_name("pyproject.toml").read_text())
    print(pyproject["project"]["description"])


if __name__ == "__main__":
    main()
