"""Трассировка прямого потока управления по исходным байтам, без сборки."""

from pathlib import Path
import json
import re
import sys
import hashlib


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from InspectZ80 import decoder, entry
from Knowledge import FUNCTIONS

# Продолжение подтверждено исполнением исходной рамки и сохранением физического байта.
CONFIRMED_CONTINUATIONS = {"Station": {0xC0C8: "af"}}


def block(slot, offset, length, origin, name, roots=()):
    return dict(slot=slot, offset=offset, length=length, origin=origin,
                name=name, roots=list(roots))


# Адреса переноса получены из LDIR исходных загрузчиков, не являются новой раскладкой.
BLOCKS = [
    block(3, 0, 0x100, 0x5CCB, "Basic", (0x5CD1,)),
    block(3, 0x100, 0xA31, 0x6400, "Intro", (0x6500, 0x65B7)),
    # Образцы исполняются только после копирования, границы взяты из длины RepeatPattern.
    block(3, 0x422, 7, 0x6722, "IntroTemplates", (0x6722,)),
    block(3, 0x85A, 25, 0x6B5A, "IntroTemplates", (0x6B5A,)),
    block(3, 0xA78, 6, 0x6D78, "IntroTemplates", (0x6D78,)),
    block(3, 0xA7E, 15, 0x6D7E, "IntroTemplates", (0x6D7E,)),
    block(3, 0x2631, 0x6CF, 0x6E31, "IntroUnpack", (0x6E31,)),
    block(4, 0, 0x319, 0x6000, "StationBoot", (0x6300,)),
    block(4, 0x319, 0x2B5, 0x4000, "StationBoot", (0x4000,)),
    block(4, 0x5CE, 0x1C6A, 0x6322, "Station", (0x6322, 0x6E9C, 0x6F5D)),
    block(4, 0x2238, 0xA000-0x2238, 0x8238, "Station", (0x9A59, 0x9AEA, 0x639F, 0x9EFF, 0xA163)),
    block(4, 0x216C, 0x48, 0x4200, "StationExit", (0x4200,)),
    block(4, 0x10BD, 0x5C, 0x4000, "StationFinalExit", (0x4000,)),
    # Исходная загрузка D3D в банк 4, пока выделен только доказанный вход настройки границ.
    block(6, 0, 15978, 0xC000, "D3D", (0xE011,)),
    block(5, 0, 3864, 0xC000, "Text", (0xC000,)),
    block(7, 0, 11776, 0xC000, "Map", (0xC000, 0xC44A, 0xC474, 0xC677, 0xD0C3)),
    block(8, 0, 5921, 0xDB00, "Help", (0xDB00, 0xDB42, 0xDB57, 0xDB5B)),
    block(10, 0, 7209, 0xDB00, "Music", (0xDB00, 0xDB05, 0xDB08)),
    block(17, 0, 0x43, 0x6000, "ActionBoot", (0x6000,)),
    block(17, 0x43, 0x1FA, 0x4200, "ActionBoot", (0x4200,)),
    block(17, 0x23D, 0x1F8F, 0x6000, "Action", (0x6000,)),
    block(17, 0x21CC, 0xA000-0x21CC, 0x81CC, "Action", (0xA82D, 0xAB1B, 0xAB23)),
    block(19, 0, 8224, 0xC000, "ThreeD", (0xC000,)),
    block(20, 0, 11264, 0xC000, "Voxel", ()),
    block(21, 0, 3784, 0xEC00, "Voxel", (0xEC00, 0xEC0E, 0xEC1B, 0xEC7F)),
    block(22, 0, 6878, 0xC000, "Controls", ()),
    block(23, 0, 6474, 0xDADE, "Controls", (0xDADE,)),
    block(29, 0, 19114, 0x6000, "Final", (0x6000, 0x616C, 0x6196)),
    block(29, 0x247, 0x34, 0x6247, "FinalTemplates", (0x6247,)),
    block(29, 0x27D, 0x17, 0x627D, "FinalTemplates", (0x627D,)),
]


def payload(slot):
    return (ROOT / (entry(slot)["path"] + ".sectors.bin")).read_bytes()


