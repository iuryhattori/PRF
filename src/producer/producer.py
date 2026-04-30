# factories/producers.py
# Criado por: Iury Hattori

from __future__ import annotations
import base64
import os
import random
import string
from decimal import Decimal

from faker import Faker

from src.models.utils import (
    Address, IdeCTe, Emit, Parte,
    CompVPrest, VPrest, InfQ, InfCarga,
    InfNFe, Icms, VeicRodo, ModalRodoviario, ProtCTe
)


MUNICIPIOS: list[tuple[str, str, str, str]] = [
    ("3550308", "São Paulo", "SP", "35"),
    ("3509502", "Campinas", "SP", "35"),
    ("3304557", "Rio de Janeiro", "RJ", "33"),
    ("3106200", "Belo Horizonte", "MG", "31"),
    ("4106902", "Curitiba", "PR", "41"),
    ("4314902", "Porto Alegre", "RS", "43"),
    ("2304400", "Fortaleza", "CE", "23"),
    ("2927408", "Salvador", "BA", "29"),
    ("5300108", "Brasília", "DF", "53"),
]

UF_IBGE = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
    "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27",
    "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35", "PR": "41",
    "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53",
}

CFOP_TRANSPORTE = ["6351", "6352", "6353", "6354", "6360"]
CST_ICMS = ["00", "20", "40", "41", "51", "60", "90"]
PRODUTOS = ["ELETRODOMÉSTICOS", "ALIMENTOS", "VESTUÁRIO", "AUTOPEÇAS", "MEDICAMENTOS"]
UNIDADES = [("01", "PESO BRUTO"), ("00", "CUBAGEM"), ("03", "QUANTIDADE")]


class ProduceAddress:
    def __init__(self):
        self._faker = Faker("pt_BR")

    @property
    def CEP(self) -> str:
        return self._faker.postcode(False)

    @property
    def xLgr(self) -> str:
        return self._faker.street_name()

    @property
    def nro(self) -> str:
        return self._faker.building_number()

    @property
    def xBairro(self) -> str:
        return self._faker.neighborhood()

    def build(self, cMun: str = "", xMun: str = "", UF: str = "") -> Address:
        if not cMun:
            cMun, xMun, UF, _ = random.choice(MUNICIPIOS)
        return Address(
            xLgr=self.xLgr,
            nro=self.nro,
            xBairro=self.xBairro,
            xMun=xMun,
            cMun=cMun,
            UF=UF,
            CEP=self.CEP,
        )


class ProduceEmit:
    def __init__(self):
        self._faker = Faker("pt_BR")
        self._addr = ProduceAddress()

    @property
    def CNPJ(self) -> str:
        return "".join(filter(str.isdigit, self._faker.cnpj()))

    @property
    def IE(self) -> str:
        return self._faker.numerify("###########")

    @property
    def xNome(self) -> str:
        return self._faker.company().upper()

    @property
    def xFant(self) -> str:
        return self._faker.company_suffix()

    def build(self) -> Emit:
        return Emit(
            CNPJ=self.CNPJ,
            IE=self.IE,
            xNome=self.xNome,
            xFant=self.xFant,
            enderEmit=self._addr.build(),
            CRT="3",
        )


class ProduceParte:
    def __init__(self):
        self._faker = Faker("pt_BR")
        self._addr = ProduceAddress()

    @property
    def CNPJ(self) -> str:
        return "".join(filter(str.isdigit, self._faker.cnpj()))

    @property
    def CPF(self) -> str:
        return "".join(filter(str.isdigit, self._faker.cpf()))

    @property
    def xNome(self) -> str:
        return self._faker.company().upper()

    @property
    def fone(self) -> str:
        return self._faker.numerify("###########")

    @property
    def email(self) -> str:
        return self._faker.email()

    def build(self, pessoa_fisica: bool = False) -> Parte:
        return Parte(
            xNome=self.xNome if not pessoa_fisica else self._faker.name().upper(),
            endereco=self._addr.build(),
            CNPJ=None if pessoa_fisica else self.CNPJ,
            CPF=self.CPF if pessoa_fisica else None,
            IE=self._faker.numerify("###########"),
            fone=self.fone,
            email=self.email,
        )


class ProduceVPrest:
    def build(self) -> VPrest:
        frete = Decimal(str(round(random.uniform(500, 5_000), 2)))
        seguro = (frete * Decimal("0.03")).quantize(Decimal("0.01"))
        total = frete + seguro
        return VPrest(
            vTPrest=total,
            vRec=total,
            Comp=[
                CompVPrest("FRETE PESO", frete),
                CompVPrest("SEGURO", seguro),
            ],
        )


