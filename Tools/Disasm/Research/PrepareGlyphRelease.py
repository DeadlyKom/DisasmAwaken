"""Выпуск разбора глифов только в новом кандидате, без замены ручных исходников."""

from pathlib import Path
import argparse
import hashlib
import json
import sys
import re

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from CandidateWorkspace import create_candidate
from GlyphFacts import FUNCTIONS, CONTRACTS, LABELS, COMMENTS, DOCUMENTS, verify_table, name_operands


def line(label, operation, comment):
    if len(label) >= 16:
        raise ValueError("Имя не помещается перед столбцом кода " + label)
    return (label.ljust(16) + operation).ljust(80) + "; " + comment


def append_before_endif(path, lines):
    text = path.read_text(encoding="utf-8")
    marker = "                endif"
    position = text.rindex(marker)
    path.write_text(text[:position] + "\n".join(lines) + "\n\n" + text[position:], encoding="utf-8")


def source_fingerprint():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("Source", "Includes", "Builder", "Docs")
            for p in (ROOT / folder).rglob("*") if p.is_file()}


def main(relative):
    if re.search(r"\bstruct\s+FGlyphRoute\b", (ROOT / "Includes/Structs/Include.inc").read_text(encoding="utf-8"), re.I):
        raise ValueError("Разбор глифов уже интегрирован, для нового снимка используйте ExportSources.py")
    before = source_fingerprint()
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    raw = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    verify_table(raw)
    for filename in ("GlyphRenderVerification.json", "TextRowVerification.json"):
        proof = json.loads((ROOT / "Tools/Disasm/Reports" / filename).read_text(encoding="utf-8"))
        if not proof.get("passed") or proof.get("source_sha256") != hashlib.sha256(raw).hexdigest():
            raise ValueError("Нет подтверждения текущих исходных байтов " + filename)
    candidate = create_candidate(ROOT, relative, "source")
    append_before_endif(candidate / "Includes/Structs/Include.inc", [
        "; -----------------------------------------",
        "; исходная запись двух этапов рисования глифа",
        "; -----------------------------------------",
        "                struct FGlyphRoute",
        line("First", "dw #0000", "цель первого участка, до границы знакоместа либо все восемь строк"),
        line("AfterWrap", "dw #0000", "цель оставшихся строк после перехода, ноль для Y кратного восьми"),
        "                ends",
        "                assert FGlyphRoute == #04",
        "",
        "; -----------------------------------------",
        "; физический кадр CPU-стека DrawGlyph, создаётся последовательностью PUSH",
        "; порядок полей соответствует POP общего выхода, адрес возврата находится последним",
        "; -----------------------------------------",
        "                struct FGlyphFrame",
        *[line(name, "dw #0000", description) for name, description in (
            ("SavedAFAlt", "исходный альтернативный AF"),
            ("SavedHLAlt", "исходный альтернативный HL"),
            ("SavedBCAlt", "исходный альтернативный BC"),
            ("SavedDEAlt", "исходный альтернативный DE"),
            ("SavedHL", "исходный основной HL"),
            ("SavedBC", "исходный основной BC"),
            ("SavedDE", "исходный основной DE"),
            ("ReturnAddress", "адрес возврата исходного вызова DrawGlyph"),
        )],
        "                ends",
        "                assert FGlyphFrame == #10",
    ])
    append_before_endif(candidate / "Includes/Variables/Include.inc", [
        "                module GlyphState",
        line("DispatchTarget", "equ #AF0A", "слово цели изменяемого JP первого и второго участка глифа"),
        line("KernelPrefix", "equ #AED5", "три изменяемых байта начала пиксельной части, либо JP успешного выхода"),
        "                endmodule",
    ])
    path = candidate / "Includes/Const/Include.inc"
    text = path.read_text(encoding="utf-8")
    text = text.replace("                module FontConst", "\n".join([
        "                module FontConst",
        line("RouteHalfPage", "equ #49", "старшая часть половинного адреса таблицы #9200 перед ADD HL,HL"),
        line("GlyphTopLimit", "equ #B9", "первая недопустимая верхняя строка восьмипиксельного глифа"),
    ]))
    text = text.replace("                module ScreenConst", "\n".join([
        "                module ScreenConst",
        line("PixelOffsetMask", "equ #07", "младшие три бита пиксельной координаты внутри знакоместа"),
        line("ColumnMask", "equ #1F", "младшие пять битов колонки в экранном адресе"),
    ]))
    path.write_text(text, encoding="utf-8")
    # Подстановка подтверждённых метаданных только в память процесса выпуска кандидата.
    import Knowledge
    import Contracts
    import SemanticNames
    import StationNotes
    Knowledge.FUNCTIONS["Station"].update(FUNCTIONS)
    Contracts.CONTRACTS.update(CONTRACTS)
    SemanticNames.LABELS.update(LABELS)
    SemanticNames.DOCUMENTS.update(DOCUMENTS)
    StationNotes.COMMENTS.update(COMMENTS)
    import Analyze
    Analyze.ROOT = candidate
    Analyze.main()
    old = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    new = json.loads((candidate / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    old_code = {(r["name"], i["slot"], i["offset"]): i for r in old for i in r["instructions"]}
    new_code = {(r["name"], i["slot"], i["offset"]): i for r in new for i in r["instructions"]}
    if old_code.keys() - new_code.keys():
        raise ValueError("Анализ удалил старые инструкции")
    for key in new_code.keys() - old_code.keys():
        item = new_code[key]
        if key[0] != "Station" or item["slot"] != 4 or not 0xAE55 <= item["address"] < 0xBBBE:
            raise ValueError("Расширение кода вышло за область глифов")
    import ExportSources
    ExportSources.ROOT = candidate
    previous_naming = ExportSources.name_operands
    ExportSources.name_operands = lambda region, address, operation: name_operands(
        region, address, previous_naming(region, address, operation))
    ExportSources.main()
    import VerifySources
    VerifySources.ROOT = candidate
    VerifySources.main()
    import AuditConformance
    AuditConformance.ROOT = candidate
    audit = AuditConformance.audit()
    for field in ("missing_includes_or_resources", "unresolved_global_references",
                  "duplicate_global_definitions", "global_reference_case_mismatches", "source_files_outside_graph"):
        if audit[field]:
            raise ValueError("Не прошёл аудит кандидата " + field)
    if before != source_fingerprint():
        raise ValueError("Выпуск изменил текущие исходники")
    info_path = candidate / "CandidateInfo.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    info.update(glyph_release=True, current_sources_overwritten=False)
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    report = dict(method="verified_glyph_release_in_isolated_candidate", passed=True,
                  candidate=candidate.relative_to(ROOT).as_posix(),
                  new_instruction_count=len(new_code.keys()-old_code.keys()),
                  functions=audit["registered_functions"], unknown=audit["unknown_fragments"],
                  contracts_pending=audit["unknown_contract_fragments"],
                  source_unchanged=True, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/GlyphReleaseCandidate.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    main(parser.parse_args().output)
