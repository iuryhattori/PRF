from __future__ import annotations

import xml.etree.ElementTree as ET
from src.models.models import CTE
from src.models.utils import Address, Parte

NS = "http://www.portalfiscal.inf.br/cte"
ET.register_namespace("", NS)


class XML_Builder:
    def __init__(self, cte: CTE):
        self._cte = cte

    def _sub(self, parent: ET.Element, tag: str, text: str | None = None) -> ET.Element:
        el = ET.SubElement(parent, tag)
        if text is not None:
            el.text = str(text)
        return el

    def _address_emit(self, parent: ET.Element, end: Address, fone: str | None = None) -> None:
        e = self._sub(parent, "enderEmit")
        self._sub(e, "xLgr", end.xLgr)
        self._sub(e, "nro", end.nro)
        if end.xCpl:
            self._sub(e, "xCpl", end.xCpl)
        if end.xBairro:
            self._sub(e, "xBairro", end.xBairro)
        self._sub(e, "cMun", end.cMun)
        self._sub(e, "xMun", end.xMun)
        if end.CEP:
            self._sub(e, "CEP", end.CEP)
        self._sub(e, "UF", end.UF)
        if fone:
            self._sub(e, "fone", fone)

    def _address(self, parent: ET.Element, tag: str, end: Address) -> None:  # Sem fone aqui
        e = self._sub(parent, tag)
        self._sub(e, "xLgr", end.xLgr)
        self._sub(e, "nro", end.nro)
        if end.xCpl:
            self._sub(e, "xCpl", end.xCpl)
        if end.xBairro:
            self._sub(e, "xBairro", end.xBairro)
        self._sub(e, "cMun", end.cMun)
        self._sub(e, "xMun", end.xMun)
        if end.CEP:
            self._sub(e, "CEP", end.CEP)
        self._sub(e, "UF", end.UF)
        if end.cPais:
            self._sub(e, "cPais", end.cPais)
        if end.xPais:
            self._sub(e, "xPais", end.xPais)

    def _parte(self, parent: ET.Element, tag: str, parte: Parte) -> None:
        p = self._sub(parent, tag)
        if parte.CNPJ:
            self._sub(p, "CNPJ", parte.CNPJ)
        elif parte.CPF:
            self._sub(p, "CPF", parte.CPF)
        if parte.IE:
            self._sub(p, "IE", parte.IE)
        self._sub(p, "xNome", parte.xNome)
        if parte.xFant:
            self._sub(p, "xFant", parte.xFant)
        if parte.fone:  # Fone AQUI, antes do endereço
            self._sub(p, "fone", parte.fone)
        if tag == "dest" and getattr(parte, "ISUF", None):
            self._sub(p, "ISUF", parte.ISUF)
        addr_tag = {
            "rem": "enderReme",
            "dest": "enderDest",
            "exped": "enderExped",
            "receb": "enderReceb",
        }.get(tag)
        if parte.endereco and addr_tag:
            self._address(p, addr_tag, parte.endereco)
        if getattr(parte, "email", None):
            self._sub(p, "email", parte.email)

    def _fmt_dec(self, value, places="2"):
        return "0.00" if value is None else f"{float(value):.{places}f}"

    def _build_icms(self, parent: ET.Element) -> None:
        imp = self._sub(parent, "imp")
        icms_g = self._sub(imp, "ICMS")
        cst = self._cte.icms.CST

        if cst == "00":
            icms = self._sub(icms_g, "ICMS00")
            self._sub(icms, "CST", cst)
            if self._cte.icms.vBC is not None:
                self._sub(icms, "vBC", self._fmt_dec(self._cte.icms.vBC))
            if self._cte.icms.pICMS is not None:
                self._sub(icms, "pICMS", self._fmt_dec(self._cte.icms.pICMS))
            if self._cte.icms.vICMS is not None:
                self._sub(icms, "vICMS", self._fmt_dec(self._cte.icms.vICMS))

        elif cst == "20":
            icms = self._sub(icms_g, "ICMS20")
            self._sub(icms, "CST", cst)
            
            # Escreve a tag obrigatoriamente sem o `if`
            self._sub(icms, "pRedBC", self._fmt_dec(self._cte.icms.pRedBC))
            
            if self._cte.icms.vBC is not None:
                self._sub(icms, "vBC", self._fmt_dec(self._cte.icms.vBC))
            if self._cte.icms.pICMS is not None:
                self._sub(icms, "pICMS", self._fmt_dec(self._cte.icms.pICMS))
            if self._cte.icms.vICMS is not None:
                self._sub(icms, "vICMS", self._fmt_dec(self._cte.icms.vICMS))

        elif cst in {"40", "41", "51"}:
            icms = self._sub(icms_g, "ICMS45")
            self._sub(icms, "CST", cst)

        elif cst == "60":
            icms = self._sub(icms_g, "ICMS60")
            self._sub(icms, "CST", cst)
            self._sub(icms, "vBCSTRet", self._fmt_dec(self._cte.icms.vBCSTRet))
            self._sub(icms, "vICMSSTRet", self._fmt_dec(self._cte.icms.vICMSSTRet))
            self._sub(icms, "pICMSSTRet", self._fmt_dec(self._cte.icms.pICMSSTRet))
            self._sub(icms, "vCred", self._fmt_dec(self._cte.icms.vCred))

        elif cst == "90":
            icms = self._sub(icms_g, "ICMS90")
            self._sub(icms, "CST", cst)
            if self._cte.icms.vBC is not None:
                self._sub(icms, "vBC", self._fmt_dec(self._cte.icms.vBC))
            if self._cte.icms.pICMS is not None:
                self._sub(icms, "pICMS", self._fmt_dec(self._cte.icms.pICMS))
            if self._cte.icms.vICMS is not None:
                self._sub(icms, "vICMS", self._fmt_dec(self._cte.icms.vICMS))

        else:
            raise ValueError(f"CST de ICMS não suportado: {cst}")

        if self._cte.icms.vTotTrib is not None:
            self._sub(imp, "vTotTrib", self._fmt_dec(self._cte.icms.vTotTrib))

    def build_cte_xml(self) -> str:
        root = ET.Element("CTe", xmlns=NS)

        cte_id = getattr(self._cte.ide, "Id", None) or getattr(self._cte.ide, "chave", None)
        if not cte_id:
            cte_id = "0" * 44

        if not str(cte_id).startswith("CTe"):
            cte_id = f"CTe{cte_id}"

        inf = ET.SubElement(root, "infCte", versao="4.00", Id=str(cte_id))

        ide = self._sub(inf, "ide")
        self._sub(ide, "cUF", self._cte.ide.cUF)
        self._sub(ide, "cCT", self._cte.ide.cCT)
        self._sub(ide, "CFOP", self._cte.ide.CFOP)
        self._sub(ide, "natOp", self._cte.ide.natOp)
        self._sub(ide, "mod", self._cte.ide.mod)
        self._sub(ide, "serie", self._cte.ide.serie)

        # nCT não pode ter zero à esquerda e deve ter 1..9 dígitos começando com 1..9
        nct_raw = str(self._cte.ide.nCT).strip()
        try:
            nct = str(int(nct_raw))  # remove zeros à esquerda
        except (TypeError, ValueError):
            raise ValueError(f"nCT inválido: {self._cte.ide.nCT!r}")

        if not nct.isdigit() or nct[0] == "0" or len(nct) > 9:
            raise ValueError(f"nCT fora do padrão (1..9 dígitos, sem zero à esquerda): {nct!r}")

        self._sub(ide, "nCT", nct)

        self._sub(ide, "dhEmi", self._cte.ide.dhEmi.strftime("%Y-%m-%dT%H:%M:%S-03:00"))
        self._sub(ide, "tpImp", self._cte.ide.tpImp)
        self._sub(ide, "tpEmis", self._cte.ide.tpEmis)
        self._sub(ide, "cDV", self._cte.ide.cDV)
        self._sub(ide, "tpAmb", self._cte.ide.tpAmb)
        self._sub(ide, "tpCTe", self._cte.ide.tpCTe)
        self._sub(ide, "procEmi", self._cte.ide.procEmi)
        self._sub(ide, "verProc", self._cte.ide.verProc)

        if getattr(self._cte.ide, "indGlobalizado", None) is not None:
            self._sub(ide, "indGlobalizado", self._cte.ide.indGlobalizado)

        self._sub(ide, "cMunEnv", self._cte.ide.cMunEnv)
        self._sub(ide, "xMunEnv", self._cte.ide.xMunEnv)
        self._sub(ide, "UFEnv", self._cte.ide.UFEnv)
        self._sub(ide, "modal", self._cte.ide.modal)
        self._sub(ide, "tpServ", self._cte.ide.tpServ)
        self._sub(ide, "cMunIni", self._cte.ide.cMunIni)
        self._sub(ide, "xMunIni", self._cte.ide.xMunIni)
        self._sub(ide, "UFIni", self._cte.ide.UFIni)
        self._sub(ide, "cMunFim", self._cte.ide.cMunFim)
        self._sub(ide, "xMunFim", self._cte.ide.xMunFim)
        self._sub(ide, "UFFim", self._cte.ide.UFFim)
        self._sub(ide, "retira", self._cte.ide.retira)

        if getattr(self._cte.ide, "xDetRetira", None):
            self._sub(ide, "xDetRetira", self._cte.ide.xDetRetira)

        self._sub(ide, "indIEToma", self._cte.ide.indIEToma or "9")

        toma3 = self._sub(ide, "toma3")
        self._sub(toma3, "toma", "0")

        emit = self._sub(inf, "emit")
        self._sub(emit, "CNPJ", self._cte.emit.CNPJ)

        if self._cte.emit.IE:
            self._sub(emit, "IE", self._cte.emit.IE)

        if self._cte.emit.IEST:
            self._sub(emit, "IEST", self._cte.emit.IEST)

        self._sub(emit, "xNome", self._cte.emit.xNome)

        if self._cte.emit.xFant:
            self._sub(emit, "xFant", self._cte.emit.xFant)

        self._address_emit(
            emit,
            self._cte.emit.enderEmit,
            getattr(self._cte.emit, "fone", None),
        )
        self._sub(emit, "CRT", self._cte.emit.CRT)

        self._parte(inf, "rem", self._cte.rem)

        if self._cte.exped:
            self._parte(inf, "exped", self._cte.exped)

        if self._cte.receb:
            self._parte(inf, "receb", self._cte.receb)

        self._parte(inf, "dest", self._cte.dest)

        vprest = self._sub(inf, "vPrest")
        self._sub(vprest, "vTPrest", f"{self._cte.vprest.vTPrest:.2f}")
        self._sub(vprest, "vRec", f"{self._cte.vprest.vRec:.2f}")

        for comp in self._cte.vprest.Comp:
            c = self._sub(vprest, "Comp")
            self._sub(c, "xNome", comp.xNome)
            self._sub(c, "vComp", f"{comp.vComp:.2f}")

        self._build_icms(inf)

        norm = self._sub(inf, "infCTeNorm")

        carga = self._sub(norm, "infCarga")
        self._sub(carga, "vCarga", f"{self._cte.infCarga.vCarga:.2f}")
        self._sub(carga, "proPred", self._cte.infCarga.proPred)

        if self._cte.infCarga.xOutCat:
            self._sub(carga, "xOutCat", self._cte.infCarga.xOutCat)

        for q in self._cte.infCarga.infQ:
            iq = self._sub(carga, "infQ")
            self._sub(iq, "cUnid", q.cUnid)
            self._sub(iq, "tpMed", q.tpMed)
            self._sub(iq, "qCarga", f"{q.qCarga:.4f}")

        if self._cte.infNFe:
            inf_doc = self._sub(norm, "infDoc")
            for nfe in self._cte.infNFe:
                n = self._sub(inf_doc, "infNFe")
                self._sub(n, "chave", nfe.chave)

                if nfe.pin:
                    self._sub(n, "PIN", nfe.pin)

                if nfe.dPrev:
                    self._sub(n, "dPrev", nfe.dPrev)

        if self._cte.modal_rodo:
            modal_el = self._sub(norm, "infModal")
            modal_el.set("versaoModal", "4.00")
            rodo = self._sub(modal_el, "rodo")
            self._sub(rodo, "RNTRC", self._cte.modal_rodo.RNTRC)

            if self._cte.modal_rodo.veic:
                v = self._sub(rodo, "veic")
                self._sub(v, "placa", self._cte.modal_rodo.veic.placa)

                if self._cte.modal_rodo.veic.RENAVAM:
                    self._sub(v, "RENAVAM", self._cte.modal_rodo.veic.RENAVAM)

                if self._cte.modal_rodo.veic.UF:
                    self._sub(v, "UF", self._cte.modal_rodo.veic.UF)

        inf_supl = self._sub(root, "infCTeSupl")
        chave_cte = inf.get("Id", "CTe00000000000000000000000000000000000000000000").replace("CTe", "")
        tp_amb = self._cte.ide.tpAmb
        qr_code = f"https://www.cte.fazenda.gov.br/portal/consultar?chCTe={chave_cte}&tpAmb={tp_amb}"
        self._sub(inf_supl, "qrCodCTe", qr_code)

        mock_signature = f"""
        <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
            <SignedInfo>
                <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
                <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
                <Reference URI="#{inf.get('Id')}">
                    <Transforms>
                        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                        <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
                    </Transforms>
                    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                    <DigestValue>TW9ja0Jhc2U2NA==</DigestValue>
                </Reference>
            </SignedInfo>
            <SignatureValue>TW9ja0Jhc2U2NA==</SignatureValue>
            <KeyInfo>
                <X509Data>
                    <X509Certificate>TW9ja0Jhc2U2NA==</X509Certificate>
                </X509Data>
            </KeyInfo>
        </Signature>
        """
        sig_el = ET.fromstring(mock_signature)
        root.append(sig_el) 
        if getattr(self._cte, "protocolo", None):
            cte_proc = ET.Element("cteProc", versao="4.00", xmlns=NS)
            cte_proc.append(root)

            prot_cte = ET.SubElement(cte_proc, "protCTe", versao="4.00")
            inf_prot = self._sub(prot_cte, "infProt")

            prot = self._cte.protocolo
            self._sub(inf_prot, "tpAmb", prot.tpAmb)
            self._sub(inf_prot, "verAplic", prot.verAplic)
            self._sub(inf_prot, "chCTe", prot.chCTe)
            self._sub(inf_prot, "dhRecbto", prot.dhRecbto)
            self._sub(inf_prot, "nProt", prot.nProt)
            self._sub(inf_prot, "digVal", prot.digVal)
            self._sub(inf_prot, "cStat", prot.cStat)
            self._sub(inf_prot, "xMotivo", prot.xMotivo)

            ET.indent(cte_proc, space="  ")
            return ET.tostring(cte_proc, encoding="unicode", xml_declaration=True)

        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)