class ProduceInfCarga:
    def build(self) -> InfCarga:
        cUnid, tpMed = random.choice(UNIDADES)
        return InfCarga(
            vCarga=Decimal(str(round(random.uniform(5_000, 200_000), 2))),
            proPred=random.choice(PRODUTOS),
            infQ=[InfQ(
                cUnid=cUnid,
                tpMed=tpMed,
                qCarga=Decimal(str(round(random.uniform(100, 5_000), 4))),
            )],
        )


class ProduceIcms:
    def build(self) -> Icms:
        cst = random.choice(CST_ICMS)

        if cst in ("00", "90"):
            vBC = Decimal(str(round(random.uniform(500, 5_000), 2)))
            pICMS = Decimal("12.00")
            return Icms(
                CST=cst,
                vBC=vBC,
                pICMS=pICMS,
                vICMS=(vBC * pICMS / 100).quantize(Decimal("0.01")),
            )

        if cst == "20":
            vBC = Decimal(str(round(random.uniform(500, 5_000), 2)))
            pICMS = Decimal("12.00")
            return Icms(
                CST=cst,
                pRedBC=Decimal("33.33"), 
                vBC=vBC,
                pICMS=pICMS,
                vICMS=(vBC * pICMS / 100).quantize(Decimal("0.01")),
            )

        if cst in ("40", "41", "51"):
            return Icms(CST=cst)

        if cst == "60":
            return Icms(
                CST=cst,
                vBCSTRet=Decimal("0.00"),
                vICMSSTRet=Decimal("0.00"),
                pICMSSTRet=Decimal("0.00"),
                vCred=Decimal("0.00")
            )

        return Icms(CST="41")


class ProduceIdeCTe:
    def __init__(self):
        self._faker = Faker("pt_BR")

    def build(self, tpAmb: str = "2", modal: str = "01") -> IdeCTe:
        ini = random.choice(MUNICIPIOS)
        fim = random.choice(MUNICIPIOS)
        env = random.choice(MUNICIPIOS)

        return IdeCTe(
            cUF=ini[3],
            cCT=self._faker.numerify("########"),
            CFOP=random.choice(CFOP_TRANSPORTE),
            natOp="PRESTAÇÃO DE SERVIÇO DE TRANSPORTE",
            nCT=self._faker.numerify("######"),
            dhEmi=self._faker.date_time_between(start_date="-30d", end_date="now"),
            tpAmb=tpAmb,
            modal=modal,
            cMunEnv=env[0], xMunEnv=env[1], UFEnv=env[2],
            cMunIni=ini[0], xMunIni=ini[1], UFIni=ini[2],
            cMunFim=fim[0], xMunFim=fim[1], UFFim=fim[2],
            indIEToma="1",
            xDetRetira=None,
        )


class ProduceModalRodo:
    def __init__(self):
        self._faker = Faker("pt_BR")

    @property
    def placa(self) -> str:
        letras = "".join(random.choices(string.ascii_uppercase, k=3))
        d1 = random.randint(0, 9)
        letra4 = random.choice(string.ascii_uppercase)
        d2 = random.randint(0, 9)
        d3 = random.randint(0, 9)
        return f"{letras}{d1}{letra4}{d2}{d3}"

    def build(self) -> ModalRodoviario:
        _, _, UF, _ = random.choice(MUNICIPIOS)
        return ModalRodoviario(
            RNTRC=self._faker.numerify("########"),
            veic=VeicRodo(placa=self.placa, UF=UF),
        )

class ProduceProtCTe:
    def __init__(self):
        self._faker = Faker("pt_BR")

    def build(self, chave_cte: str, tp_amb: str = "1") -> ProtCTe:
        dh_recbto = self._faker.date_time_between(start_date="-5d", end_date="now")
        
        fake_digest = base64.b64encode(os.urandom(20)).decode('utf-8')

        return ProtCTe(
            tpAmb=tp_amb,
            verAplic="SP_PL_CTe_400",
            chCTe=chave_cte,
            dhRecbto=dh_recbto.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
            nProt=str(self._faker.random_int(min=100000000000000, max=999999999999999)),
            digVal=fake_digest,
            cStat="100",
            xMotivo="Autorizado o uso do CT-e"
        )