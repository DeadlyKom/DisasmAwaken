"""Аудит текущих включённых исходников, без генерации кода и запуска сборки.

По умолчанию только печатает отчёт. --output сохраняет JSON по относительному пути.
Исторические снимки не участвуют в проверке текущего графа include.
"""

from pathlib import Path
from collections import Counter
import argparse
import ast
import json
import re

from SourcePresentation import BOILERPLATE, continuity, operation
from MapRuntimeProfiles import GUARDS as MAP_ORIGINAL_PROFILE_GUARDS


ROOT = Path(__file__).resolve().parents[3]


def structure_fields(paths):
    """Поля реальных STRUCT, без доверия к внешнему реестру Symbols.json."""
    structures = {}
    for path in paths:
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            code = line.split(";", 1)[0].strip()
            declaration = re.fullmatch(r"struct\s+(\w+)", code, re.I)
            if declaration:
                current = declaration[1]
                structures[current] = []
            elif current and code.lower() == "ends":
                current = None
            elif current and code:
                field = re.fullmatch(r"(\w+)\s+(?:db|dw|ds|text)\s+.+", code, re.I)
                if not field:
                    raise ValueError("Неподдержанное поле STRUCT: " + code)
                structures[current].append(field[1])
    return structures


def audit():
    functions = json.loads((ROOT / "Tools/Disasm/Reports/Functions.json").read_text(encoding="utf-8"))
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    following, order = continuity(functions, flow)
    files = set()
    missing = []
    incbins = set()

    def walk(path):
        path = path.resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Включение вне проекта: " + str(path))
        if not path.is_file():
            missing.append(path.relative_to(ROOT).as_posix())
            return
        if path in files:
            return
        files.add(path)
        for kind, name in re.findall(r'^\s*(?:\w+:\s*)?(include|incbin)\s+"([^"]+)"', path.read_text(encoding="utf-8"), re.M | re.I):
            target = (path.parent / name).resolve()
            if kind.lower() == "include":
                walk(target)
            elif not target.is_relative_to(ROOT) or not target.is_file():
                missing.append(str(target))
            else:
                incbins.add(target)

    # Проверка фактического графа включений от единственной точки сборки.
    walk(ROOT / "Builder/Main.asm")
    findings = []
    totals = Counter()
    unlinked = []
    unknown_contracts = []
    for function in functions:
        path = ROOT / function["path"]
        if path.resolve() not in files:
            unlinked.append(function["path"])
            continue
        text = path.read_text(encoding="utf-8")
        contract_block = re.search(r"^; In:[ \t]*\n(.*?)(?=^; Note:|^; -{3})", text, re.M | re.S)
        if contract_block and re.search(r"^;[ \t]+Unknown\b", contract_block[1], re.M):
            unknown_contracts.append(function["path"])
        lines = text.splitlines()
        for index, line in enumerate(lines):
            op = operation(line)
            issues = []
            if BOILERPLATE.fullmatch(line):
                issues.append("boilerplate_comment")
            if line.rstrip() != line:
                issues.append("trailing_whitespace")
            label = re.match(r"^\w+:\s*(.*)$", line)
            if label and (not label[1] or line.index(label[1]) != 16):
                issues.append("label_body_alignment")
            if re.match(r"^Point[0-9A-F]+:", line):
                issues.append("address_label")
            if re.search(r"\(I[XY]\s*[+-]\s*#[0-9A-F]+\)", op):
                issues.append("numeric_index_operand")
            if re.search(r"\b(?:JP|JR|CALL)\s+(?:[A-Z]+,\s*)?#[0-9A-F]+", op):
                issues.append("numeric_control_target")
            if re.search(r"; (?:переход|выход|вызов), если флаг (?:Z|Carry|Sign|P/V)", line):
                issues.append("condition_without_data_semantics")
            if re.match(r"^(?:JR|JP|CALL) (?:NZ|Z|NC|C|PO|PE|P|M),", op) or re.fullmatch(r"RET (?:NZ|Z|NC|C|PO|PE|P|M)", op):
                if ";" not in line or not line.split(";",1)[1].strip():
                    issues.append("conditional_without_right_comment")
            if op and ";" in line and line.index(";") != 80:
                issues.append("right_comment_column")
            if re.match(r"^(?:JP|JR|DJNZ|RET|RETI|RETN)(?:\s|$)", op):
                if index + 1 < len(lines) and lines[index + 1].strip():
                    issues.append("missing_blank_after_control")
            for issue in issues:
                totals[issue] += 1
                findings.append({"path": function["path"], "line": index + 1, "issue": issue})
        if function["path"] in following:
            target = following[function["path"]]
            marker = f"; JP @{target['region']}.{target['name']}.Entry, продолжение в "
            if marker not in text:
                totals["missing_continuation"] += 1
        if not re.search(r"\]\(\.\./\.\./Docs/[^)]+\.md\)", text):
            totals["missing_code_documentation_link"] += 1
    missing_order = []
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r'^\s*include "([^"]+)"', line, re.I)
            if not match:
                continue
            target = (path.parent / match[1]).resolve().relative_to(ROOT).as_posix()
            if target in order and f"({order[target]}) жёсткий порядок" not in line:
                missing_order.append({"path": path.relative_to(ROOT).as_posix(), "target": target})
    # Проверка объявлений глобальных ссылок в реальном графе, отдельно от чисел в Symbols.json.
    definitions = {}
    references = []
    duplicates = []
    exact_definitions = set()
    structures = structure_fields(files)
    for path in sorted(files):
        modules = []
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            code = line.split(";", 1)[0].strip()
            module = re.fullmatch(r"module\s+(\w+)", code, re.I)
            if module:
                modules.append(module[1])
                continue
            if code.lower() == "endmodule":
                modules.pop()
                continue
            # Регистрация размера структуры и смещений её фактически объявленных полей.
            declaration = re.fullmatch(r"struct\s+(\w+)", code, re.I)
            names = []
            if declaration:
                name = declaration[1]
                names = [name, *[name + "." + field for field in structures[name]]]
            label = re.match(r"^(\w+):|^(\w+)\s+equ\b", code, re.I)
            if label:
                name = label[1] or label[2]
                names.append(name)
                # Регистрация полей физического экземпляра только известного STRUCT.
                instance = re.match(r"^\w+:\s*(\w+)\b", code)
                if instance and instance[1] in structures:
                    names.extend(name + "." + field for field in structures[instance[1]])
            for name in names:
                exact_key = ".".join([*modules, name])
                exact_definitions.add(exact_key)
                key = exact_key.upper()
                if key in definitions:
                    duplicates.append({"symbol": key, "path": path.relative_to(ROOT).as_posix(), "line": index + 1})
                definitions[key] = path.relative_to(ROOT).as_posix()
            for symbol in re.findall(r"@([A-Za-z_][A-Za-z0-9_.]*)", code):
                references.append({"symbol": symbol, "path": path.relative_to(ROOT).as_posix(), "line": index + 1})
    unresolved = [item for item in references if item["symbol"].upper() not in definitions]
    case_mismatches = [item for item in references if item["symbol"] not in exact_definitions
                       and item["symbol"].upper() in definitions]
    unused_sources = [path.relative_to(ROOT).as_posix() for path in (ROOT / "Source").rglob("*")
                      if path.is_file() and path.resolve() not in files | incbins]
    # Проверка синтаксиса собственных Python-сценариев без исполнения и создания pyc.
    python_files = [p for p in (ROOT / "Tools/Disasm").rglob("*.py")
                    if not any(part in ("vendor", "History", "__pycache__") for part in p.parts)]
    duplicate_keys = []
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.relative_to(ROOT).as_posix())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            seen = set()
            for key in node.keys:
                try:
                    value = ast.literal_eval(key)
                    if value in seen:
                        duplicate_keys.append({"path": path.relative_to(ROOT).as_posix(), "line": key.lineno, "key": repr(value)})
                    seen.add(value)
                except (ValueError, TypeError, SyntaxError):
                    pass
    return {
        "method": "static_source_audit_without_assembly",
        "included_text_files": len(files), "included_binary_files": len(incbins),
        "registered_functions": len(functions), "unlinked_functions": unlinked,
        "missing_includes_or_resources": missing, "missing_include_order": missing_order,
        "global_definitions": len(definitions), "global_references": len(references),
        "unresolved_global_references": unresolved, "duplicate_global_definitions": duplicates,
        "global_reference_case_mismatches": case_mismatches, "source_files_outside_graph": unused_sources,
        "unknown_fragments": sum(f["semantic_status"] == "unknown" for f in functions),
        "unknown_contract_fragments": len(unknown_contracts), "unknown_contract_files": unknown_contracts,
        "named_fragments_without_proved_contract": sum(
            f["semantic_status"] == "described" and f["path"] in unknown_contracts for f in functions),
        "original_profile_only_contracts": len(MAP_ORIGINAL_PROFILE_GUARDS),
        "runtime_profile_limits": "See RuntimeProfileQualification.json and Docs/MapRuntimeProfiles.md, whole game remains unproved",
        "pending_by_region": dict(Counter(f["region"] for f in functions if f["semantic_status"] == "unknown")),
        "potential_continuations": len(following), "ordered_fragments": len(order),
        "python_scripts_parsed": len(python_files), "python_duplicate_literal_keys": duplicate_keys,
        "totals": dict(totals),
        "findings": findings, "full_semantic_analysis_complete": False,
        "assembly_executed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    if args.output:
        if args.output.is_absolute() or not (ROOT / args.output).resolve().is_relative_to(ROOT):
            raise ValueError("Отчёт должен сохраняться по относительному пути внутри проекта")
        (ROOT / args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("findings", "unknown_contract_files")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