def analyze(name, extra_roots=(), observed=(), initial_bank=None):
    chunks = [b for b in BLOCKS if b["name"] == name]
    memory = bytearray(65536)
    origins = {}
    for chunk in chunks:
        data = payload(chunk["slot"])[chunk["offset"]:chunk["offset"] + chunk["length"]]
        for index, value in enumerate(data):
            address = chunk["origin"] + index
            if address in origins:
                raise ValueError(f"Перекрытие представления {name} #{address:04X}")
            memory[address] = value
            origins[address] = (chunk["slot"], chunk["offset"] + index)
    dis = decoder(memory)
    instructions = {}
    owners = {}
    calls = set()
    branches = set()
    unresolved = []
    overlaps = []
    roots = {address for chunk in chunks for address in chunk["roots"]}
    roots.update(address for address in extra_roots if address in origins)
    roots.update(address for address in FUNCTIONS.get(name, {}) if address in origins)
    # Поиск девяти продолжений доказанного переходного умножителя, его JP не создаёт CPU-возврата.
    if name == "D3D":
        # Поиск исходных целей девяти достижимых кодов сторон, общих для E171 и EAB6.
        # Это корни разнесённой таблицы, а не перенос готового реестра инструкций в разведку.
        clip_codes = (0, 1, 2, 4, 5, 6, 8, 9, 10)
        clip_targets = set()
        for first in clip_codes:
            for second in clip_codes:
                index = first * 16 + second
                target = memory[0xCC00 + index] + 256 * memory[0xCD00 + index]
                if not 0xE1EB <= target <= 0xE85D:
                    raise ValueError("Изменена исходная цель таблицы отсечения D3D")
                clip_targets.add(target)
        if len(clip_targets) != 71:
            raise ValueError("Изменилось число различных целей отсечения D3D")
        roots.update(clip_targets)
        # Продолжения обоих диспетчеров положены в стек явно, JP (HL) их сам не обнаруживает.
        if memory[0xE1DD:0xE1E2] != bytes.fromhex('11e2e1d5e9'):
            raise ValueError("Изменено стековое продолжение отсечения многоугольника D3D")
        if memory[0xEB01:0xEB08] != bytes.fromhex('1108ebd5d5d5e9'):
            raise ValueError("Изменены три стековых продолжения отсечения отрезка D3D")
        roots.update((0xE1E2, 0xEB08))
        # Проверка всех 32 чётных входов развёрнутой строки, включая не наблюдённую первую пару.
        if memory[0xD1C0:0xD207] != bytes.fromhex('020c'*31+'08fd5deb0aa62cb602'):
            raise ValueError("Изменена исходная развёрнутая строка D3D")
        roots.update(range(0xD1C0,0xD200,2))
        multiply_continuations = set()
        for address in range(0xEB7E, 0xEC28 - 6):
            if (memory[address:address+2] == bytes.fromhex("d911") and
                    memory[address+4:address+7] == bytes.fromhex("c310eb")):
                target = memory[address+2] + 256*memory[address+3]
                if target != address+7:
                    raise ValueError("Изменено продолжение переходного умножителя D3D")
                multiply_continuations.add(target)
        if len(multiply_continuations) != 9:
            raise ValueError("Изменены девять исходных вызовов умножителя D3D")
        roots.update(multiply_continuations)
        # Поиск всех шести подготовленных целей каждого JR масштаба, исходные FE не отражают рабочие переходы.
        # Три последних операнда подготавливает проверенный ConfigurePreviewProjectionScale.
        for address in (0xED5B, 0xEDC3, 0xEDFC, 0xDA1F, 0xDA3A, 0xDAF8):
            if memory[address:address+7] != bytes.fromhex("18fe2929292929"):
                raise ValueError("Изменён исходный развёрнутый масштаб D3D")
            roots.update(address+2+skip for skip in range(6))
        # Продолжение преобразования задаётся IY, доказанный помощник завершает работу JP (IY).
        if memory[0xED0A:0xED11] != bytes.fromhex("fd2111edc37eeb"):
            raise ValueError("Изменено продолжение преобразования D3D")
        roots.add(0xED11)
        # Поиск десяти подготовок продолжения через HL перед JP к перспективе.
        # Маска 81 возвращается в Opposite, который не достигается обычным последовательным декодированием.
        for address,target in ((0xD987,0xD98D),(0xD99D,0xDA08),(0xD9A7,0xD9AD),(0xD9B4,0xD9BA),(0xD9C1,0xD9C7),(0xD9CE,0xD9D4),(0xD9DB,0xD9E1),(0xD9E8,0xD9EE),(0xD9F5,0xD9FB),(0xDA02,0xDA08)):
            opcode = 0xC3 if address in (0xD987,0xD99D) else 0xC2
            if memory[address:address+6] != bytes((0x21,target&255,target>>8,opcode,0x14,0xDA)):
                raise ValueError("Изменена подготовка продолжения перспективы D3D")
            roots.add(target)
        # Проверка самостоятельного плоского входа, его полный проход доказан моделью, игровой вызывающий путь ещё не установлен.
        if memory[0xD819:0xD822] != bytes.fromhex("3a01c2473a1fc29047"):
            raise ValueError("Изменено начало плоского обхода D3D")
        roots.add(0xD819)
    # Периодический адрес 68EA записывается DrawItem26, остальные входы достигаются его исходными ветвями.
    if name == "Station":
        roots.update((0x6870, 0x68CC, 0x68EA, 0x693E))
    # Поиск корней по исходной разнесённой таблице кодов границ, это статический снимок до рабочих записей.
    if name == "Map":
        codes = (0, 1, 2, 4, 5, 6, 8, 9, 10)
        for first in codes:
            for second in codes:
                index = first * 16 + second
                target = memory[0xDE00 + index] + 256 * memory[0xDF00 + index]
                if not 0xD4DD <= target < 0xDB63:
                    raise ValueError("Изменена исходная цель допустимой пары кодов границ")
                roots.add(target)
        roots.add(0xD4DD)
    # Поиск станционных обработчиков по исходной таблице шестнадцатибайтовых элементов интерфейса.
    if name == "Station":
        position = 0xF0FD
        for index in range(128):
            if memory[position] == 0x80:
                break
            for field in (6, 12):
                target = memory[position+field] + 256*memory[position+field+1]
                if target in origins:
                    roots.add(target)
                # Действие вызывается по EventHandler+3, сама обёртка задаёт отдельный вход закрытия.
                if field == 6 and target+3 in origins:
                    roots.add(target+3)
            position += 16
        # Шаблон диалогового элемента задаёт два входа, обёртку JP и обработчик из HL.
        for address in range(0x6322, 0x7F8C - 10):
            if (memory[address] == 0xC3 and
                    memory[address+1] + 256*memory[address+2] == address+3 and
                    memory[address+3] == 0x21 and
                    memory[address+6:address+9] == bytes.fromhex("cd21cc")):
                roots.add(address)
                roots.add(memory[address+4] + 256*memory[address+5])
    # Поиск обработчиков в доказанных таблицах трёхбайтовых команд интерпретатора.
    if name == "Text":
        for position in range(0xC935, 0xCA67, 3):
            target = memory[position+1] + 256*memory[position+2]
            if not 0xC000 <= target < 0xC935:
                raise ValueError("Нарушен формат семейства таблиц интерпретатора")
            roots.add(target)
        for start, count in ((0xC932, 15), (0xC95F, 11), (0xC980, 36),
                             (0xCA3A, 7), (0xCA4F, 7)):
            for index in range(1, count + 1):
                position = start + index * 3
                target = memory[position + 1] + 256 * memory[position + 2]
                if target in origins:
                    roots.add(target)
        # Вложенные диспетчеры используют тот же формат из символа и адреса.
        for address in range(0xC000, 0xC932 - 7):
            if memory[address] == 0x21 and memory[address+3] == 0x06:
                start = memory[address+1] + 256*memory[address+2]
                count = memory[address+4]
                if 0xC932 <= start < 0xCA67 and 1 <= count <= 36 and start + count*3 + 2 < 0xCA67:
                    for index in range(1, count + 1):
                        position = start + index*3
                        target = memory[position+1] + 256*memory[position+2]
                        if 0xC000 <= target < 0xC935:
                            roots.add(target)
    # Поиск входов таблицы диспетчеризации, младшие и старшие байты разделены.
    if name in ("ThreeD", "Action"):
        roots.update(memory[0xCF00+i] + 256*memory[0xD000+i]
                     for i in range(256) if memory[0xD000+i] != 0)
    # Дополнение проверенных непрерывных кодовых областей между входами обработчиков.
    ranges = {"Text": ((0xC000, 0xC935),),
              "ThreeD": ((0xC000, 0xCEE3), (0xCF08, 0xCF0B), (0xD10A, 0xD194)),
              "Action": ((0xC000, 0xCEE3), (0xCF08, 0xCF0B), (0xD10A, 0xD194))}
    linear = set()
    for start, end in ranges.get(name, ()):
        for instruction in dis.disassemble(start, end, "h"):
            if instruction.operation.startswith("DEFB") or instruction.address + len(instruction.bytes) > end:
                raise ValueError(f"Неоднозначное кодирование в установленном диапазоне {name}")
            linear.add(instruction.address)
    # Проверка ручных продолжений не превращает их в самостоятельные точки входа функций.
    continuations = CONFIRMED_CONTINUATIONS.get(name, {})
    for address, encoded in continuations.items():
        raw = bytes.fromhex(encoded)
        if any(address + i not in origins for i in range(len(raw))) or memory[address:address + len(raw)] != raw:
            raise ValueError("Не совпали исходные байты подтверждённого продолжения")
    if initial_bank is None:
        initial_bank = 4 if name == "D3D" else 0
    pending = [(address, initial_bank, None) for address in sorted(roots | set(observed) | linear | set(continuations), reverse=True)]
    while pending:
        address, bank, accumulator = pending.pop()
        hl_constant = None
        while address in origins and address not in instructions:
            if name in ("Station", "Action") and address >= 0xC000 and bank != 0:
                break
            if address in owners:
                overlaps.append({"entry": address, "instruction": owners[address]})
                break
            instruction = dis.disassemble(address, address + 1, "h")[0]
            data = instruction.bytes
            if not data or any(address + i not in origins for i in range(len(data))):
                break
            if any(address + i in owners for i in range(len(data))):
                overlaps.append({"entry": address, "instruction": "crossed"})
                break
            operation = instruction.operation
            if operation.startswith("DEFB"):
                unresolved.append({"address": address, "operation": operation,
                                   "reason": "неоднозначное или недокументированное кодирование"})
                break
            instructions[address] = dict(address=address, operation=operation,
                                         hex=data.hex(), slot=origins[address][0],
                                         offset=origins[address][1])
            for index in range(len(data)):
                owners[address + index] = address
            following = address + len(data)
            match = re.fullmatch(r"(CALL|JP|JR|DJNZ) (?:([A-Z]+),)?#([0-9A-F]+)", operation)
            if match:
                kind, condition, value = match.groups()
                target = int(value, 16)
                (calls if kind == "CALL" else branches).add(target)
                # Проверка явно банковых и создаваемых во время исполнения входов.
                dynamic = name in ("Station", "Action") and target >= 0xC000 and bank != 0
                dynamic |= name == "Station" and (target >= 0xD000 or target == 0x910D)
                dynamic |= name == "Intro" and target >= 0x6E31
                dynamic |= name == "Final" and target >= 0x62A9
                dynamic |= name == "ThreeD" and not any(start <= target < end for start,end in ranges["ThreeD"])
                if target in origins and not dynamic:
                    pending.append((target, bank, accumulator))
                else:
                    unresolved.append({"address": address, "operation": operation,
                                       "target": target, "bank": bank,
                                       "reason": "банковый или динамический вход" if dynamic
                                       else "вне текущего представления памяти"})
                if kind in ("JP", "JR") and not condition:
                    break
                if kind == "CALL":
                    # Переданный через HL обработчик позже вызывается диспетчером интерфейса.
                    if name == "Station" and target in (0xCBA9, 0xCC21) and hl_constant in origins:
                        roots.add(hl_constant)
                        pending.append((hl_constant, bank, None))
                    # Обновление абстрактной страницы только через установленный интерфейс OUT #7FFD.
                    page_calls = {"Station": (0x6396, 0x639F), "StationExit": (0x6396,), "StationFinalExit": (0x6396,), "Action": (0xAB1B,)}
                    if target in page_calls.get(name, ()):
                        bank = None if accumulator is None else accumulator & 7
                    elif name in ("Station", "Action"):
                        bank = None
                    accumulator = None
                    hl_constant = None
            elif operation in ("RET", "RETI", "RETN"):
                break
            elif operation in ("JP (HL)", "JP (IX)", "JP (IY)"):
                unresolved.append({"address": address, "operation": operation,
                                   "reason": "косвенный переход"})
                break
            elif operation.startswith("RST "):
                unresolved.append({"address": address, "operation": operation,
                                   "reason": "обработчик RST зависит от ПЗУ и контекста"})
                break
            # Обновление банка для доказанного прямого OUT 1F в перенесённом финальном загрузчике.
            if name == "StationFinalExit" and address == 0x4011 and operation == "OUT (C),A" and accumulator == 0x1F:
                bank = 7
            # Поиск фактического callback MainLoop по записи в операнд периодического CALL.
            if name == "Station" and operation == "LD (#9A89),HL" and hl_constant in origins:
                roots.add(hl_constant)
                pending.append((hl_constant, bank, None))
            # Расчёт константы A для последующих явных переключений банков.
            constant = re.fullmatch(r"LD A,#([0-9A-F]+)", operation)
            if constant:
                accumulator = int(constant[1], 16)
            elif operation in ("XOR A", "SUB A"):
                accumulator = 0
            elif operation.startswith("LD A,") or operation in ("POP AF", "EX AF,AF'"):
                accumulator = None
            elif re.match(r"^(ADD A,|ADC A,|SUB |SBC A,|AND |OR |XOR |IN |RLA|RLCA|RRA|RRCA|CPL|NEG|DAA|INC A|DEC A)", operation):
                accumulator = None
            constant_hl = re.fullmatch(r"LD HL,#([0-9A-F]+)", operation)
            if constant_hl:
                hl_constant = int(constant_hl[1],16)
            elif re.match(r"^(LD HL,|LD H,|LD L,|POP HL|ADD HL,|ADC HL,|SBC HL,|INC HL|DEC HL|EX |EXX|LDI|LDD)", operation):
                hl_constant = None
            address = following
    return dict(name=name, blocks=chunks, roots=sorted(roots), calls=sorted(calls),
                branches=sorted(branches), instructions=sorted(instructions.values(), key=lambda i:(i["slot"],i["offset"])),
                unresolved=unresolved, overlaps=overlaps,
                instruction_count=len(instructions), code_bytes=len(owners),
                total_bytes=len(origins), classified_fraction=len(owners)/len(origins))


