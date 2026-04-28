import argparse
from pathlib import Path
from src.extractor.extract import Extractor


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai campos obrigatórios de arquivos .xsd e salva como JSON"
    )
    parser.add_argument(
    "--xsd-path",
    type=Path,
    default=Path("./schemas"),   
    help="Caminho para a pasta raiz com os diretórios de .xsd"
)
    parser.add_argument(
    "--json-path",
    type=Path,
    default=Path("./RequiredFields"),    
    help="Caminho para a pasta de saída dos arquivos .json"
)
    args = parser.parse_args()

    extractor = Extractor(xsd_path=args.xsd_path, json_path=args.json_path)
    extractor.extract_required_fields()
    print("Extração concluída!")


if __name__ == "__main__":
    main()