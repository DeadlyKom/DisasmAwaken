"""Перенос клавиатуры, джойстика и направлений с сохранением неизвестных байтов до и после привязок клавиш."""

from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from CandidateWorkspace import create_candidate, require_candidate
import VerifySources
import AuditConformance

INTERVALS = ((0x8E4, 0x984), (0x994, 0xA0E), (0xA0F, 0xA1D), (0x3400, 0x3A58))


def load(root, name):
    return json.loads((root / "Tools/Disasm/Reports" / name).read_text(encoding="utf-8"))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+"\n").encode("utf-8")


def fingerprint():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
            for p in (ROOT / folder).rglob("*") if p.is_file()}


def inside(item):
    return item["slot"] == 4 and any(begin <= item["offset"] < end for begin, end in INTERVALS)


def main(relative, review_relative):
    candidate = (ROOT / relative).resolve()
    require_candidate(ROOT, candidate)
    if not json.loads((candidate / "CandidateInfo.json").read_text(encoding="utf-8")).get("pointer_input_release"):
        raise ValueError("Требуется проверенный выпуск клавиатуры и направлений")
    history = ROOT / "Tools/Disasm/Research/History/BeforePointerInputRelease"
    if history.exists():
        raise ValueError("Разбор уже переносился")
    VerifySources.main()
    original_hashes = fingerprint()
    old_functions, fresh_functions = load(ROOT, "Functions.json"), load(candidate, "Functions.json")
    old_local, new_local = [f for f in old_functions if inside(f)], [f for f in fresh_functions if inside(f)]
    if len(old_local) != 2 or len(new_local) != 12 or sum(f["semantic_status"] == "unknown" for f in old_local) != 2:
        raise ValueError("Не совпали границы неизвестных фрагментов клавиатуры и направлений")
    old_outer = [f for f in old_functions if not inside(f)]
    fresh_outer = [f for f in fresh_functions if not inside(f)]
    if old_outer != fresh_outer:
        raise ValueError("Выпуск изменил функции за пределами интерактивной геометрии")
    old_map, fresh_map = load(ROOT, "SourceMap.json"), load(candidate, "SourceMap.json")
    old_ranges, new_ranges = [r for r in old_map if inside(r)], [dict(r) for r in fresh_map if inside(r)]
    for record in (*old_ranges, *new_ranges):
        if not any(begin <= record['offset'] and record['offset']+record['length'] <= end for begin, end in INTERVALS):
            raise ValueError('Диапазон пересёк посторонние байты')
    merged_map = sorted([r for r in old_map if not inside(r)] + new_ranges, key=lambda r: (r['slot'], r['offset']))
    region_order = {name: index for index, name in enumerate(dict.fromkeys(f['region'] for f in old_functions))}
    key = lambda f: (region_order[f['region']], f['slot'], f['offset'])
    if old_functions != sorted(old_functions, key=key):
        raise ValueError('Старый порядок функций требует отдельного разбора')
    merged_functions = sorted(old_outer+new_local, key=key)
    pending = {}
    deletions = set()
    # Подготовка полного цикла и пяти общих выходов без нового размещения памяти.
    raw_tail = None
    resource_renames = {}
    for record in new_ranges:
        original_path = record['path']
        if record['kind'] == 'unclassified':
            old = next(r for r in old_ranges if r['offset'] <= record['offset'] < r['offset']+r['length'])
            if old['kind'] != 'unclassified':
                raise ValueError('Преобразование прежнего кода в неизвестные байты запрещено')
            record['path'] = old['path'] if record['offset'] == old['offset'] else old['path'][:-4]+'AfterKeys.bin'
            old_data = (ROOT / old['path']).read_bytes()
            begin = record['offset']-old['offset']
            if old_data[begin:begin+record['length']] != (candidate / original_path).read_bytes():
                raise ValueError('Изменились байты сохранённого префикса или хвоста')
            resource_renames[original_path] = record['path']
        elif record['kind'] not in ('code','typed_data'):
            raise ValueError('Неожиданная классификация клавиатуры и направлений')
        elif (ROOT / original_path).exists():
            raise ValueError('Новый исходник уже существует '+original_path)
        pending[record['path']] = (candidate / original_path).read_bytes()
    merged_map = sorted([r for r in old_map if not inside(r)] + new_ranges, key=lambda r: (r['slot'],r['offset']))
    deletions = {r['path'] for r in old_ranges} - {r['path'] for r in new_ranges}
    # Включения вне двух известных физических участков сохраняются буквально.
    unit = "Source/Files/04_STATIONF.inc"
    text = (ROOT / unit).read_text(encoding="utf-8")
    new_text = (candidate / unit).read_text(encoding="utf-8")
    for begin, end in INTERVALS:
        first, last = f'                assert $ == #{begin:04X}\n', f'                assert $ == #{end:04X}\n'
        chunk = new_text[new_text.index(first):new_text.index(last)]
        for before, after in resource_renames.items():
            chunk = chunk.replace(before[7:], after[7:])
        text = text[:text.index(first)] + chunk + text[text.index(last):]
    pending[unit] = text.encode('utf-8')
    pending['Includes/Const/Include.inc'] = (candidate / 'Includes/Const/Include.inc').read_bytes()
    # Адресная замена учитывает новые границы функций, а не только старое имя файла.
    old_names = {f["name"] for f in old_local}
    new_symbols = load(candidate, "Symbols.json")
    by_address = {value: key for key, value in new_symbols.items()
                  if key.startswith("Station.") and any(f["address"] <= value < f["address"]+f["end_offset"]-f["offset"] for f in new_local)}
    symbol_map = {key: by_address[value] for key, value in load(ROOT, "Symbols.json").items()
                  if key.startswith("Station.") and key.split(".")[1] in old_names}
    path_map = {}
    for function in old_local:
        owner = next(f for f in new_local if f["offset"] <= function["offset"] < f["end_offset"])
        path_map[function["path"]] = owner["path"]
    symbol_pattern = re.compile(r"Station\.(?:"+"|".join(re.escape(n) for n in old_names)+r")\.[A-Za-z_][A-Za-z0-9_]*")

    def rename(text):
        text = symbol_pattern.sub(lambda m: symbol_map[m[0]], text)
        for before, after in path_map.items():
            text = text.replace(before, after).replace("../"+before[7:], "../"+after[7:])
        return text

    for base in ("Source", "Docs", "Tools/Disasm/Reports"):
        for path in (ROOT / base).rglob("*"):
            relative_path = path.relative_to(ROOT).as_posix()
            if (not path.is_file() or relative_path in deletions or relative_path in pending
                    or path.suffix not in (".asm", ".inc", ".md", ".json") or "Runtime" in path.parts):
                continue
            before = path.read_text(encoding="utf-8")
            after = rename(before)
            if after != before:
                if path.suffix in (".asm", ".inc"):
                    lines = []
                    for old_line, new_line in zip(before.splitlines(), after.splitlines()):
                        if old_line != new_line and ";" in new_line and not new_line.lstrip().startswith(";"):
                            code, comment = new_line.split(";", 1)
                            if len(code.rstrip()) >= 80:
                                raise ValueError("Не помещается комментарий после замены символа")
                            new_line = code.rstrip().ljust(80)+";"+comment
                        lines.append(new_line)
                    after = "\n".join(lines)+"\n"
                pending[relative_path] = after.encode("utf-8")
    pending["Tools/Disasm/Reports/Functions.json"] = encode(merged_functions)
    pending["Tools/Disasm/Reports/SourceMap.json"] = encode(merged_map)
    pending["Tools/Disasm/Reports/ControlFlow.json"] = (candidate / "Tools/Disasm/Reports/ControlFlow.json").read_bytes()
    pending["Tools/Disasm/Reports/Symbols.json"] = encode(new_symbols)
    inventory = load(ROOT, "Inventory.json")
    totals = Counter()
    for record in merged_map:
        totals[record["kind"]] += record["length"]
    inventory.update(fragments=len(merged_functions),
                     described=sum(f["semantic_status"] == "described" for f in merged_functions),
                     unknown=sum(f["semantic_status"] == "unknown" for f in merged_functions),
                     instructions=sum(r["instruction_count"] for r in load(candidate, "ControlFlow.json")),
                     physical_bytes_by_kind=dict(totals),
                     ranges_by_kind=dict(Counter(r["kind"] for r in merged_map)))
    pending["Tools/Disasm/Reports/Inventory.json"] = encode(inventory)
    for path in ("Tools/Disasm/Reports/ModifiedCode.json", "Docs/ModifiedCode.md"):
        pending[path] = (candidate / path).read_bytes()
    # Обновление только станционных строк общего реестра и раздела новых процедур.
    path = "Docs/Functions.md"
    root_lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    new_lines = (candidate / path).read_text(encoding="utf-8").splitlines()
    selected = [i for i, s in enumerate(root_lines) if "| [Station." in s]
    root_lines[selected[0]:selected[-1]+1] = [s for s in new_lines if "| [Station." in s]
    root_lines = [next(n for n in new_lines if n.startswith("| Station |")) if s.startswith("| Station |") else s for s in root_lines]
    pending[path] = ("\n".join(root_lines)+"\n").encode("utf-8")
    path = "Docs/FunctionDetails/Station.md"
    old_doc = (ROOT / path).read_text(encoding="utf-8")
    new_doc = (candidate / path).read_text(encoding="utf-8")
    for old_name, new_name, next_name in (
            ('Unknown6638','PollJoystick','ClearInputFlags'),):
        next_new = next_name
        old_doc = (old_doc[:old_doc.index('## '+old_name+'\n')] +
                   new_doc[new_doc.index('## '+new_name+'\n'):new_doc.index('## '+next_new+'\n')] +
                   old_doc[old_doc.index('## '+next_name+'\n'):])
    for first, after in (('StepUpLeft','NoPointerMotion'),('StepUp','HandleItem25')):
        old_doc = old_doc.replace('## '+after+'\n',
                  new_doc[new_doc.index('## '+first+'\n'):new_doc.index('## '+after+'\n')]+'## '+after+'\n')
    pending[path] = old_doc.encode('utf-8')
    review = create_candidate(ROOT, review_relative, "documentation")
    for relative_path, data in pending.items():
        target = review / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for relative_path in deletions:
        target = (review / relative_path).resolve()
        if not target.is_relative_to(review / "Source"):
            raise ValueError("Удаление вышло за Source кандидата")
        target.unlink()
    VerifySources.ROOT = review
    VerifySources.main()
    AuditConformance.ROOT = review
    audit = AuditConformance.audit()
    for field in ("unlinked_functions", "missing_includes_or_resources", "missing_include_order",
                  "unresolved_global_references", "duplicate_global_definitions",
                  "global_reference_case_mismatches", "source_files_outside_graph", "python_duplicate_literal_keys"):
        if audit[field]:
            raise ValueError("Не прошла проверка объединения " + field)
    if original_hashes != fingerprint():
        raise ValueError("Текущие файлы изменились после начала подготовки")
    # Сохранение каждого заменяемого и архивируемого файла до записи в рабочую копию.
    for relative_path in set(pending) | deletions:
        path = ROOT / relative_path
        if path.exists():
            target = history / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    for relative_path, data in pending.items():
        path = (ROOT / relative_path).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Путь записи вышел за проект")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for relative_path in deletions:
        path = (ROOT / relative_path).resolve()
        if not path.is_relative_to(ROOT / "Source"):
            raise ValueError("Архивируемый путь вне Source")
        path.unlink()
    VerifySources.ROOT = ROOT
    VerifySources.main()
    AuditConformance.ROOT = ROOT
    audit = AuditConformance.audit()
    (ROOT / "Tools/Disasm/Reports/ConformanceAudit.json").write_bytes(encode(audit))
    report = dict(method="pointer_input_release_merge_after_isolated_static_validation", passed=True,
                  candidate=candidate.relative_to(ROOT).as_posix(), review=review.relative_to(ROOT).as_posix(),
                  replaced_existing_functions=len(old_local),
                  replaced_unknown_functions=sum(f["semantic_status"] == "unknown" for f in old_local),
                  documented_functions=sum(f["semantic_status"] == "described" for f in new_local),
                  archived_files=len(deletions), working_copy_files_written=len(pending),
                  instruction_count=inventory["instructions"],
                  remaining_unknown=audit["unknown_fragments"], remaining_contracts=audit["unknown_contract_fragments"],
                  assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/PointerInputReleaseVerification.json").write_bytes(encode(report))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate")
    parser.add_argument("review")
    args = parser.parse_args()
    main(args.candidate, args.review)
