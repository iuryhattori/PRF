# Criado por: Iury Hattori
# Motivo: Extrair os campos obrigatórios de cada .xsd para facilitar a geração de dados sintéticos

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field

import xmlschema


@dataclass(slots=True)
class Extractor:
    xsd_path: Path | str
    json_path: Path | str
    invoice: dict[str, dict[str, str]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.xsd_path = Path(self.xsd_path)
        self.json_path = Path(self.json_path)

    def _load_schema(self, file: Path) -> xmlschema.XMLSchema:
        return xmlschema.XMLSchema(str(file))

    def _create_root(self, json_path: Path, name: str) -> Path:
        new_folder = json_path / name
        new_folder.mkdir(parents=True, exist_ok=True)
        return new_folder

    def _save_json(self, path: Path, registry: dict) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(registry, f, indent=4, ensure_ascii=False)

    def _type_name(self, node) -> str:
        node_type = getattr(node, "type", None)
        if node_type is None:
            return "unknown"
        return getattr(node_type, "name", None) or "anonymous"

    def _extract_elements(
        self,
        element_node,
        parent_path: str = "",
        visited: set[str] | None = None
    ) -> dict[str, dict]:
        extracted_data: dict[str, dict] = {}

        if visited is None:
            visited = set()

        if element_node is None:
            return extracted_data

        element_name = getattr(element_node, "name", None)
        if not element_name:
            return extracted_data

        clean_name = element_name.split("}")[-1]
        current_path = f"{parent_path}/{clean_name}" if parent_path else clean_name

        node_type = getattr(element_node, "type", None)
        type_name = getattr(node_type, "name", None) if node_type else None
        visit_key = f"{current_path}::{type_name}"
        if visit_key in visited:
            return extracted_data
        visited.add(visit_key)

        is_required = getattr(element_node, "min_occurs", 1) > 0

        extracted_data[current_path] = {
            "required": is_required,
            "type": self._type_name(element_node),
            "kind": "element",
            "min_occurs": getattr(element_node, "min_occurs", None),
            "max_occurs": getattr(element_node, "max_occurs", None),
        }

        if node_type is None:
            return extracted_data

        attributes = getattr(node_type, "attributes", None)
        if attributes:
            for attr_name, attr in attributes.items():
                clean_attr_name = str(attr_name).split("}")[-1]
                attr_type = getattr(getattr(attr, "type", None), "name", None) or "unknown"
                attr_required = getattr(attr, "use", "optional") == "required"

                extracted_data[f"{current_path}/@{clean_attr_name}"] = {
                    "required": attr_required,
                    "type": attr_type,
                    "kind": "attribute",
                    "use": getattr(attr, "use", None),
                }

        if hasattr(node_type, "is_simple") and node_type.is_simple():
            return extracted_data

        content = getattr(node_type, "content", None)
        if content and hasattr(content, "iter_elements"):
            for child in content.iter_elements():
                extracted_data.update(
                    self._extract_elements(child, current_path, visited)
                )

        return extracted_data

    def extract_required_fields(self) -> None:
        if not self.xsd_path.exists():
            print(f"Erro: O diretório XSD '{self.xsd_path}' não foi encontrado.")
            return

        self.json_path.mkdir(parents=True, exist_ok=True)

        for invoice_dir in self.xsd_path.iterdir():
            if not invoice_dir.is_dir():
                continue

            name = invoice_dir.name
            output_dir = self._create_root(self.json_path, name)
            xsd_files = sorted(invoice_dir.glob("*.xsd"))

            for file in xsd_files:
                try:
                    invoice_info: dict[str, dict] = {}
                    schema = self._load_schema(file)

                    for root_name, root_element in schema.elements.items():
                        if root_name is None:
                            continue

                        invoice_info.update(self._extract_elements(root_element))

                    output_file = output_dir / f"{file.stem}.json"
                    self._save_json(output_file, invoice_info)

                    print(f"Sucesso: {output_file.name} gerado com {len(invoice_info)} campos.")

                except Exception as e:
                    print(f"Aviso: erro ao processar {file.name}: {e}")