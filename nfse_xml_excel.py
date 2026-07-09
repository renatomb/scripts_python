#!/usr/bin/env python3
"""Gera relatório Excel (.xlsx) a partir de XMLs de NFS-e no padrão nacional.

Campos extraídos:
- dhEmi: data/hora de emissão (dentro de DPS/infDPS)
- nNFSe: número da NFS-e
- vLiq: valor líquido da NFS-e
- toma/CNPJ: CNPJ do cliente/tomador
- toma/xNome: nome do cliente/tomador

Uso:
  python3 ~/.hermes/scripts/nfse_xml_excel.py /home/hermes/arquivos-xml
  python3 ~/.hermes/scripts/nfse_xml_excel.py /home/hermes/arquivos-xml -o /tmp/relatorio.xlsx
"""
from __future__ import annotations

import argparse
import html
import sys
import zipfile
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

COLUMNS = [
    "Data e hora de emissao",
    "Numero da nfse",
    "Valor da nfse",
    "CNPJ do tomador",
    "Nome do tomador",
]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def first_child_text(parent: ET.Element | None, child_name: str) -> str:
    if parent is None:
        return ""
    for child in list(parent):
        if local_name(child.tag) == child_name and child.text is not None:
            return child.text.strip()
    return ""


def first_desc_text(root: ET.Element, name: str) -> str:
    for elem in root.iter():
        if local_name(elem.tag) == name and elem.text is not None:
            return elem.text.strip()
    return ""


def first_desc(root: ET.Element, name: str) -> ET.Element | None:
    for elem in root.iter():
        if local_name(elem.tag) == name:
            return elem
    return None


def parse_nfse_xml(path: Path) -> dict[str, object]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"XML inválido: {exc}") from exc

    toma = first_desc(root, "toma")
    dh_emi = first_desc_text(root, "dhEmi")
    n_nfse = first_desc_text(root, "nNFSe")
    v_liq_text = first_desc_text(root, "vLiq")
    cnpj_toma = first_child_text(toma, "CNPJ")
    nome_toma = first_child_text(toma, "xNome")

    try:
        v_liq: float | str = float(v_liq_text.replace(",", ".")) if v_liq_text else ""
    except ValueError:
        v_liq = v_liq_text

    return {
        COLUMNS[0]: dh_emi,
        COLUMNS[1]: int(n_nfse) if n_nfse.isdigit() else n_nfse,
        COLUMNS[2]: v_liq,
        COLUMNS[3]: cnpj_toma,
        COLUMNS[4]: nome_toma,
        "arquivo": str(path),
    }


def col_letters(idx: int) -> str:
    letters = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def cell_xml(row: int, col: int, value: object) -> str:
    ref = f"{col_letters(col)}{row}"
    if value is None or value == "":
        return f'<c r="{ref}"/>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    escaped = html.escape(str(value), quote=False)
    return f'<c r="{ref}" t="inlineStr"><is><t>{escaped}</t></is></c>'


def write_xlsx(rows: list[dict[str, object]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    all_rows = [COLUMNS] + [[row.get(col, "") for col in COLUMNS] for row in rows]
    sheet_rows = []
    for r_idx, values in enumerate(all_rows, 1):
        cells = "".join(cell_xml(r_idx, c_idx, value) for c_idx, value in enumerate(values, 1))
        sheet_rows.append(f'<row r="{r_idx}">{cells}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<cols><col min="1" max="1" width="25" customWidth="1"/><col min="2" max="2" width="20" customWidth="1"/>'
        '<col min="3" max="3" width="18" customWidth="1"/><col min="4" max="4" width="24" customWidth="1"/>'
        '<col min="5" max="5" width="45" customWidth="1"/></cols>'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        '</worksheet>'
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="NFS-e" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    wb_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera relatório Excel de XMLs NFS-e.")
    parser.add_argument("input_dir", nargs="?", default="/home/hermes/arquivos-xml", help="Diretório contendo XMLs")
    parser.add_argument("-o", "--output", help="Caminho do .xlsx de saída")
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir).expanduser().resolve()
    if not input_dir.is_dir():
        print(f"ERRO: diretório não encontrado: {input_dir}", file=sys.stderr)
        return 2

    xml_files = sorted(input_dir.glob("*.xml"))
    if not xml_files:
        print(f"ERRO: nenhum .xml encontrado em {input_dir}", file=sys.stderr)
        return 2

    rows: list[dict[str, object]] = []
    errors: list[str] = []
    for path in xml_files:
        try:
            rows.append(parse_nfse_xml(path))
        except Exception as exc:  # noqa: BLE001 - CLI deve reportar e seguir
            errors.append(f"{path.name}: {exc}")

    rows.sort(key=lambda row: (str(row.get(COLUMNS[0], "")), str(row.get(COLUMNS[1], ""))))
    if args.output:
        out_path = Path(args.output).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = input_dir / f"relatorio-nfse-{stamp}.xlsx"

    write_xlsx(rows, out_path)
    print(f"Relatório gerado: {out_path}")
    print(f"XMLs lidos com sucesso: {len(rows)}")
    if errors:
        print(f"XMLs com erro: {len(errors)}", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
