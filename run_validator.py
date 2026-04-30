from pathlib import Path
from lxml import etree
import csv

def carregar_schema(xsd_path: str):
    with open(xsd_path, "rb") as f:
        schema_doc = etree.parse(f)
    return etree.XMLSchema(schema_doc)

def validar_xml(xml_path: Path, schema: etree.XMLSchema):
    try:
        with open(xml_path, "rb") as f:
            xml_doc = etree.parse(f)

        ok = schema.validate(xml_doc)

        if ok:
            return True, []
        else:
            erros = [f"Linha {e.line}, col {e.column}: {e.message}" for e in schema.error_log]
            return False, erros

    except Exception as e:
        return False, [str(e)]

def validar_pasta(xml_dir: str, xsd_path: str, output_csv: str = "relatorio_validacao.csv"):
    schema = carregar_schema(xsd_path)
    xml_dir = Path(xml_dir)

    resultados = []

    for xml_file in sorted(xml_dir.glob("*.xml")):
        valido, erros = validar_xml(xml_file, schema)
        resultados.append({
            "arquivo": xml_file.name,
            "valido": valido,
            "erros": " | ".join(erros) if erros else ""
        })

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["arquivo", "valido", "erros"])
        writer.writeheader()
        writer.writerows(resultados)

    return resultados

if __name__ == "__main__":
    resultados = validar_pasta(
        xml_dir="Sintetic_Xml",
        xsd_path="schemas/CT-e/procCTe_v4.00.xsd",
        output_csv="relatorio_validacao.csv"
    )

    for r in resultados:
        print(r["arquivo"], "OK" if r["valido"] else "ERRO")
        if r["erros"]:
            print(" ", r["erros"])