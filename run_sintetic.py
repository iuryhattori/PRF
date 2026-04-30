from pathlib import Path
import random

from src.producer.producer import (
    ProduceAddress, ProduceEmit, ProduceParte,
    ProduceVPrest, ProduceInfCarga, ProduceIcms,
    ProduceIdeCTe, ProduceModalRodo, 
    ProduceProtCTe, ProtCTe
)
from src.models.utils import InfNFe
from src.models.models import CTE
from src.builder.builder import XML_Builder

output_dir = Path("Sintetic_Xml")
output_dir.mkdir(exist_ok=True)

def build_cte(tpAmb: str = "2") -> CTE:
    ide_data = ProduceIdeCTe().build(tpAmb=tpAmb)
    emit_data = ProduceEmit().build()
    

    aamm = "2604"
    serie_str = str(ide_data.serie).zfill(3)
    nct_str = str(ide_data.nCT).zfill(9)
    cct_str = str(ide_data.cCT).zfill(8)
    dv = str(random.randint(0, 9))
    
    chave_sintetica = f"{ide_data.cUF}{aamm}{emit_data.CNPJ}57{serie_str}{nct_str}1{cct_str}{dv}"
    
    return CTE(
        ide=ide_data,
        emit=emit_data,
        rem=ProduceParte().build(),
        dest=ProduceParte().build(pessoa_fisica=True),
        vprest=ProduceVPrest().build(),
        infCarga=ProduceInfCarga().build(),
        icms=ProduceIcms().build(),
        infNFe=[InfNFe(chave="4" + "1" * 43)],
        modal_rodo=ProduceModalRodo().build(),
        protocolo=ProduceProtCTe().build(chave_cte=chave_sintetica, tp_amb=tpAmb) 
    )

ctes = [build_cte() for _ in range(100)]

for i, cte in enumerate(ctes, start=1):
    xml = XML_Builder(cte).build_cte_xml()
    (output_dir / f"cte_{i:03}.xml").write_text(xml, encoding="utf-8")