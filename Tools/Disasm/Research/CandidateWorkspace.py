"""Отдельная папка исследовательского выпуска, текущие исходники не перезаписываются."""

from pathlib import Path
import json
import shutil


def require_candidate(project, target, restore_archive=True):
    parent = (project / "Tools/Disasm/Research/Candidates").resolve()
    target = target.resolve()
    if target == parent or not target.is_relative_to(parent):
        raise ValueError("Выпуск допускается только в отдельную папку Tools/Disasm/Research/Candidates")
    # Восстановление старого снимка требуется только при явном обращении исследовательского инструмента.
    if restore_archive and (target / "ARCHIVED.json").is_file():
        from ResearchArchive import restore_snapshot
        restore_snapshot(project, target)


def create_candidate(project, relative, kind):
    relative = Path(relative)
    if relative.is_absolute():
        raise ValueError("Путь кандидата должен быть относительным")
    target = (project / relative).resolve()
    require_candidate(project, target, restore_archive=False)
    if target.exists():
        raise ValueError("Папка кандидата уже существует, перезапись запрещена")
    # Создание независимого набора входных материалов до выпуска нового исходного текста.
    for folder in ("Tools/Disasm/Disk", "Tools/Disasm/Extracted", "Includes", "Docs"):
        shutil.copytree(project / folder, target / folder)
    reports = target / "Tools/Disasm/Reports"
    reports.mkdir(parents=True)
    for path in (project / "Tools/Disasm/Reports").glob("*.json"):
        shutil.copy2(path, reports / path.name)
    if kind == "documentation":
        for folder in ("Source", "Builder"):
            shutil.copytree(project / folder, target / folder)
    (target / "CandidateInfo.json").write_text(json.dumps(
        {"kind": kind, "current_sources_overwritten": False, "assembly_executed": False,
         "copied_reports_are_input_snapshots": True}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
