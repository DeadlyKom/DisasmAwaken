"""Подготовка разбора чтения списков и восстановления границ в новой папке, без перезаписи исходников."""

from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from CandidateWorkspace import create_candidate


def fingerprint():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("Source", "Includes", "Builder", "Docs")
            for p in (ROOT / folder).rglob("*") if p.is_file()}


def main(relative):
    before = fingerprint()
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    raw = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    proof = json.loads((ROOT / "Tools/Disasm/Reports/InterfaceListsVerification.json").read_text(encoding="utf-8"))
    if not proof.get("passed") or proof.get("source_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("Модель не подтверждает текущие исходные байты")
    candidate = create_candidate(ROOT, relative, "source")
    import Analyze
    Analyze.ROOT = candidate
    Analyze.main()
    old = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    new = json.loads((candidate / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    old_code = {(r["name"], i["slot"], i["offset"]): i for r in old for i in r["instructions"]}
    new_code = {(r["name"], i["slot"], i["offset"]): i for r in new for i in r["instructions"]}
    if old_code.keys()-new_code.keys():
        raise ValueError("Анализ потерял старые инструкции")
    for key in new_code.keys()-old_code.keys():
        if key[0] != "Station" or key[1] != 4 or not (0x6B52 <= key[2] < 0x6BE0):
            raise ValueError("Новые инструкции вне области второго контура")
    import ExportSources
    ExportSources.ROOT = candidate
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
    import GenerateDocs
    GenerateDocs.ROOT = candidate
    GenerateDocs.main()
    if before != fingerprint():
        raise ValueError("Подготовка изменила исходники")
    path = candidate / "CandidateInfo.json"
    info = json.loads(path.read_text(encoding="utf-8"))
    info["bounds_release"] = True
    path.write_text(json.dumps(info, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(candidate=relative, passed=True, new_instructions=len(new_code.keys()-old_code.keys()),
                          unknown=audit["unknown_fragments"], source_unchanged=True, assembly_executed=False), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    main(parser.parse_args().output)
