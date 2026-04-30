# src/extractor/extract.py

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd


def _f(elem, tag: str) -> str:
    """Busca um filho direto ignorando namespace."""
    found = elem.find(f"{{*}}{tag}")
    return found.text.strip() if found is not None and found.text else ""


def _ff(root, tag: str) -> ET.Element | None:
    """Busca recursiva em qualquer nível, ignorando namespace."""
    return root.find(f".//{{*}}{tag}")


def parse_cte(path: Path) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()

    cte_inf = root.find(".//{*}infCte") or root

    ide       = _ff(cte_inf, "ide")
    emit      = _ff(cte_inf, "emit")
    rem       = _ff(cte_inf, "rem")
    dest      = _ff(cte_inf, "dest")
    vprest    = _ff(cte_inf, "vPrest")
    inf_carga = _ff(cte_inf, "infCarga")
    modal     = _ff(cte_inf, "veicRodo")

    # ICMS — tenta cada CST possível
    icms_el = (
        _ff(cte_inf, "ICMS00") or _ff(cte_inf, "ICMS20") or
        _ff(cte_inf, "ICMS40") or _ff(cte_inf, "ICMS41") or
        _ff(cte_inf, "ICMS60")
    )

    def gf(elem, tag):
        return _f(elem, tag) if elem is not None else ""

    return {
        # Arquivo
        "arquivo":    path.name,

        # Identificação
        "nCT":        gf(ide, "nCT"),
        "cCT":        gf(ide, "cCT"),
        "CFOP":       gf(ide, "CFOP"),
        "dhEmi":      gf(ide, "dhEmi"),
        "tpAmb":      gf(ide, "tpAmb"),
        "modal":      gf(ide, "modal"),
        "xMunIni":    gf(ide, "xMunIni"),
        "UFIni":      gf(ide, "UFIni"),
        "xMunFim":    gf(ide, "xMunFim"),
        "UFFim":      gf(ide, "UFFim"),

        # Emitente
        "emit_CNPJ":  gf(emit, "CNPJ"),
        "emit_xNome": gf(emit, "xNome"),

        # Remetente
        "rem_CNPJ":   gf(rem, "CNPJ"),
        "rem_CPF":    gf(rem, "CPF"),
        "rem_xNome":  gf(rem, "xNome"),

        # Destinatário
        "dest_CNPJ":  gf(dest, "CNPJ"),
        "dest_CPF":   gf(dest, "CPF"),
        "dest_xNome": gf(dest, "xNome"),

        # Valores
        "vTPrest":    gf(vprest, "vTPrest"),
        "vRec":       gf(vprest, "vRec"),

        # Carga
        "vCarga":     gf(inf_carga, "vCarga"),
        "proPred":    gf(inf_carga, "proPred"),

        # ICMS
        "CST":        gf(icms_el, "CST"),
        "vBC":        gf(icms_el, "vBC"),
        "pICMS":      gf(icms_el, "pICMS"),
        "vICMS":      gf(icms_el, "vICMS"),

        # Veículo
        "placa":      gf(modal, "placa"),
        "UF_veiculo": gf(modal, "UF"),
    }


def xml_folder_to_csv(input_dir: str | Path, output_csv: str | Path) -> pd.DataFrame:
    input_dir  = Path(input_dir)
    output_csv = Path(output_csv)

    files = sorted(input_dir.glob("*.xml"))
    if not files:
        print(f"Nenhum XML encontrado em: {input_dir}")
        return pd.DataFrame()

    rows = [parse_cte(f) for f in files if (row := parse_cte(f))]
    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ {len(df)} CT-e exportados → {output_csv}")
    return df