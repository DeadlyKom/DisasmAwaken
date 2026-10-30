"""Точечный перенос трёх входов цепочки перерисовки без замены окружающих исходников."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
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


def fingerprint():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
            for p in (ROOT / folder).rglob("*") if p.is_file()}


def main():
    before_hashes = fingerprint()
    candidate = ROOT / "Tools/Disasm/Research/Candidates/RepaintChainRelease"
    history = ROOT / "Tools/Disasm/Research/History/BeforeRepaintChainRelease"
    if history.exists():
        raise ValueError("Выпуск уже перенесён")
    old_map, fresh_map = load(ROOT, "SourceMap.json"), load(candidate, "SourceMap.json")
    old_ranges = [r for r in old_map if r["slot"] == 4 and r["offset"] == 0x6BE0]
    if [(r["offset"], r["length"], r["kind"]) for r in old_ranges] != [(0x6BE0, 65, "unclassified")]:
        raise ValueError("Не совпал исходный диапазон цепочки")
    spans = [(r["offset"], r["offset"]+r["length"]) for r in old_ranges]
    inside = lambda r: r["slot"] == 4 and any(begin <= r["offset"] < end for begin, end in spans)
    new_ranges = [dict(r) for r in fresh_map if inside(r)]
    pending, resource_names = {}, {}
    for item in new_ranges:
        path = item["path"]
        if item["kind"] != "code":
            raise ValueError("Остался неклассифицированный участок цепочки")
        pending[item["path"]] = (candidate / path).read_bytes()
    merged_map = sorted([r for r in old_map if r not in old_ranges]+new_ranges, key=lambda r:(r["slot"], r["offset"]))
    functions = load(ROOT, "Functions.json")
    fresh_functions = load(candidate, "Functions.json")
    new_functions = [f for f in fresh_functions if inside(f)]
    if len(new_functions) != 3 or [f for f in fresh_functions if not inside(f)] != functions:
        raise ValueError("Изменены посторонние функции")
    region_order = {name:i for i,name in enumerate(dict.fromkeys(f["region"] for f in functions))}
    functions = sorted(functions+new_functions, key=lambda f:(region_order[f["region"]], f["slot"], f["offset"]))
    old_flow, fresh_flow = load(ROOT, "ControlFlow.json"), load(candidate, "ControlFlow.json")
    old_code = {(r["name"], i["slot"], i["offset"]):i for r in old_flow for i in r["instructions"]}
    new_code = {(r["name"], i["slot"], i["offset"]):i for r in fresh_flow for i in r["instructions"]}
    if any(new_code.get(key) != value for key,value in old_code.items()):
        raise ValueError("Изменены прежние инструкции")
    added = new_code.keys()-old_code.keys()
    if len(added) != 37 or any(name != "Station" or slot != 4 or not 0x6BE0 <= offset < 0x6C21 for name,slot,offset in added):
        raise ValueError("Новые инструкции вне цепочки")
    unit = "Source/Files/04_STATIONF.inc"
    text, fresh_text = (ROOT / unit).read_text(encoding="utf-8"), (candidate / unit).read_text(encoding="utf-8")
    for begin,end in spans:
        first, last = f"                assert $ == #{begin:04X}\n", f"                assert $ == #{end:04X}\n"
        chunk = fresh_text[fresh_text.index(first):fresh_text.index(last)]
        for previous,current in resource_names.items():
            chunk = chunk.replace(previous,current)
        text = text[:text.index(first)]+chunk+text[text.index(last):]
    pending[unit] = text.encode("utf-8")
    # Именование внешних вызовов трёх новых входов, исходные инструкции остаются эквивалентными.
    for path in (ROOT / "Source/Station").glob("*.asm"):
        before = path.read_text(encoding="utf-8")
        lines = []
        for line in before.splitlines():
            code,sep,comment = line.partition(";")
            changed = code
            for address,name in ((0xCBE0,"RepaintAndTrack"),(0xCBEB,"RepaintAndFlag"),(0xCBF2,"RepaintItemCore")):
                changed = re.sub(r"\b(CALL|JP|JR) (.*?)#"+f"{address:04X}"+r"\b", lambda m:m[1]+" "+m[2]+"@Station."+name+".Entry", changed)
            if changed != code:
                if sep and len(changed.rstrip()) >= 80:
                    raise ValueError("Не помещается правый комментарий")
                line = changed.rstrip().ljust(80)+";"+comment if sep else changed
            lines.append(line)
        after = "\n".join(lines)+"\n"
        if after != before:
            pending[path.relative_to(ROOT).as_posix()] = after.encode("utf-8")
    symbols = load(ROOT, "Symbols.json")
    symbols.update({k:v for k,v in load(candidate,"Symbols.json").items() if k.startswith(("Station.RepaintAndTrack.","Station.RepaintAndFlag.","Station.RepaintItemCore."))})
    inventory = load(ROOT,"Inventory.json")
    totals = Counter()
    for record in merged_map:
        totals[record["kind"]] += record["length"]
    inventory.update(fragments=len(functions), described=sum(f["semantic_status"] == "described" for f in functions),
                     unknown=sum(f["semantic_status"] == "unknown" for f in functions), instructions=sum(r["instruction_count"] for r in fresh_flow),
                     physical_bytes_by_kind=dict(totals), ranges_by_kind=dict(Counter(r["kind"] for r in merged_map)))
    for name,value in (("SourceMap.json",merged_map),("Functions.json",functions),("ControlFlow.json",fresh_flow),("Symbols.json",symbols),("Inventory.json",inventory)):
        pending["Tools/Disasm/Reports/"+name] = encode(value)
    pending["Docs/Functions.md"] = (candidate / "Docs/Functions.md").read_bytes()
    path = "Docs/FunctionDetails/Station.md"
    text, fresh = (ROOT / path).read_text(encoding="utf-8"), (candidate / path).read_text(encoding="utf-8")
    for name,next_name in (("RepaintAndTrack","ActivateInterfaceCallback"),):
        section = fresh[fresh.index("## "+name+"\n"):fresh.index("## "+next_name+"\n")]
        text = text.replace("## "+next_name+"\n",section+"## "+next_name+"\n")
    pending[path] = text.encode("utf-8")
    for path in ("Docs/ModifiedCode.md","Tools/Disasm/Reports/ModifiedCode.json"):
        pending[path] = (candidate / path).read_bytes()
    review = create_candidate(ROOT,"Tools/Disasm/Research/Candidates/RepaintChainMergeReview","documentation")
    for path,data in pending.items():
        target = review / path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    # Исключение только архивируемого 65-байтового ресурса после проверки границ пути.
    for old in old_ranges:
        path = (review / old["path"]).resolve()
        if not path.is_relative_to(review / "Source/Resources"):
            raise ValueError("Архивируемый ресурс вне Source/Resources")
        path.unlink()
    VerifySources.ROOT = review
    VerifySources.main()
    AuditConformance.ROOT = review
    audit = AuditConformance.audit()
    for field in ("unlinked_functions","missing_includes_or_resources","missing_include_order","unresolved_global_references",
                  "duplicate_global_definitions","global_reference_case_mismatches","source_files_outside_graph","python_duplicate_literal_keys"):
        if audit[field]:
            raise ValueError("Не прошла проверка " + field)
    if fingerprint() != before_hashes:
        raise ValueError("Рабочая копия изменилась во время подготовки")
    # Архивирование всех заменяемых файлов перед точечным переносом в локальную рабочую копию.
    for path in set(pending) | {r["path"] for r in old_ranges}:
        source_path = ROOT / path
        if source_path.exists():
            saved = history / path
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source_path,saved)
    for path,data in pending.items():
        target = ROOT / path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    for old in old_ranges:
        path = (ROOT / old["path"]).resolve()
        if not path.is_relative_to(ROOT / "Source/Resources"):
            raise ValueError("Архивируемый ресурс вне Source/Resources")
        path.unlink()
    VerifySources.ROOT = ROOT
    VerifySources.main()
    AuditConformance.ROOT = ROOT
    (ROOT / "Tools/Disasm/Reports/ConformanceAudit.json").write_bytes(encode(AuditConformance.audit()))
    (ROOT / "Tools/Disasm/Reports/RepaintChainReleaseVerification.json").write_bytes(encode(
        dict(passed=True, added_instructions=37, code_bytes=65, callee_contract_stubs=True, assembly_executed=False)))


if __name__ == "__main__":
    main()
