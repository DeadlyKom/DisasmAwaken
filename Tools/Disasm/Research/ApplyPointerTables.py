"""Точечный перенос двух физических таблиц указателя после проверки отдельного варианта."""

from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(Path(__file__).resolve().parent)]
from CandidateWorkspace import create_candidate
from PointerTables import SPRITES, BACKGROUND
import VerifySources
import AuditConformance


def load(root, name):
    return json.loads((root / "Tools/Disasm/Reports" / name).read_text(encoding="utf-8"))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+"\n").encode("utf-8")


def fingerprint():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for directory in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
            for p in (ROOT / directory).rglob("*") if p.is_file()}


def main():
    candidate = ROOT / "Tools/Disasm/Research/Candidates/PointerTypedRelease"
    history = ROOT / "Tools/Disasm/Research/History/BeforePointerDataMerge"
    if history.exists():
        raise ValueError("Таблицы уже переносились")
    before = fingerprint()
    old = load(ROOT, "SourceMap.json")
    fresh = load(candidate, "SourceMap.json")
    old_ranges = [r for r in old if r["slot"] == 4 and r["offset"] in (0, 0x821)]
    new_ranges = [dict(r) for r in fresh if r["slot"] == 4 and r["offset"] in (0, 0x821, 0x831)]
    if [(r["offset"], r["length"], r["kind"]) for r in old_ranges] != [(0, 768, "unclassified"), (0x821, 25, "unclassified")]:
        raise ValueError("Не совпали исходные физические границы указателя")
    if [(r["offset"], r["length"], r["kind"]) for r in new_ranges] != [(0, 768, "typed_data"), (0x821, 16, "typed_data"), (0x831, 9, "unclassified")]:
        raise ValueError("Не совпали новые физические границы указателя")
    pending = {path: (candidate / path).read_bytes() for path in (SPRITES, BACKGROUND)}
    tail = new_ranges[-1]
    candidate_tail_path = tail["path"]
    tail["path"] = old_ranges[-1]["path"]
    pending[tail["path"]] = (candidate / candidate_tail_path).read_bytes()
    # Замена только двух участков включений, остальные ручные изменения сохраняются.
    unit = "Source/Files/04_STATIONF.inc"
    text = (ROOT / unit).read_text(encoding="utf-8")
    fresh_text = (candidate / unit).read_text(encoding="utf-8")
    for begin, end in ((0, 0x300), (0x821, 0x83A)):
        first, last = f"                assert $ == #{begin:04X}\n", f"                assert $ == #{end:04X}\n"
        chunk = fresh_text[fresh_text.index(first):fresh_text.index(last)]
        chunk = chunk.replace(candidate_tail_path[7:], tail["path"][7:])
        text = text[:text.index(first)]+chunk+text[text.index(last):]
    pending[unit] = text.encode("utf-8")
    merged = sorted([r for r in old if r not in old_ranges]+new_ranges, key=lambda r: (r["slot"], r["offset"]))
    pending["Tools/Disasm/Reports/SourceMap.json"] = encode(merged)
    symbols = load(ROOT, "Symbols.json")
    symbols.update({k: v for k, v in load(candidate, "Symbols.json").items()
                    if k.startswith(("PointerSprites.", "PointerBackground."))})
    pending["Tools/Disasm/Reports/Symbols.json"] = encode(symbols)
    pending["Tools/Disasm/Reports/PointerRows.json"] = (candidate / "Tools/Disasm/Reports/PointerRows.json").read_bytes()
    inventory = load(ROOT, "Inventory.json")
    totals = Counter()
    for record in merged:
        totals[record["kind"]] += record["length"]
    inventory["physical_bytes_by_kind"] = dict(totals)
    inventory["ranges_by_kind"] = dict(Counter(r["kind"] for r in merged))
    pending["Tools/Disasm/Reports/Inventory.json"] = encode(inventory)
    deletions = {old_ranges[0]["path"]}
    review = create_candidate(ROOT, "Tools/Disasm/Research/Candidates/PointerDataMergeReview", "documentation")
    for path, data in pending.items():
        target = review / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    # Удаление только дублирующего исходного бинарника, проверка границы Source перед операцией.
    for path in deletions:
        target = (review / path).resolve()
        if not target.is_relative_to(review / "Source"):
            raise ValueError("Архивируемый путь вне Source варианта")
        target.unlink()
    VerifySources.ROOT = review
    VerifySources.main()
    AuditConformance.ROOT = review
    audit = AuditConformance.audit()
    for key in ("unlinked_functions", "missing_includes_or_resources", "missing_include_order",
                "unresolved_global_references", "duplicate_global_definitions", "global_reference_case_mismatches",
                "source_files_outside_graph", "python_duplicate_literal_keys"):
        if audit[key]:
            raise ValueError("Не прошла проверка объединения " + key)
    if fingerprint() != before:
        raise ValueError("Рабочая копия изменилась во время проверки")
    # Сохранение каждого заменяемого файла, включая полный старый бинарник фона и его неизвестный хвост.
    for path in set(pending) | deletions:
        source = ROOT / path
        if source.exists():
            saved = history / path
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, saved)
    for path, data in pending.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for path in deletions:
        target = (ROOT / path).resolve()
        if not target.is_relative_to(ROOT / "Source"):
            raise ValueError("Архивируемый путь вне Source проекта")
        target.unlink()
    VerifySources.ROOT = ROOT
    VerifySources.main()
    AuditConformance.ROOT = ROOT
    audit = AuditConformance.audit()
    (ROOT / "Tools/Disasm/Reports/ConformanceAudit.json").write_bytes(encode(audit))
    report = dict(passed=True, typed_bytes=784, raster_records=192, background_records=8,
                  preserved_unknown_tail=9, candidate=candidate.relative_to(ROOT).as_posix(),
                  review=review.relative_to(ROOT).as_posix(), current_instructions_unchanged=True,
                  assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/PointerTablesVerification.json").write_bytes(encode(report))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
