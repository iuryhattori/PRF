from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Address:
    xLgr: str
    nro: str
    xMun: str
    cMun: str
    UF: str
    CEP: str | None = None
    xBairro: str | None = None
    xCpl: str | None = None
    cPais: str = "1058"
    xPais: str = "Brasil"


@dataclass(slots=True)
class IdeCTe:
    cUF: str
    cCT: str
    CFOP: str
    natOp: str
    mod: str = "57"
    serie: str = "0"
    nCT: str = ""
    dhEmi: datetime = field(default_factory=datetime.now)
    tpImp: str = "1"
    tpEmis: str = "1"
    cDV: str = "0"
    tpAmb: str = "2"
    tpCTe: str = "0"
    procEmi: str = "0"
    verProc: str = "1.0.0"
    cMunEnv: str = ""
    xMunEnv: str = ""
    UFEnv: str = ""
    modal: str = "01"
    tpServ: str = "0"
    cMunIni: str = ""
    xMunIni: str = ""
    UFIni: str = ""
    cMunFim: str = ""
    xMunFim: str = ""
    UFFim: str = ""
    retira: str = "1"
    indIEToma: str = "9"
    Id: str | None = None
    chave: str | None = None
    xDetRetira: str | None = None
    indGlobalizado: str | None = None


@dataclass(slots=True)
class Emit:
    CNPJ: str
    IE: str
    xNome: str
    enderEmit: Address
    CRT: str = "3"
    IEST: str | None = None
    xFant: str | None = None
    fone: str | None = None


@dataclass(slots=True)
class ProtCTe:
    tpAmb: str
    verAplic: str
    chCTe: str
    dhRecbto: str
    nProt: str
    digVal: str
    cStat: str
    xMotivo: str

@dataclass(slots=True)
class Parte:
    xNome: str
    endereco: Address
    CNPJ: str | None = None
    CPF: str | None = None
    IE: str | None = None
    xFant: str | None = None
    fone: str | None = None
    email: str | None = None


@dataclass(slots=True)
class CompVPrest:
    xNome: str
    vComp: Decimal


@dataclass(slots=True)
class VPrest:
    vTPrest: Decimal
    vRec: Decimal
    Comp: list[CompVPrest] = field(default_factory=list)


@dataclass(slots=True)
class InfQ:
    cUnid: str
    tpMed: str
    qCarga: Decimal
    vCargaAverb: Decimal | None = None


@dataclass(slots=True)
class InfCarga:
    vCarga: Decimal
    proPred: str
    infQ: list[InfQ] = field(default_factory=list)
    xOutCat: str | None = None


@dataclass(slots=True)
class InfNFe:
    chave: str
    pin: str | None = None
    dPrev: str | None = None


@dataclass(slots=True)
class Icms:
    CST: str
    pRedBC: Decimal | None = None
    vBC: Decimal | None = None
    pICMS: Decimal | None = None
    vICMS: Decimal | None = None
    vTotTrib: Decimal | None = None
    vBCSTRet: Decimal | None = None
    vICMSSTRet: Decimal | None = None
    pICMSSTRet: Decimal | None = None
    vCred: Decimal | None = None


@dataclass(slots=True)
class VeicRodo:
    placa: str
    RENAVAM: str | None = None
    UF: str | None = None


@dataclass(slots=True)
class ModalRodoviario:
    RNTRC: str
    veic: VeicRodo | None = None
    occ: str | None = None
    TAF: str | None = None
    veicReboque: list[VeicRodo] = field(default_factory=list)