"""Перенос одного подтверждённого 14-байтового входа из бинарной области в исходный код."""

from pathlib import Path
from collections import Counter
import json
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
    candidate = ROOT / "Tools/Disasm/Research/Candidates/InterfaceStateRelease"
    history = ROOT / "Tools/Disasm/Research/History/BeforeFrameBitRelease"
    if history.exists():
        raise ValueError("Вход уже перенесён")
    old_map, new_map = load(ROOT, "SourceMap.json"), load(candidate, "SourceMap.json")
    before = next(r for r in old_map if r["slot"] == 4 and r["offset"] == 0x3E97)
    after = next(r for r in new_map if r["slot"] == 4 and r["offset"] == 0x3E97)
    if (before["kind"], after["kind"], before["length"], after["length"]) != ("unclassified", "code", 14, 14):
        raise ValueError("Не совпал физический участок чтения контура")
    merged_map = [after if r is before else r for r in old_map]
    functions = load(ROOT, "Functions.json")
    function = next(f for f in load(candidate, "Functions.json") if f["region"] == "Station" and f["address"] == 0x9E97)
    previous = next(f for f in functions if f["region"] == "Station" and f["address"] == 0x9E77)
    functions.insert(functions.index(previous)+1, function)
    pending = {function["path"]: (candidate / function["path"]).read_bytes()}
    unit = "Source/Files/04_STATIONF.inc"
    text = (ROOT / unit).read_text(encoding="utf-8")
    fresh_text = (candidate / unit).read_text(encoding="utf-8")
    first, last = "                assert $ == #3E97\n", "                assert $ == #3EA5\n"
    pending[unit] = (text[:text.index(first)]+fresh_text[fresh_text.index(first):fresh_text.index(last)]+text[text.index(last):]).encode("utf-8")
    old_flow, new_flow = load(ROOT, "ControlFlow.json"), load(candidate, "ControlFlow.json")
    old_code = {(r["name"], i["slot"], i["offset"]): i for r in old_flow for i in r["instructions"]}
    new_code = {(r["name"], i["slot"], i["offset"]): i for r in new_flow for i in r["instructions"]}
    if any(new_code.get(k) != v for k, v in old_code.items()):
        raise ValueError("Анализ изменил прежние инструкции")
    added = new_code.keys()-old_code.keys()
    if len(added) != 11 or any(name != "Station" or slot != 4 or not 0x3E97 <= offset < 0x3EA5 for name, slot, offset in added):
        raise ValueError("Анализ затронул посторонние инструкции")
    symbols = load(ROOT, "Symbols.json")
    symbols.update({k: v for k, v in load(candidate, "Symbols.json").items() if k.startswith("Station.GetItemFrameBit.")})
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
    # Дополнение только одной строки и одного раздела документации, остальной текст сохраняется.
    path = "Docs/Functions.md"
    text = (ROOT / path).read_text(encoding="utf-8")
    lines = text.splitlines()
    where = next(i for i, s in enumerate(lines) if s.startswith("| #9E77 |"))
    fresh = (candidate / path).read_text(encoding="utf-8").splitlines()
    lines.insert(where+1, next(s for s in fresh if s.startswith("| #9E97 |")))
    station = [f for f in functions if f["region"] == "Station"]
    lines = [f'| Station | {len(station)} | {sum(f["semantic_status"] == "described" for f in station)} | [Факты](FunctionDetails/Station.md) |'
             if s.startswith("| Station |") else s for s in lines]
    pending[path] = ("\n".join(lines)+"\n").encode("utf-8")
    path = "Docs/FunctionDetails/Station.md"
    text = (ROOT / path).read_text(encoding="utf-8")
    fresh = (candidate / path).read_text(encoding="utf-8")
    section = fresh[fresh.index("## GetItemFrameBit\n"):fresh.index("## ToggleItemFrame\n")]
    pending[path] = text.replace("## ToggleItemFrame\n", section+"## ToggleItemFrame\n").encode("utf-8")
    review = create_candidate(ROOT, "Tools/Disasm/Research/Candidates/FrameBitMergeReview", "documentation")
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
    # Сохранение всех заменяемых файлов, исходный 14-байтовый бинарник архивируется без потери.
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
    (ROOT / "Tools/Disasm/Reports/FrameBitReleaseVerification.json").write_bytes(encode(
        dict(passed=True, added_instructions=11, code_bytes=14, original_bytes_preserved=True, assembly_executed=False)))


if __name__ == "__main__":
    main()
