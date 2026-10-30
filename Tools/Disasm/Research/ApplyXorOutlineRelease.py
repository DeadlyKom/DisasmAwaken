"""Перенос трёх подтверждённых процедур временного XOR-контура из бинарной области в исходный код."""

from pathlib import Path
from collections import Counter
import json
import hashlib
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(Path(__file__).resolve().parent)]
from CandidateWorkspace import create_candidate
import VerifySources
import AuditConformance


def load(root, name):
    return json.loads((root / "Tools/Disasm/Reports" / name).read_text(encoding="utf-8"))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+"\n").encode("utf-8")


def main():
    before_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for folder in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
                     for p in (ROOT / folder).rglob("*") if p.is_file()}
    candidate = ROOT / "Tools/Disasm/Research/Candidates/XorOutlineRelease"
    history = ROOT / "Tools/Disasm/Research/History/BeforeXorOutlineRelease"
    if history.exists():
        raise ValueError("Вход уже перенесён")
    old_map, new_map = load(ROOT, "SourceMap.json"), load(candidate, "SourceMap.json")
    before = next(r for r in old_map if r["slot"] == 4 and r["offset"] == 0x64BE)
    after = [r for r in new_map if r["slot"] == 4 and 0x64BE <= r["offset"] < 0x6626]
    if before["kind"] != "unclassified" or before["length"] != 360 or len(after) != 3 or any(r["kind"] != "code" for r in after):
        raise ValueError("Не совпал физический участок продолжения и геометрии")
    merged_map = [item for r in old_map for item in (after if r is before else [r])]
    functions = load(ROOT, "Functions.json")
    new_functions = [f for f in load(candidate, "Functions.json") if f["region"] == "Station" and 0xC4BE <= f["address"] < 0xC626]
    previous = next(f for f in functions if f["region"] == "Station" and f["address"] == 0xC436)
    where = functions.index(previous)+1
    functions[where:where] = new_functions
    pending = {f["path"]: (candidate / f["path"]).read_bytes() for f in new_functions}
    unit = "Source/Files/04_STATIONF.inc"
    text = (ROOT / unit).read_text(encoding="utf-8")
    fresh_text = (candidate / unit).read_text(encoding="utf-8")
    first, last = "                assert $ == #64BE\n", "                assert $ == #6626\n"
    pending[unit] = (text[:text.index(first)]+fresh_text[fresh_text.index(first):fresh_text.index(last)]+text[text.index(last):]).encode("utf-8")
    old_flow, new_flow = load(ROOT, "ControlFlow.json"), load(candidate, "ControlFlow.json")
    old_code = {(r["name"], i["slot"], i["offset"]): i for r in old_flow for i in r["instructions"]}
    new_code = {(r["name"], i["slot"], i["offset"]): i for r in new_flow for i in r["instructions"]}
    if any(new_code.get(k) != v for k, v in old_code.items()):
        raise ValueError("Анализ изменил прежние инструкции")
    added = new_code.keys()-old_code.keys()
    if len(added) != 302 or any(name != "Station" or slot != 4 or not 0x64BE <= offset < 0x6626 for name, slot, offset in added):
        raise ValueError("Анализ затронул посторонние инструкции")
    symbols = load(ROOT, "Symbols.json")
    symbols.update({k: v for k, v in load(candidate, "Symbols.json").items() if k.startswith(("Station.XorRectOutline.", "Station.XorOutlineRow.", "Station.XorOutlineColumn."))})
    inventory = load(ROOT, "Inventory.json")
    totals = Counter()
    for item in merged_map:
        totals[item["kind"]] += item["length"]
    inventory.update(fragments=len(functions), described=sum(f["semantic_status"] == "described" for f in functions),
                     unknown=sum(f["semantic_status"] == "unknown" for f in functions),
                     instructions=sum(r["instruction_count"] for r in new_flow),
                     physical_bytes_by_kind=dict(totals), ranges_by_kind=dict(Counter(r["kind"] for r in merged_map)))
    for name, value in (("SourceMap.json", merged_map), ("Functions.json", functions),
                        ("ControlFlow.json", new_flow), ("Symbols.json", symbols), ("Inventory.json", inventory)):
        pending["Tools/Disasm/Reports/"+name] = encode(value)
    # Обновление производного реестра по текущим именам и вставка только двух новых разделов подробностей.
    pending["Docs/Functions.md"] = (candidate / "Docs/Functions.md").read_bytes()
    path = "Docs/FunctionDetails/Station.md"
    text = (ROOT / path).read_text(encoding="utf-8")
    fresh = (candidate / path).read_text(encoding="utf-8")
    section = fresh[fresh.index("## XorRectOutline\n"):fresh.index("## FillRectangle\n")]
    pending[path] = text.replace("## FillRectangle\n", section+"## FillRectangle\n").encode("utf-8")
    for path in ("Docs/ModifiedCode.md", "Tools/Disasm/Reports/ModifiedCode.json"):
        pending[path] = (candidate / path).read_bytes()
    review = create_candidate(ROOT, "Tools/Disasm/Research/Candidates/XorOutlineMergeReview", "documentation")
    for path, data in pending.items():
        target = review / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    target = (review / before["path"]).resolve()
    if not target.is_relative_to(review / "Source"):
        raise ValueError("Удаление дубликата вне Source варианта")
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
    current_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for folder in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
                      for p in (ROOT / folder).rglob("*") if p.is_file()}
    if current_hashes != before_hashes:
        raise ValueError("Рабочая копия изменилась во время подготовки переноса")
    # Сохранение всех заменяемых файлов, исходный 360-байтовый бинарник архивируется без потери.
    for path in set(pending) | {before["path"]}:
        source = ROOT / path
        if source.exists():
            saved = history / path
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, saved)
    for path, data in pending.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    target = (ROOT / before["path"]).resolve()
    if not target.is_relative_to(ROOT / "Source"):
        raise ValueError("Архивируемый путь вне Source проекта")
    target.unlink()
    VerifySources.ROOT = ROOT
    VerifySources.main()
    AuditConformance.ROOT = ROOT
    audit = AuditConformance.audit()
    (ROOT / "Tools/Disasm/Reports/ConformanceAudit.json").write_bytes(encode(audit))
    (ROOT / "Tools/Disasm/Reports/XorOutlineReleaseVerification.json").write_bytes(encode(
        dict(passed=True, added_instructions=302, code_bytes=360, original_bytes_preserved=True, assembly_executed=False)))


if __name__ == "__main__":
    main()
