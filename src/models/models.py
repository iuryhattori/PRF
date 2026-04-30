# Criado por: Iury Hattori
# Motivo: Construir uma dataclass com os dados necessários para cada tipo de
# nota fiscal para facilitar a produção de dados sintéticos

from __future__ import annotations

from dataclasses import dataclass, field 

from .utils import IdeCTe, Emit, Parte, VPrest, InfCarga, Icms, InfNFe, ModalRodoviario, ProtCTe


@dataclass(slots=True)
class CTE:
    ide: IdeCTe
    emit: Emit
    rem: Parte
    dest: Parte
    vprest: VPrest
    infCarga: InfCarga
    icms: Icms
    infNFe: list[InfNFe] = field(default_factory=list)
    exped: Parte | None = None
    receb: Parte | None = None
    modal_rodo: ModalRodoviario | None = None
    protocolo: ProtCTe | None = None