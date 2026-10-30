"""Регрессионная проверка совпадающих адресных имён в разных банках, только на кандидате."""

from pathlib import Path
import argparse
import copy
import hashlib
import json
import sys

from CandidateWorkspace import require_candidate
import PromoteFunction

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
import VerifySources


def fingerprints(root):
    # Проверка текущего проекта ограничена материалами, которые сценарий продвижения умеет менять.
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in ("Source", "Includes", "Builder", "Docs", "Tools/Disasm/Reports")
            for path in (root / folder).rglob("*") if path.is_file()}


def main(candidate):
    require_candidate(ROOT, candidate)
    info_path = candidate / "CandidateInfo.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    if info.get("regression_fixture"):
        raise ValueError("Кандидат уже использовался для теста")
    before_project = fingerprints(ROOT)
    station_path = candidate / "Source/Station/UnknownC325.asm"
    before_station = station_path.read_bytes()
    reports = candidate / "Tools/Disasm/Reports"
    before_functions = json.loads((reports / "Functions.json").read_text(encoding="utf-8"))
    expected_station = next(f for f in before_functions if f["region"] == "Station" and f["address"] == 0xC325)
    # Тестовое имя применяется только к копии Map, оно не объявляет неизвестный алгоритм разобранным.
    PromoteFunction.ROOT = candidate
    VerifySources.ROOT = candidate
    PromoteFunction.FUNCTIONS = copy.deepcopy(PromoteFunction.FUNCTIONS)
    PromoteFunction.CONTRACTS = copy.deepcopy(PromoteFunction.CONTRACTS)
    PromoteFunction.FUNCTIONS.setdefault("Map", {})[0xC325] = (
        "RegressionOnly", "Тестовая метка, назначение алгоритма этим не установлено")
    PromoteFunction.CONTRACTS["Map", 0xC325] = (
        ["Unknown, только проверка переименования"], ["Unknown, семантика не проверяется"],
        ["Unknown, семантика не проверяется"], ["Только регрессионная фикстура в отдельном кандидате"])
    PromoteFunction.promote("Map", 0xC325)
    VerifySources.main()
    actual_functions = json.loads((reports / "Functions.json").read_text(encoding="utf-8"))
    actual_station = next(f for f in actual_functions if f["region"] == "Station" and f["address"] == 0xC325)
    if actual_station != expected_station or station_path.read_bytes() != before_station:
        raise ValueError("Переименование Map изменило одноимённый фрагмент Station")
    if before_project != fingerprints(ROOT):
        raise ValueError("Проверка изменила текущий проект")
    info.update(regression_fixture=True, semantic_names_in_fixture_are_not_evidence=True)
    info_path.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"method": "scoped_promotion_in_isolated_candidate", "passed": True,
              "candidate": candidate.relative_to(ROOT).as_posix(),
              "same_name": "UnknownC325", "changed_region": "Map", "preserved_region": "Station",
              "current_project_sources_unchanged": True, "static_source_verification_passed": True,
              "semantic_analysis_proved": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/ScopedRenameVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    main((ROOT / parser.parse_args().candidate).resolve())
