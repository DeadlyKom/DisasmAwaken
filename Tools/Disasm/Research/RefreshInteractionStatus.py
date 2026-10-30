"""Обновление конкретных счётчиков проекта по актуальным статическим отчётам, без сборки."""

from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]


def main():
    reports = ROOT / "Tools/Disasm/Reports"
    audit = json.loads((reports / "ConformanceAudit.json").read_text(encoding="utf-8"))
    inventory = json.loads((reports / "Inventory.json").read_text(encoding="utf-8"))
    source = json.loads((reports / "SourceVerification.json").read_text(encoding="utf-8"))
    if source["instruction_count"] != inventory["instructions"] or audit["registered_functions"] != inventory["fragments"]:
        raise ValueError("Отчёты относятся к разным состояниям исходников")
    history = ROOT / "Tools/Disasm/Research/History/BeforeInteractionStatus"
    if history.exists():
        raise ValueError("Эта фиксация статуса уже выполнена")
    pending = {}
    for name in ("Docs/Validation.md", "Docs/ConformancePlan.md"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        if name.endswith("Validation.md"):
            values = {
                "Исходных фрагментов": inventory["fragments"],
                "Именовано по установленному назначению или роли интерфейса": inventory["described"],
                "Назначение Unknown": audit["unknown_fragments"],
                "Размеченных инструкций": source["instruction_count"],
            }
            for label, value in values.items():
                text = re.sub(r"(?m)^- "+re.escape(label)+r": \d+\.", f"- {label}: {value}.", text)
            text = re.sub(r"(?m)^- Без доказанного регистрового контракта: .+$",
                          f'- Без доказанного регистрового контракта: {audit["unknown_contract_fragments"]}, включая {audit["named_fragments_without_proved_contract"]} уже именованных фрагментов.', text)
        else:
            text = re.sub(r"статическое соответствие \d+ инструкций", f'статическое соответствие {source["instruction_count"]} инструкций', text)
            text = re.sub(r"Актуальный остаток содержит \d+ фрагментов с неизвестным назначением и \d+ фрагментов\nбез доказанного регистрового контракта, включая \d+ уже именованных\.",
                          f'Актуальный остаток содержит {audit["unknown_fragments"]} фрагментов с неизвестным назначением и {audit["unknown_contract_fragments"]} фрагментов\nбез доказанного регистрового контракта, включая {audit["named_fragments_without_proved_contract"]} уже именованных.', text)
        text += "\nПроверенная цепочка указателя, смены контура, активного callback и геометрии описана в [Pointer](Pointer.md), [ItemToggle](ItemToggle.md), [InterfaceInput](InterfaceInput.md), [ActiveItem](ActiveItem.md) и [BoundsToggle](BoundsToggle.md). Ещё 137 исходных байтов размечены как 66 инструкций, 784 байта оформлены реальными записями масок и фона. Все 950 исходников имеют действующие относительные ссылки на документацию, проверены 1113 ссылок и обратные переходы сложных алгоритмов. Эти результаты не закрывают оставшийся смысловой разбор.\n"
        pending[name] = text
    for name, text in pending.items():
        path = ROOT / name
        saved = history / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, saved)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
