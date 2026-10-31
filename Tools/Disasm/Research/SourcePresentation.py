"""Оформление подтверждённой разметки, без изменения инструкций и адресов."""

import re


BOILERPLATE = re.compile(
    r"^\s*; (?:расчёт арифметического результата с исходным учётом переноса|"
    r"проверка соотношения аккумулятора и .+|проверка бита \d+ в .+|"
    r"копирование блока по исходным HL, DE и BC с направлением команды)\s*$")


def operation(line):
    if not line.strip() or line.lstrip().startswith(";"):
        return ""
    return line[16:].split(";", 1)[0].strip()


def instructions(text):
    return [op for line in text.splitlines() if (op := operation(line))
            and not op.lower().startswith(("module ", "endmodule"))]


def continuity(functions, flow):
    """Потенциальное продолжение при совпадении банка, физического и рабочего адреса."""
    decoded = {(r["name"], i["slot"], i["offset"]): i
               for r in flow for i in r["instructions"]}
    starts = {(f["region"], f["slot"], f["offset"]): f for f in functions}
    following = {}
    for function in functions:
        target = starts.get((function["region"], function["slot"], function["end_offset"]))
        if not target:
            continue
        # Проверка непрерывности рабочего адреса отдельно от дискового смещения.
        if target["address"] != function["address"] + function["end_offset"] - function["offset"]:
            continue
        block = [decoded[(function["region"], function["slot"], offset)]
                 for offset in range(function["offset"], function["end_offset"])
                 if (function["region"], function["slot"], offset) in decoded]
        last = block[-1]["operation"]
        # Проверка отсутствия обычного продолжения после безусловного выхода.
        if last in ("RET", "RETI", "RETN") or re.match(r"^(?:JP|JR) (?!NZ,|Z,|NC,|C,|PO,|PE,|P,|M,)", last):
            continue
        following[function["path"]] = target
    # Создание номеров только для связанных цепочек, независимо от порядка реестра.
    previous = {target["path"]: path for path, target in following.items()}
    order = {}
    for function in functions:
        path = function["path"]
        if path not in following or path in previous:
            continue
        index = 0
        while True:
            order[path] = index
            if path not in following:
                break
            path = following[path]["path"]
            index += 1
    return following, order


def format_function(text, target=None):
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(";"):
            line = " " * 16 + line.lstrip()
        if BOILERPLATE.fullmatch(line):
            continue
        op = operation(line)
        # Отделение следующего кода после каждого перехода и варианта выхода.
        if line.strip() and lines and lines[-1] and re.match(r"^(?:JP|JR|DJNZ|RET|RETI|RETN)(?:\s|$)", operation(lines[-1])):
            lines.append("")
        lines.append(line)
    if target:
        continuation = (" " * 16 + f"; JP @{target['region']}.{target['name']}.Entry, "
                        + "продолжение в " + target["path"].rsplit("/", 1)[-1])
        if continuation not in lines:
            # Добавление пояснения до закрытия модулей, без машинной команды.
            end = next(i for i, line in enumerate(lines) if operation(line).lower() == "endmodule")
            begin = end
            while begin and not lines[begin-1].strip():
                begin -= 1
            previous = operation(lines[begin-1]) if begin else ""
            gap = [""] if re.match(r"^(?:JP|JR|DJNZ|RET|RETI|RETN)(?:\s|$)", previous) else []
            lines[begin:end] = [*gap, continuation, ""]
    # Закрытие внутренних смысловых разделов перед концом модуля, без добавления инструкции.
    end = next((i for i, line in enumerate(lines) if operation(line).lower() == "endmodule"), len(lines))
    seen_code = False
    has_internal_sections = False
    divider = "; -----------------------------------------"
    for line in lines[:end]:
        op = operation(line)
        if op and not op.lower().startswith("module "):
            seen_code = True
        if seen_code and line.strip() == divider:
            has_internal_sections = True
    last = next((line.strip() for line in reversed(lines[:end]) if line.strip()), "")
    if has_internal_sections and last != divider:
        lines.insert(end, " " * 16 + divider)
    result = "\n".join(lines).rstrip() + "\n"
    if instructions(result) != instructions(text):
        raise ValueError("Оформление изменило последовательность инструкций")
    return result
