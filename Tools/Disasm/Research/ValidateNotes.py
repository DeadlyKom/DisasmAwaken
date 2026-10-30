"""Проверка адресной привязки ручных пояснений до изменения исходников."""

import re


def validate_notes(analysis, region_comments):
    checked = 0
    for region_name, comments in region_comments.items():
        operations = {i["address"]: i["operation"] for r in analysis if r["name"] == region_name
                      for i in r["instructions"]}
        for address, (_, right) in comments.items():
            if address not in operations:
                raise ValueError(f"Нет инструкции для пояснения {region_name} #{address:04X}")
            if right and right.startswith("переход, если") and not re.match(
                    r"^(JR|JP) (NZ|Z|NC|C|PO|PE|P|M),", operations[address]):
                raise ValueError(f"Пояснение условного перехода стоит у другой команды {region_name} #{address:04X}")
            if right and right.startswith("выход, если") and not re.fullmatch(
                    r"RET (NZ|Z|NC|C|PO|PE|P|M)", operations[address]):
                raise ValueError(f"Пояснение условного выхода стоит у другой команды {region_name} #{address:04X}")
            checked += 1
    return checked