def main():
    reports = ROOT / "Tools/Disasm/Reports"
    reports.mkdir(parents=True, exist_ok=True)
    names = list(dict.fromkeys(b["name"] for b in BLOCKS))
    extra = {name:set() for name in names}
    observed = {name:set() for name in names}
    # Поиск входов, действительно достигнутых ограниченной моделью с совпадающими исходными байтами.
    for model_file, primary, context in (
            ("FlightModel.json", "Action", {0:"Action", 1:"Controls", 3:"Voxel"}),
            ("StationModel.json", "Station", {0:"Station", 1:"Map", 3:"Music", 6:"Text", 7:"Help"})):
        model_path = reports / model_file
        if not model_path.exists():
            continue
        model = json.loads(model_path.read_text(encoding="utf-8"))
        for key, encoded in model["visited"].items():
            page_text, address_text = key.split(":")
            address, page = int(address_text, 16), int(page_text)
            name = primary if page == -1 and address >= 0x6000 else context.get(page)
            if not name:
                continue
            for chunk in BLOCKS:
                if chunk["name"] == name and chunk["origin"] <= address < chunk["origin"] + chunk["length"] - 3:
                    offset = chunk["offset"] + address - chunk["origin"]
                    if payload(chunk["slot"])[offset:offset+4].hex() == encoded:
                        observed[name].add(address)
        for page, source, target in model["calls"]:
            name = primary if target < 0xC000 else context.get(page)
            if name and target in observed[name]:
                extra[name].add(target)
    # Поиск исходных музыкальных инструкций, достигнутых отдельной проверкой до петли позиций.
    music_path = reports / "MusicVerification.json"
    if music_path.exists():
        model = json.loads(music_path.read_text(encoding="utf-8"))
        for address_text, encoded in model.get("original_visited", {}).items():
            address = int(address_text, 16)
            for chunk in BLOCKS:
                if chunk["name"] == "Music" and chunk["origin"] <= address < chunk["origin"] + chunk["length"] - 3:
                    offset = chunk["offset"] + address - chunk["origin"]
                    if payload(chunk["slot"])[offset:offset+4].hex() == encoded:
                        observed["Music"].add(address)
    # Поиск только неизменённых инструкций глифов, достигнутых моделью с побитовой сверкой изображения.
    glyph_path = reports / "GlyphRenderVerification.json"
    if glyph_path.exists():
        glyph = json.loads(glyph_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not glyph.get("passed") or glyph.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка глифов не относится к текущим исходным байтам")
        for encoded_address, encoded in glyph.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xAE55 <= address < 0xBCAB:
                raise ValueError("Адрес модели глифов вне проверенного диапазона")
            offset = address - 0x6000
            if data[offset:offset + len(raw)] != raw:
                raise ValueError("Изменённая инструкция ошибочно названа исходной")
            observed["Station"].add(address)
    # Поиск исходных числовых инструкций только по проверенной модели того же секторного файла.
    number_path = reports / "NumberOutputVerification.json"
    if number_path.exists():
        number = json.loads(number_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not number.get("passed") or number.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка числового вывода не относится к текущим байтам")
        for encoded_address, encoded in number.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xBBA8 <= address < 0xBD01 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная исходная инструкция числовой модели")
            observed["Station"].add(address)
    # Поиск исполненных инструкций второго контура рамки по проверенной модели тех же байтов.
    inner_path = reports / "InnerFrameVerification.json"
    if inner_path.exists():
        model = json.loads(inner_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка внутренней рамки не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not (0xC201 <= address < 0xC21F or 0xC3A4 <= address < 0xC436):
                raise ValueError("Инструкция модели внутренней рамки вне разрешённого участка")
            if data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Инструкция модели внутренней рамки изменена")
            observed["Station"].add(address)
    # Поиск полного восстановления границ только по исходным инструкциям подтверждённой модели.
    bounds_path = reports / "InterfaceListsVerification.json"
    if bounds_path.exists():
        model = json.loads(bounds_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка границ не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xCB52 <= address < 0xCBE0 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели восстановления границ")
            observed["Station"].add(address)
    # Дополнение чтения бита контура только неизменёнными инструкциями проверенной побайтовой модели.
    state_path = reports / "InterfaceStateVerification.json"
    if state_path.exists():
        model = json.loads(state_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка входного состояния не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0x9E97 <= address < 0x9EA5 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели чтения бита контура")
            observed["Station"].add(address)
    # Дополнение активации только исходными инструкциями полной модели списка, рамок и указателя.
    active_path = reports / "ActiveItemVerification.json"
    if active_path.exists():
        model = json.loads(active_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка активации не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xCC81 <= address < 0xCCAA or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели активации")
            observed["Station"].add(address)
    # Дополнение условного продолжения и смены геометрии проверенными неизменёнными инструкциями.
    toggle_path = reports / "BoundsToggleVerification.json"
    if toggle_path.exists():
        model = json.loads(toggle_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка смены геометрии не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xCC2C <= address < 0xCC81 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели смены геометрии")
            observed["Station"].add(address)
    # Дополнение трёх XOR-ядер только полностью покрытыми исходными инструкциями пиксельной модели.
    outline_path = reports / "XorOutlineVerification.json"
    if outline_path.exists():
        model = json.loads(outline_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка XOR-контура не относится к текущим байтам")
        verified_bytes = 0
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xC4BE <= address < 0xC626 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели XOR-контура")
            verified_bytes += len(raw)
            observed["Station"].add(address)
        if verified_bytes != 360:
            raise ValueError("Неполное покрытие XOR-контура")
    # Дополнение удаления по индексу только исходными байтами проверенной модели фиксированного сдвига.
    remove_path = reports / "RemoveDrawVerification.json"
    if remove_path.exists():
        model = json.loads(remove_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка удаления не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not (0xC873 <= address < 0xC87C or 0xCB1C <= address < 0xCB52) or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели удаления")
            observed["Station"].add(address)
    # Дополнение интерактивной геометрии после проверки полного цикла и исчерпывающих осевых ограничений.
    tracker_path = reports / "TrackGeometryVerification.json"
    if tracker_path.exists():
        model = json.loads(tracker_path.read_text(encoding="utf-8"))
        clamps = json.loads((reports / "GeometryClampsVerification.json").read_text(encoding="utf-8"))
        data = payload(4)
        digest = hashlib.sha256(data).hexdigest()
        if not model.get("passed") or not clamps.get("passed") or model.get("source_sha256") != digest or clamps.get("source_sha256") != digest:
            raise ValueError("Проверки геометрии не относятся к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xC87C <= address < 0xCB1C or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция модели интерактивной геометрии")
            observed["Station"].add(address)
    # Дополнение цепочки перерисовки только неизменёнными байтами модели договоров вызовов.
    repaint_path = reports / "RepaintChainVerification.json"
    if repaint_path.exists():
        model = json.loads(repaint_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка цепочки возвратов не относится к текущим байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xCBE0 <= address < 0xCC21 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция цепочки возвратов")
            observed["Station"].add(address)
    # Дополнение кнопок мыши исходными инструкциями проверенной модели аппаратных байтов.
    mouse_path = reports / "MouseInputVerification.json"
    if mouse_path.exists():
        model = json.loads(mouse_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка мыши не относится к исходным байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            offset = address-0x6322+0x5CE
            if not 0x658E <= address < 0x6638 or data[offset:offset+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция опроса мыши")
            observed["Station"].add(address)
    # Дополнение направлений только исходными инструкциями проверенного опроса и таблицы вызовов.
    input_path = reports / "PointerInputsVerification.json"
    if input_path.exists():
        model = json.loads(input_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка клавиатуры и джойстика не относится к исходным байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            offset = address-0x6322+0x5CE
            if not (0x6638 <= address < 0x66D8 or 0x670E <= address < 0x6771) or data[offset:offset+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция обработки направлений")
            observed["Station"].add(address)
    # Дополнение двух графических входов по пиксельной модели с инъекцией исходного ISR.
    graphics_path = reports / "WindowGraphicsVerification.json"
    if graphics_path.exists():
        model = json.loads(graphics_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка графики окна не относится к исходным байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xA020 <= address < 0xA102 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция графики окна")
            observed["Station"].add(address)
    # Дополнение одиночного ввода только исходными инструкциями модели всех клавиш и их пар.
    matrix_path = reports / "MatrixKeyVerification.json"
    if matrix_path.exists():
        model = json.loads(matrix_path.read_text(encoding="utf-8"))
        data = payload(4)
        if not model.get("passed") or model.get("source_sha256") != hashlib.sha256(data).hexdigest():
            raise ValueError("Проверка одиночной клавиши не относится к исходным байтам")
        for encoded_address, encoded in model.get("original_visited", {}).items():
            address = int(encoded_address, 16)
            raw = bytes.fromhex(encoded)
            if not 0xA116 <= address < 0xA163 or data[address-0x6000:address-0x6000+len(raw)] != raw:
                raise ValueError("Недостоверная инструкция одиночного ввода")
            observed["Station"].add(address)
    # Поиск межбанковых входов только по известным переключениям исходных загрузчиков.
    for iteration in range(8):
        analysis = [analyze(name, extra[name], observed[name]) for name in names]
        before = sum(map(len, extra.values()))
        for region in analysis:
            bank_names = ({1:"Map", 3:"Music", 6:"Text", 7:"Help"} if region["name"] == "Station"
                          else {1:"Controls", 3:"Voxel"} if region["name"] == "Action" else {})
            for call in region["unresolved"]:
                if call.get("target", 0) >= 0xC000 and call.get("bank") in bank_names:
                    extra[bank_names[call["bank"]]].add(call["target"])
        # Обновление разметки совпадающей копии 3DPART внутри ACTION после побайтовой проверки.
        action = next(r for r in analysis if r["name"] == "Action")
        shared = payload(19)[:8224]
        if shared != payload(17)[0x6000:0x8020]:
            raise ValueError("Копии 3DPART различаются")
        decoded_addresses = {i["address"] for i in action["instructions"]}
        extra["ThreeD"].update(address for address in action["calls"] + action["roots"]
                               if 0xC000 <= address < 0xE020 and address in decoded_addresses)
        if sum(map(len, extra.values())) == before:
            break
    (reports / "ControlFlow.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for region in analysis:
        print(f"{region['name']:16} {region['instruction_count']:5} instructions, "
              f"{region['code_bytes']:5}/{region['total_bytes']:5} bytes, "
              f"{len(region['calls']):3} call targets, {len(region['overlaps'])} overlaps")


if __name__ == "__main__":
    main()
