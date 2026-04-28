
# Criado por: Iury Hattori
#Motivo: Extrair os campos obrigatórios de cada .xsd para facilitar a geração de dados sintéticos

from numpy import require
from pydantic import FilePath
import xmlschema
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, field
import os


@dataclass(slots=True)
class Extractor:
    xsd_path: Path | str
    json_path : Path | str
    invoice : dict[str, dict[str, str]] = field(init=False, default_factory=dict)
    def __post_init__(self):
        self.xsd_path = Path(self.xsd_path)
        self.json_path = Path(self.json_path)

    def _load_schema(self, file: str) -> xmlschema.XMLSchema:
        return xmlschema.XMLSchema(file)

    def _create_root(self, json_path : Path | str, name : str) -> None:
        new_folder = json_path / name
        new_folder.mkdir(parents=True, exist_ok=True)
    def _save_json(self, path : str, registry : dict) -> None:
        with open(path, 'w') as f:
            json.dump(registry, f, indent=4)

    def _extract_elements(self, element_node, parent_path="") -> dict:
        """Navega pela árvore do XSD à prova de falhas estruturais."""
        extracted_data = {}
        
        if element_node is None or not hasattr(element_node, 'type') or element_node.type is None:
            return extracted_data

        if element_node.type.is_simple():
            is_required = getattr(element_node, 'min_occurs', 1) > 0
            type_name = getattr(element_node.type, 'name', 'simple')
            
            extracted_data[parent_path] = {
                "Required": is_required,
                "Type": type_name
            }
            return extracted_data

        if element_node.type.is_complex():
            content = getattr(element_node.type, 'content', None)
            
            if content and hasattr(content, 'iter_elements'):
                for child in content.iter_elements():
                    
                    child_name = getattr(child, 'name', None)
                    if child_name is None:
                        continue
                        
                    clean_name = child_name.split('}')[-1]
                    current_path = f"{parent_path}/{clean_name}" if parent_path else clean_name
                    extracted_data.update(self._extract_elements(child, current_path))
                    
        return extracted_data
    
    def extract_require_fields(self) -> None:
        if not self.xsd_path.exists():
            print(f"Erro: O diretório XSD '{self.xsd_path}' não foi encontrado.")
            return

        for invoice_dir in self.xsd_path.iterdir():
            if not invoice_dir.is_dir():
                continue
                
            name = invoice_dir.name
            path = self.json_path / name
            self._create_root(self.json_path, name)
            
            xsd_files = sorted(invoice_dir.glob("*.xsd"))
            
            for file in xsd_files:
                try:
                    invoice_info: dict[str, dict] = {}
                    schema = self._load_schema(file)
                    

                    for root_name, root_element in schema.elements.items():
                        if root_name is None:
                            continue
                            
                        clean_root_name = root_name.split('}')[-1]
                        invoice_info.update(self._extract_elements(root_element, clean_root_name))
                    
                    output_file = path / f"{file.stem}.json"
                    self._save_json(output_file, invoice_info)
                    
                    print(f"Sucesso: {output_file.name} gerado com {len(invoice_info)} campos.")
                    
                except Exception as e:
                    print(f"Aviso: Erro inesperado ao processar {file.name}: {e}")






    



