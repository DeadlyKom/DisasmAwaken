"""Статическая проверка относительных ссылок из активных исходников и обратных ссылок сложных алгоритмов."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def local_targets(path):
    for link in LINK.findall(path.read_text(encoding="utf-8")):
        if "://" in link or link.startswith("#"):
            continue
        target = link.split("#", 1)[0]
        if target:
            yield link, (path.parent / target).resolve()


def audit():
    functions = json.loads((ROOT / "Tools/Disasm/Reports/Functions.json").read_text(encoding="utf-8"))
    missing, absolute, missing_backlinks = [], [], []
    checked = 0
    for function in functions:
        source = ROOT / function["path"]
        for literal, document in local_targets(source):
            checked += 1
            if not document.is_relative_to(ROOT):
                absolute.append(dict(source=function["path"], link=literal))
            elif not document.is_file():
                missing.append(dict(source=function["path"], link=literal))
            elif "FunctionDetails" not in document.parts:
                if not any(target == source.resolve() for _, target in local_targets(document)):
                    missing_backlinks.append(dict(source=function["path"], document=document.relative_to(ROOT).as_posix()))
    return dict(method="relative_source_documentation_link_graph_without_assembly", passed=not (missing or absolute or missing_backlinks),
                function_files=len(functions), source_links_checked=checked, missing_targets=missing,
                outside_project=absolute, missing_backlinks=missing_backlinks, assembly_executed=False)


if __name__ == "__main__":
    report = audit()
    (ROOT / "Tools/Disasm/Reports/DocumentationVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
