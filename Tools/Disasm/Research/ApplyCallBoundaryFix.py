"""Удаление двух ложных границ полётного кода с сохранением всех существующих комментариев."""
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
from SourcePresentation import operation,instructions
import VerifySources
import AuditConformance


def load(root,name):
    return json.loads((root / "Tools/Disasm/Reports" / name).read_text(encoding="utf-8"))


def encode(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf-8")


def hashes():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("Source","Includes","Builder","Docs","Tools/Disasm/Reports")
            for p in (ROOT / folder).rglob("*") if p.is_file()}


def main():
    baseline = hashes()
    history = ROOT / "Tools/Disasm/Research/History/BeforeCallBoundaryFix"
    if history.exists():
        raise ValueError("Исправление границ уже переносилось")
    candidate = ROOT / "Tools/Disasm/Research/Candidates/TrackGeometryRelease2"
    functions = load(ROOT,"Functions.json")
    old = [f for f in functions if f["region"] == "Action" and f["name"] in ("UnknownC88C","UnknownCAB3","UnknownCAE3")]
    fresh = next(f for f in load(candidate,"Functions.json") if f["region"] == "Action" and f["name"] == "UnknownC88C")
    if len(old) != 3 or old[0]["offset"] != fresh["offset"] or old[-1]["end_offset"] != fresh["end_offset"]:
        raise ValueError("Не совпали границы объединяемых фрагментов")
    if any(f["semantic_status"] != "unknown" for f in old):
        raise ValueError("Объединение затрагивает доказанный контракт")
    symbol_map = {}
    symbols = load(ROOT,"Symbols.json")
    for function in old[1:]:
        prefix = "Action."+function["name"]+"."
        for key in symbols:
            if key.startswith(prefix):
                suffix = key[len(prefix):]
                symbol_map[key] = "Action.UnknownC88C."+(f"Point{function['address']:04X}" if suffix == "Entry" else suffix)
    pattern = re.compile(r"Action\.(?:UnknownCAB3|UnknownCAE3)\.[A-Za-z_][A-Za-z0-9_]*")

    def rename(text):
        text = pattern.sub(lambda m:symbol_map[m[0]],text)
        for function in old[1:]:
            text = text.replace(function["path"],old[0]["path"])
            text = text.replace("../Action/"+function["name"]+".asm","../Action/UnknownC88C.asm")
        return text

    parts = []
    expected_ops = []
    for index,function in enumerate(old):
        text = (ROOT / function["path"]).read_text(encoding="utf-8")
        expected_ops.extend(instructions(rename(text)))
        lines = []
        for line in text.splitlines():
            if operation(line).lower().startswith(("module ","endmodule")):
                continue
            if line.lstrip().startswith("; JP ") and any("продолжение в "+f["name"]+".asm" in line for f in old[1:]):
                continue
            if index and line.startswith("Entry:"):
                line = (f"Point{function['address']:04X}:").ljust(16)+line[16:]
            lines.append(line)
        if index:
            lines.insert(0,f"; прежняя физическая граница #{function['address']:04X}, вход CALL этого банка не установлен")
        parts.append(rename("\n".join(lines)).strip("\n"))
    text = "                module Action\n                module UnknownC88C\n"+"\n\n".join(parts)+"\n\n                endmodule\n                endmodule\n"
    text = text.replace(f"#688C..#{old[0]['end_offset']-1:04X}",f"#688C..#{fresh['end_offset']-1:04X}",1)
    if instructions(text) != expected_ops:
        raise ValueError("Объединение изменило инструкции")
    pending = {old[0]["path"]:text.encode("utf-8")}
    removed = {f["path"] for f in old[1:]}
    # Обновление только ссылок на два прежних внутренних пространства имён.
    for folder in ("Source","Docs"):
        for path in (ROOT / folder).rglob("*"):
            relative = path.relative_to(ROOT).as_posix()
            if not path.is_file() or path.suffix not in (".asm",".inc",".md") or relative in removed or relative in pending:
                continue
            before = path.read_text(encoding="utf-8")
            after = rename(before)
            if after != before:
                if path.suffix in (".asm",".inc"):
                    lines = []
                    for previous,line in zip(before.splitlines(),after.splitlines()):
                        if previous != line and ";" in line and not line.lstrip().startswith(";"):
                            code,comment = line.split(";",1)
                            if len(code.rstrip()) >= 80:
                                raise ValueError("Не помещается правый комментарий")
                            line = code.rstrip().ljust(80)+";"+comment
                        lines.append(line)
                    after = "\n".join(lines)+"\n"
                pending[relative] = after.encode("utf-8")
    merged_functions = [fresh if f is old[0] else f for f in functions if f not in old[1:]]
    source_map = load(ROOT,"SourceMap.json")
    ranges = [r for r in source_map if r["slot"] == 17 and 0x688C <= r["offset"] < 0x6EE3]
    new_range = next(r for r in load(candidate,"SourceMap.json") if r["slot"] == 17 and r["offset"] == 0x688C)
    if len(ranges) != 3 or sum(r["length"] for r in ranges) != new_range["length"]:
        raise ValueError("Не совпало физическое покрытие")
    merged_map = [new_range if r is ranges[0] else r for r in source_map if r not in ranges[1:]]
    for before,after in symbol_map.items():
        symbols[after] = symbols.pop(before)
    inventory = load(ROOT,"Inventory.json")
    inventory.update(fragments=len(merged_functions),unknown=sum(f["semantic_status"] == "unknown" for f in merged_functions),
                     ranges_by_kind=dict(Counter(r["kind"] for r in merged_map)))
    for name,value in (("Functions.json",merged_functions),("SourceMap.json",merged_map),("Symbols.json",symbols),("Inventory.json",inventory)):
        pending["Tools/Disasm/Reports/"+name] = encode(value)
    unit = next(u["path"] for u in load(ROOT,"BuildUnits.json") if u["slot"] == 17)
    text = (ROOT / unit).read_text(encoding="utf-8")
    fresh_text = (candidate / unit).read_text(encoding="utf-8")
    first,last = "                assert $ == #688C\n","                assert $ == #6EE3\n"
    pending[unit] = (text[:text.index(first)]+fresh_text[fresh_text.index(first):fresh_text.index(last)]+text[text.index(last):]).encode("utf-8")
    path = "Docs/Functions.md"
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    fresh_lines = (candidate / path).read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not any("../"+f["path"] in line for f in old[1:])]
    action = [f for f in merged_functions if f["region"] == "Action"]
    lines = [f'| Action | {len(action)} | {sum(f["semantic_status"] == "described" for f in action)} | [Факты](FunctionDetails/Action.md) |' if line.startswith("| Action |") else line for line in lines]
    pending[path] = ("\n".join(lines)+"\n").encode("utf-8")
    path = "Docs/FunctionDetails/Action.md"
    text = (ROOT / path).read_text(encoding="utf-8")
    fresh_text = (candidate / path).read_text(encoding="utf-8")
    first,last = "## UnknownC88C\n","## UnknownCF08\n"
    pending[path] = (text[:text.index(first)]+fresh_text[fresh_text.index(first):fresh_text.index(last)]+text[text.index(last):]).encode("utf-8")
    for path in ("Docs/ModifiedCode.md","Tools/Disasm/Reports/ModifiedCode.json"):
        pending[path] = rename((ROOT / path).read_text(encoding="utf-8")).encode("utf-8")
    review = create_candidate(ROOT,"Tools/Disasm/Research/Candidates/CallBoundaryMergeReview","documentation")
    for path,data in pending.items():
        target = review / path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    for path in removed:
        target = (review / path).resolve()
        if not target.is_relative_to(review / "Source"):
            raise ValueError("Удаление вне Source варианта")
        target.unlink()
    VerifySources.ROOT = review
    VerifySources.main()
    AuditConformance.ROOT = review
    audit = AuditConformance.audit()
    for field in ("unlinked_functions","missing_includes_or_resources","missing_include_order","unresolved_global_references",
                  "duplicate_global_definitions","global_reference_case_mismatches","source_files_outside_graph","python_duplicate_literal_keys"):
        if audit[field]:
            raise ValueError("Не прошла проверка " + field)
    if hashes() != baseline:
        raise ValueError("Рабочая копия изменилась во время подготовки")
    for path in set(pending)|removed:
        original = ROOT / path
        if original.exists():
            target = history / path
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,target)
    for path,data in pending.items():
        (ROOT / path).write_bytes(data)
    for path in removed:
        target = (ROOT / path).resolve()
        if not target.is_relative_to(ROOT / "Source"):
            raise ValueError("Архивируемый путь вне Source проекта")
        target.unlink()
    VerifySources.ROOT = ROOT
    VerifySources.main()
    AuditConformance.ROOT = ROOT
    (ROOT / "Tools/Disasm/Reports/ConformanceAudit.json").write_bytes(encode(AuditConformance.audit()))
    (ROOT / "Tools/Disasm/Reports/CallBoundaryVerification.json").write_bytes(encode(dict(
        passed=True,removed_false_boundaries=["Action:#CAB3","Action:#CAE3"],source_comments_preserved=True,
        instructions_changed=False,semantic_analysis_completed=False,assembly_executed=False)))


if __name__ == "__main__":
    main()
