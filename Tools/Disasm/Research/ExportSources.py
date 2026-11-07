"""Однократный выпуск исходников по сохранённой статической разметке.

Это исследовательский этап, сборка его не запускает. Не применять поверх
пользовательских исправлений без отдельного просмотра получающихся изменений.
"""

from pathlib import Path
import hashlib
import json
import re
import sys
import argparse


ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = ROOT
sys.path.insert(0, str(Path(__file__).resolve().parent))
from Analyze import BLOCKS
from PackedResourcePrefixTable import final_lines
from Knowledge import FUNCTIONS, REGIONS
from Contracts import CONTRACTS

from IntroNotes import NOTES as INTRO_NOTES, COMMENTS as INTRO_COMMENTS
from MusicNotes import NOTES as MUSIC_NOTES, COMMENTS as MUSIC_COMMENTS
from EffectsNotes import NOTES as EFFECTS_NOTES, COMMENTS as EFFECTS_COMMENTS
from FinalNotes import NOTES as FINAL_NOTES, COMMENTS as FINAL_COMMENTS
from TextNotes import NOTES as TEXT_NOTES, COMMENTS as TEXT_COMMENTS
from MapNotes import NOTES as MAP_NOTES, COMMENTS as MAP_COMMENTS
from StationNotes import NOTES as STATION_NOTES, COMMENTS as STATION_COMMENTS
from BasicNotes import NOTES as BASIC_NOTES, COMMENTS as BASIC_COMMENTS
from SemanticNames import LABELS, name_operands, name_instruction, documentation_links
from SourcePresentation import continuity, format_function
from TokenTables import render as render_token_tables, PATH as TOKEN_TABLE_PATH
from CandidateWorkspace import create_candidate, require_candidate
from PhaseStates import render as render_phase_states, PATH as PHASE_STATE_PATH
from GlyphRoutes import render as render_glyph_routes, PATH as GLYPH_ROUTE_PATH
from NumberFacts import BOUNDARIES
from PointerTables import render as render_pointer_tables, SPRITES as POINTER_SPRITES, BACKGROUND as POINTER_BACKGROUND
from MouseInputTables import render as render_mouse_input, PATH as MOUSE_INPUT_PATH
from MatrixKeyTable import render as render_matrix_keys, PATH as MATRIX_KEYS
from ContextMenuText import render as render_context_menu, PATH as CONTEXT_MENU_TEXT
from RandomStateTable import render as render_random_states, PATH as RANDOM_STATES
from SignatureTables import render as render_signature, PATH as CURRENT_SIGNATURE
from MarketTables import render as render_market, RANGES as MARKET_RANGES
from AuxiliaryMapTables import RANGES as AUXILIARY_MAP_RANGES, render as render_auxiliary_map
from MarkerSpriteTables import RANGES as MARKER_SPRITE_RANGES, render as render_marker_sprites
from AnimatedVariantTables import RANGES as ANIMATED_VARIANT_RANGES, render as render_animated_variants
from ArcWorkspaceTable import DATA as ARC_WORKSPACE, render as render_arc_workspace
from ClipWorkTables import render as render_clip_work, ENDPOINTS as CLIP_ENDPOINTS, PRODUCTS as CLIP_PRODUCTS, OUTPUT_SIZE as CLIP_OUTPUT_SIZE, CORNERS as CLIP_CORNERS
from MapLineTables import render as render_map_line, RANGES as MAP_LINE_RANGES
from MapChainPointTables import render as render_map_chain_points, RANGES as MAP_CHAIN_POINT_RANGES
from StoredMapOrderTable import render as render_stored_map_order, PATH as STORED_MAP_ORDER
from StoredMapPointTables import render as render_stored_map_points, PATH as STORED_MAP_POINTS
from MissionTextsTable import render as render_mission_texts, PATH as MISSION_TEXTS
from MissionMessageTables import render as render_mission_messages, RANGES as MISSION_MESSAGES
from SystemPrefixTable import render as render_system_prefixes, PATH as SYSTEM_PREFIXES
from MissionOfferTable import render as render_mission_offer, PATH as MISSION_OFFER
from PlayerRankTable import render as render_player_ranks, PATH as PLAYER_RANKS
from ActionFileKeyTable import render as render_action_key, PATH as ACTION_FILE_KEY
from StationExitFacts import COMMENTS as STATION_EXIT_COMMENTS
from FinalExitFacts import COMMENTS as FINAL_EXIT_COMMENTS
from D3DClipFacts import COMMENTS as D3D_COMMENTS
from FinalFileKeyTable import render as render_final_key, PATH as FINAL_FILE_KEY
from ExpressionStackTable import render as render_expression_stack, PATH as EXPRESSION_STACK
from AssignmentScratchTable import render as render_assignment_scratch, PATH as ASSIGNMENT_SCRATCH
from MarketScriptTable import render as render_market_script, PATH as MARKET_SCRIPT, START as MARKET_SCRIPT_START
from SettingsTables import render as render_settings, CHOICES as SETTINGS_CHOICES, COLORS as SETTINGS_COLORS, CONTROLS as SETTINGS_CONTROLS, TEXT as SETTINGS_TEXT
from StationIrqTables import render as render_station_irq_data, COUNTER as IRQ_COUNTER, STACK as IRQ_STACK, CHAIN as WINDOW_CHAIN
from PointerInputTables import render as render_pointer_input, FLAGS as INPUT_FLAGS, DIRECTIONS as INPUT_DIRECTIONS, KEYS as INPUT_KEYS

REGION_NOTES = {"Intro": INTRO_NOTES, "Music": MUSIC_NOTES, "Voxel": EFFECTS_NOTES, "Final": FINAL_NOTES, "Text": TEXT_NOTES, "Map": MAP_NOTES, "Station": STATION_NOTES, "Basic": BASIC_NOTES}
REGION_COMMENTS = {"Intro": INTRO_COMMENTS, "Music": MUSIC_COMMENTS, "Voxel": EFFECTS_COMMENTS, "Final": FINAL_COMMENTS, "Text": TEXT_COMMENTS, "Map": MAP_COMMENTS, "Station": STATION_COMMENTS, "Basic": BASIC_COMMENTS, "StationExit": STATION_EXIT_COMMENTS, "StationFinalExit": FINAL_EXIT_COMMENTS, "D3D": D3D_COMMENTS}


def write(path, text):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def asm(operation="", comment=None, label=""):
    line = f"{label:<16}{operation}" if label else " " * 16 + operation
    if comment:
        if len(line) >= 80:
            raise ValueError("Инструкция не помещается перед правым комментарием: " + line)
        line = line.ljust(80) + "; " + comment
    return line.rstrip()


CONDITIONS = {
    "Z": "флаг Z установлен", "NZ": "флаг Z сброшен",
    "C": "флаг Carry установлен", "NC": "флаг Carry сброшен",
    "P": "флаг Sign сброшен", "M": "флаг Sign установлен",
    "PE": "флаг P/V установлен", "PO": "флаг P/V сброшен",
}


def annotate(operation):
    condition = re.match(r"(JR|JP|CALL|RET) (NZ|Z|NC|C|PO|PE|P|M)(?:,|$)", operation)
    if condition:
        verb = {"JR": "переход", "JP": "переход", "CALL": "вызов", "RET": "выход"}[condition[1]]
        return f"{verb}, если {CONDITIONS[condition[2]]}"
    return None


def prefix_comment(operation):
    # Пояснение операции берётся из ручного разбора, автоматический пересказ запрещён.
    return None


def export_screens(slot, data, sizes):
    folder = "Source/Screens/Station" if slot == 9 else f"Source/Screens/Panel{slot:02d}"
    includes = []
    records = []
    offset = 0
    for index, sectors in enumerate(sizes):
        allocated = sectors * 256
        block = data[offset:offset+allocated]
        # Проверка сигнатуры, длины экрана и секторной границы по исходному заголовку.
        unpacked = int.from_bytes(block[2:4], "little")
        packed = int.from_bytes(block[4:6], "little")
        if block[:2] != b"HR" or unpacked != 6912 or not 12 < packed <= allocated:
            raise ValueError("Не подтверждён заголовок экранного ресурса")
        stem = f"Screen{index:02d}"
        target = ROOT / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / (stem+".Bitstream.bin")).write_bytes(block[12:packed])
        (target / (stem+".Tail.bin")).write_bytes(block[packed:])
        lines = [asm(f"module PackedScreens{slot:02d}"), asm("module "+stem),
                 asm('; Формат [сохранённый конец и общий поток](../../../Docs/PackedResourcePrefix.md)'),
                 "; -----------------------------------------",
                 f"; упакованный экран {index}, исходное смещение #{offset:04X}",
                 "; 6144 байта пикселей и 768 байт атрибутов после распаковки",
                 "; хвост сохраняет физический секторный формат исходного диска",
                 "; -----------------------------------------",
                 asm('FPackedHeader {', "исходный заголовок ресурса", "Header:"),
                 asm('#5248,', "Signature, сигнатура HR"),
                 asm('#1B00,', "UnpackedSize, размер экрана с атрибутами"),
                 asm(f'#{packed:04X}', "PackedSize, длина файла вместе с заголовком"),
                 asm('}'),
                 *final_lines(block,stem),
                 asm(f'incbin "{stem}.Tail.bin"', "байты до конца выделенных секторов", "Tail:"),
                 asm(f"assert $ - Header == #{allocated:04X}"),
                 asm("endmodule"), asm("endmodule")]
        write(folder+"/"+stem+".asm", "\n".join(lines))
        includes.append(asm(f'include "{stem}.asm"'))
        records.append(dict(slot=slot, index=index, offset=offset, packed_size=packed,
                            unpacked_size=unpacked, allocated_size=allocated,
                            path=folder+"/"+stem+".asm"))
        offset += allocated
    if offset != len(data):
        raise ValueError("Экранные блоки не покрывают исходные сектора")
    write(folder+"/Include.inc", "\n".join(includes))
    return folder+"/Include.inc", records


def main():
    require_candidate(PROJECT_ROOT, ROOT)
    disk = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    analysis = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    # Проверка привязки ручных пояснений к началу реальных инструкций до записи исходников.
    from ValidateNotes import validate_notes
    validate_notes(analysis, REGION_COMMENTS)
    data_by_slot = {e["slot"]: (ROOT / (e["path"] + ".sectors.bin")).read_bytes() for e in disk["entries"]}
    language = data_by_slot[5]
    for index, position in enumerate(range(0x935,0xA67,3)):
        token = language[position]
        address = int.from_bytes(language[position+1:position+3],"little")
        if index < 15:
            name = f"Command{token:02X}"
            role = "команда"
        elif position < 0x983:
            name = f"Operator{token:02X}"
            role = "оператор выражения"
        elif position < 0x9EF:
            suffix = ("Upper" if chr(token).isupper() else "Lower" if chr(token).islower() else "Code") + (chr(token) if chr(token).isalnum() else f"{token:02X}")
            name = "ReadField" + suffix
            role = "чтение поля"
        else:
            name = f"Property{index:03d}"
            role = "обработчик свойства или записи"
        FUNCTIONS.setdefault("Text",{}).setdefault(address,
            (name, f"{role} торгового языка, символ #{token:02X}, исходная запись таблицы #{position+0xC000:04X}"))
    # Именование обработчиков по установленной роли в таблице диспетчеризации рёбер.
    geometry = data_by_slot[19]
    handlers = {}
    for index in range(256):
        target = geometry[0xF00+index] + 256*geometry[0x1000+index]
        if target:
            handlers.setdefault(target,[]).append(index)
    for address, indices in handlers.items():
        description = "обработчик ребра для индексов таблицы " + ", ".join(f"#{i:02X}" for i in indices)
        for region in ("ThreeD","Action"):
            FUNCTIONS.setdefault(region,{}).setdefault(address,(f"EdgeCase{indices[0]:02X}",description))
    for address, description in FUNCTIONS.get("ThreeD",{}).items():
        FUNCTIONS.setdefault("Action",{}).setdefault(address,description)
    interface = []
    position = 0x90FD
    while data_by_slot[4][position] != 0x80:
        raw = data_by_slot[4][position:position+16]
        values = list(raw[:6]) + [int.from_bytes(raw[6:8],"little")] + list(raw[8:12]) + [int.from_bytes(raw[12:14],"little"),int.from_bytes(raw[14:16],"little")]
        index = len(interface)
        interface.append(dict(index=index, offset=position, values=values, hex=raw.hex()))
        for field, prefix, purpose in ((6,"Handle","обработчик события"),(12,"Draw","обработчик рисования")):
            address = int.from_bytes(raw[field:field+2],"little")
            FUNCTIONS.setdefault("Station", {}).setdefault(address,
                (f"{prefix}Item{index:02d}",f"{purpose} станционного элемента из записи {index} таблицы FInterfaceItem"))
        position += 16
    item_end = position + 1
    list_end = item_end
    while int.from_bytes(data_by_slot[4][list_end:list_end+2],"little") != 0x0101:
        list_end += 2
    list_end += 2
    instructions = {}
    names = {}
    functions = []
    symbols = {}
    used_symbols = set()

    # Создание физически непрерывных фрагментов с границами по прямым вызовам и ручной разметке.
    for region in analysis:
        name = region["name"]
        by_address = {i["address"]: i for i in region["instructions"]}
        # Вызов чужого банка не создаёт границу процедуры по совпавшему числовому адресу текущего банка.
        nonlocal_calls = {(item["address"], item.get("target")) for item in region["unresolved"]
                          if item.get("reason") == "банковый или динамический вход"}
        local_calls = set()
        for instruction in region["instructions"]:
            call = re.fullmatch(r"CALL (?:[A-Z]+,)?#([0-9A-F]+)", instruction["operation"])
            if call:
                target = int(call[1], 16)
                if (instruction["address"], target) not in nonlocal_calls:
                    local_calls.add(target)
        starts = set(region["roots"]) | local_calls
        starts.update(FUNCTIONS.get(name, {}))
        starts.update(BOUNDARIES.get(name, set()))
        ordered = sorted(region["instructions"], key=lambda i: (i["slot"], i["offset"]))
        current = None
        for instruction in ordered:
            address = instruction["address"]
            if current is None or address in starts or instruction["slot"] != current["slot"] or instruction["offset"] != current["end_offset"]:
                known = FUNCTIONS.get(name, {}).get(address)
                stem = known[0] if known else f"Unknown{address:04X}"
                current = dict(region=name, name=stem, address=address,
                               slot=instruction["slot"], offset=instruction["offset"],
                               description=known[1] if known else "Unknown, назначение этого фрагмента ещё не установлено",
                               semantic_status="described" if known else "unknown",
                               instructions=[])
                functions.append(current)
            current["instructions"].append(instruction)
            current["end_offset"] = instruction["offset"] + len(bytes.fromhex(instruction["hex"]))
            instructions[(instruction["slot"], instruction["offset"])] = (current, instruction)
        for function in [f for f in functions if f["region"] == name]:
            function["path"] = f"Source/{name}/{function['name']}.asm"
            for index, instruction in enumerate(function["instructions"]):
                label = "Entry" if index == 0 else LABELS.get((name, instruction["address"]), f"Point{instruction['address']:04X}")
                full = f"{name}.{function['name']}.{label}"
                names[(name, instruction["address"])] = full
                symbols[full] = instruction["address"]

    following, include_order = continuity(functions, analysis)
    # Сохранение исходников инструкций, числа в операндах заменяются только доказанными целями.
    for function in functions:
        name = function["region"]
        begin, end = function["offset"], function["end_offset"]
        contract = CONTRACTS.get((name, function["address"]))
        inputs, outputs, corrupt, notes = contract or (
            ["Unknown, регистровый контракт ещё не доказан"],
            ["исходный поток управления, включая переходы в соседние фрагменты"],
            ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница"],
            ["граница файла не доказывает границу логической процедуры",
             "состояние самомодификации и активной страницы учитывается отдельно"])
        notes = [*notes, *REGION_NOTES.get(name, {}).get(function["address"], [])]
        lines = [asm("module " + name), asm("module " + function["name"]),
                 *documentation_links(name, function["address"]),
                 "; -----------------------------------------", "; " + function["description"],
                 f"; исходная запись {function['slot']}, файловые смещения #{begin:04X}..#{end-1:04X}",
                 "; In:", *[";   "+s for s in inputs],
                 "; Out:", *[";   "+s for s in outputs],
                 "; Corrupt:", *[";   "+s for s in corrupt],
                 "; Note:", *[";   "+s for s in notes],
                 "; -----------------------------------------"]
        for index, instruction in enumerate(function["instructions"]):
            operation = instruction["operation"]
            custom = REGION_COMMENTS.get(name, {}).get(instruction["address"])
            before, custom_right = custom or (None, None)
            if before is None:
                automatic = prefix_comment(operation)
                before = [automatic] if automatic else []
            for text in before:
                lines.append(asm("; " + text))
            comment = custom_right or annotate(operation)
            target = re.fullmatch(r"(CALL|JP|JR|DJNZ) (?:([A-Z]+),)?#([0-9A-F]+)", operation)
            if target:
                key = (name, int(target[3], 16))
                unresolved = next(r for r in analysis if r["name"] == name)["unresolved"]
                is_banked = any(u["address"] == instruction["address"] and u.get("reason") == "банковый или динамический вход" for u in unresolved)
                if key in names and not is_banked:
                    operation = operation[:operation.rfind("#")] + "@" + names[key]
                    used_symbols.add(names[key])
                elif int(target[3], 16) == 0x3D13:
                    operation = operation[:operation.rfind("#")] + "@TrDos.Dispatch"
            operation = re.sub(r",(?!\s)", ", ", operation)
            if name == "Station":
                for address, variable in ((0x6306,"CurrentPage"),(0x8500,"ItemIndex"),
                                          (0x8600,"DirtyCells"),(0xF0FD,"Items"),(0xF3DE,"DrawList")):
                    operation = operation.replace(f"#{address:04X}", "@StationState."+variable)
            operation = operation.replace("(IX+", "(IX + ").replace("(IY+", "(IY + ")
            operation = operation.replace("(IX-", "(IX - ").replace("(IY-", "(IY - ")
            operation = name_operands(name, function["address"], operation)
            operation = name_instruction(name, function["address"], instruction["address"], operation)
            # Локальные метки оставляются только у входов и действительных целей переходов.
            label = "Entry:" if index == 0 else LABELS.get((name, instruction["address"]), f"Point{instruction['address']:04X}") + ":"
            lines.append(asm(operation, comment, label))
            if instruction["operation"] in ("RET", "RETI", "RETN") or instruction["operation"].startswith(("JP ", "JR ")):
                lines.append("")
        lines.extend([asm("endmodule"), asm("endmodule")])
        write(function["path"], format_function("\n".join(lines), following.get(function["path"])))

    # Удаление избыточных служебных меток из нового выпуска, сами инструкции не меняются.
    for function in functions:
        path = ROOT / function["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            label = re.match(r"^(Point[0-9A-F]{4}):", line)
            if label:
                full = f"{function['region']}.{function['name']}.{label[1]}"
                if full not in used_symbols:
                    lines[index] = " " * 16 + line[16:]
        write(function["path"], "\n".join(lines))
    symbols = {name:value for name,value in symbols.items() if name.endswith(".Entry") or name in used_symbols
               or name.rsplit(".", 1)[-1] in LABELS.values()}

    # Создание типизированной исходной таблицы интерфейса без изменения её физических байтов.
    fields = ["X","Y","Width","Height","Flags","TextIndex","EventHandler",
              "SavedX","SavedY","SavedWidth","SavedHeight","DrawHandler","Unknown0E"]
    item_lines = [asm("module InterfaceItems"), "; исходная таблица #F0FD, шаг FInterfaceItem равен #10"]
    for record in interface:
        # Регистрация фактического физического экземпляра для именованных обращений к его полям.
        symbols[f"InterfaceItems.Item{record['index']:02d}"] = 0xF0FD+16*record['index']
        item_lines.append(asm("FInterfaceItem {", label=f"Item{record['index']:02d}:"))
        for index, (field,value) in enumerate(zip(fields,record["values"])):
            expression = "@"+names[("Station",value)] if field in ("EventHandler","DrawHandler") and ("Station",value) in names else f"#{value:04X}" if field in ("EventHandler","DrawHandler","Unknown0E") else f"#{value:02X}"
            item_lines.append(asm("    "+expression+("," if index<len(fields)-1 else ""), "FInterfaceItem."+field))
        item_lines.append(asm("}"))
    item_lines.extend([asm("DB #80", "ограничитель таблицы элементов", "End:"), asm("endmodule")])
    symbols["InterfaceItems.End"] = 0xF0FD+16*len(interface)
    write("Source/Station/Data/InterfaceItems.asm", "\n".join(item_lines))
    list_lines = [asm("module InterfaceDrawList"), "; исходные указатели перерисовки с ограничителем #0101"]
    for offset in range(item_end, list_end-2, 2):
        value = int.from_bytes(data_by_slot[4][offset:offset+2],"little")
        expression = "@"+names[("Station",value)] if ("Station",value) in names else f"#{value:04X}"
        list_lines.append(asm("DW "+expression))
    list_lines.extend([asm("DW #0101", "ограничитель списка обработчиков", "End:"), asm("endmodule")])
    write("Source/Station/Data/DrawList.asm", "\n".join(list_lines))
    special = {(4,0x90FD):(item_end,"Source/Station/Data/InterfaceItems.asm",0xF0FD),
               (4,item_end):(list_end,"Source/Station/Data/DrawList.asm",0xF3DE)}
    # Выделение только доказанных разнесённых слов, исполняемый код между ними сохраняется отдельно.
    if re.search(r"\bstruct\s+FMusicEffectTarget\b", (ROOT/"Includes/Structs/Include.inc").read_text(encoding="utf-8"), re.I):
        from MusicEffectTables import TABLES as MUSIC_EFFECT_TABLES, render as render_music_effect_table
        for table in MUSIC_EFFECT_TABLES:
            module, path, start, entries = table
            text, bindings = render_music_effect_table(data_by_slot[10], table)
            write(path, text)
            symbols.update(bindings)
            special[10, start-0xDB00] = (start-0xDB00+2*len(entries), path, start)
    # Выделение исходных физических таблиц музыки только при наличии согласованных структур.
    if re.search(r"\bstruct\s+FMusicAyRegisters\b", (ROOT/"Includes/Structs/Include.inc").read_text(encoding="utf-8"), re.I):
        from MusicPlayerTables import TABLES as MUSIC_PLAYER_TABLES, render as render_music_player_table
        for table in MUSIC_PLAYER_TABLES:
            module, path, start, end, structure, fields, record_names = table
            text, bindings = render_music_player_table(data_by_slot[10], table)
            write(path, text)
            symbols.update(bindings)
            special[10, start] = (end, path, 0xDB00+start)
    # Очередь Controls остаётся двумя физическими байтами HighKind и LowValue.
    if re.search(r"\bstruct\s+FTextQueueItem\b", (ROOT/"Includes/Structs/Include.inc").read_text('utf-8'), re.I):
        from ControlsTextQueueFacts import TABLE as TEXT_QUEUE_TABLE, render as render_text_queue
        text, bindings = render_text_queue(data_by_slot[23])
        write(TEXT_QUEUE_TABLE[1], text)
        symbols.update(bindings)
        special[23, 0x11A2] = (0x11C4, TEXT_QUEUE_TABLE[1], 0xEC80)
    # Восстановление восьми физических фаз XOR-маркера только в отдельном кандидате.
    if "struct FMarkerPhaseMasks" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsMarkerFacts import TABLE as MARKER_TABLE, render as render_marker
        text, bindings = render_marker(data_by_slot[23])
        write(MARKER_TABLE[1], text)
        symbols.update(bindings)
        special[23, 0x160F] = (0x162F, MARKER_TABLE[1], 0xF0ED)
    # Физические записи Y,X выделяются только в отдельном кандидате.
    if "struct FBufferPoint" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsBufferPointsFacts import TABLE as BUFFER_POINTS_TABLE, render as render_buffer_points
        text, bindings = render_buffer_points(data_by_slot[22])
        write(BUFFER_POINTS_TABLE[1], text)
        symbols.update(bindings)
        special[22, 0x500] = (0x546, BUFFER_POINTS_TABLE[1], 0xC500)
    # Исходные 256 отсчётов синуса формируются из байтов, не из новой формулы.
    if "struct FFixedSineValue" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionSineTable import TABLE as ACTION_SINE_TABLE, render as render_action_sine
        text, bindings = render_action_sine(data_by_slot[17])
        write(ACTION_SINE_TABLE[1], text)
        symbols.update(bindings)
        special[17, 0x3900] = (0x3A00, ACTION_SINE_TABLE[1], 0x9900)
    # Две исходные плоскости квадратов оформляются по физическим байтам CONTROL0.
    if "struct FSquareTableByte" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsSquareTable import TABLE as SQUARE_TABLE, render as render_squares
        text, bindings = render_squares(data_by_slot[22])
        write(SQUARE_TABLE[1], text)
        symbols.update(bindings)
        special[22, 0x300] = (0x500, SQUARE_TABLE[1], 0xC300)
    # Исходные затравки и известная часть записываемых строковых масок.
    if "struct FSmallMaskSeed" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsSmallMaskTables import TABLES as SMALL_MASK_TABLES, render as render_small_mask
        for table in SMALL_MASK_TABLES:
            text, bindings = render_small_mask(data_by_slot[22], table)
            write(table[1], text)
            symbols.update(bindings)
            special[22, table[2]] = (table[3], table[1], 0xC000+table[2])
    # Четыре физических входных байта проекции, остальные рабочие байты не типизируются формально.
    if "struct FBodyProjection" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsBodyProjection import TABLE as BODY_PROJECTION, render as render_body_projection
        text, bindings = render_body_projection(data_by_slot[22])
        write(BODY_PROJECTION[1], text)
        symbols.update(bindings)
        special[22, 0x117D] = (0x1181, BODY_PROJECTION[1], 0xD17D)
    # Физическая рабочая запись, сохранение исходного порядка и байтов.
    if "struct FCircleRasterWork" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsCircleWork import TABLE as CIRCLE_WORK, render as render_circle_work
        text, bindings = render_circle_work(data_by_slot[22])
        write(CIRCLE_WORK[1], text)
        symbols.update(bindings)
        special[22, 0x1181] = (0x118D, CIRCLE_WORK[1], 0xD181)
    # Четыре исходных байта двухсловного генератора ACTION.
    if "struct FWordRandomState" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionWordRandomState import TABLE as WORD_RANDOM_STATE, render as render_word_random
        text, bindings = render_word_random(data_by_slot[17])
        write(WORD_RANDOM_STATE[1], text)
        symbols.update(bindings)
        special[17, 0x3B15] = (0x3B19, WORD_RANDOM_STATE[1], 0x9B15)
    # Исходные трёхбайтовые правила параметров, перекрытые шаблонные чтения сохраняются.
    if "struct FParameterCoefficient" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsParameterCoefficients import TABLE as PARAMETER_COEFFICIENTS, render as render_parameter_coefficients
        text, bindings = render_parameter_coefficients(data_by_slot[23])
        write(PARAMETER_COEFFICIENTS[1], text)
        symbols.update(bindings)
        special[23, 0x486] = (0x4B3, PARAMETER_COEFFICIENTS[1], 0xDF64)
    # Исходные 32 физических фазы четырёх трёхстрочных знаков.
    if "struct FThreeRowGlyphPhase" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsThreeRowGlyphs import TABLE as THREE_ROW_GLYPHS, render as render_three_row_glyphs
        text, bindings = render_three_row_glyphs(data_by_slot[23])
        write(THREE_ROW_GLYPHS[1], text)
        symbols.update(bindings)
        special[23, 0x6D3] = (0x793, THREE_ROW_GLYPHS[1], 0xE1B1)
    # Четыре физические записи входов индикаторов, третий вектор хранит Y перед X.
    if "struct FGlyphIndicatorControl" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionGlyphIndicatorState import PATH as GLYPH_INPUT_PATH, render as render_glyph_inputs
        text, bindings = render_glyph_inputs(data_by_slot[17])
        write(GLYPH_INPUT_PATH, text)
        symbols.update(bindings)
        special[17, 0x3B81] = (0x3B8D, GLYPH_INPUT_PATH, 0x9B81)
    # Шестнадцать исходных адресов для диспетчеризации через RET, полного разбора хвостов нет.
    if "struct FReturnDispatchEntry" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsRasterReturns import TABLE as RASTER_RETURNS, render as render_raster_returns
        text, bindings = render_raster_returns(data_by_slot[23])
        write(RASTER_RETURNS[1], text)
        symbols.update(bindings)
        special[23, 0x793] = (0x7B3, RASTER_RETURNS[1], 0xE271)
    # Исходные физические ресурсы маскированных объектных значков.
    if "struct FObjectGlyphClearPhase" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsObjectGlyphData import TABLES as OBJECT_GLYPH_TABLES, render as render_object_glyph_data
        for table in OBJECT_GLYPH_TABLES:
            text, bindings = render_object_glyph_data(data_by_slot[23],table)
            write(table[1],text)
            symbols.update(bindings)
            special[23,table[2]] = (table[3],table[1],0xDADE+table[2])
    # Семь физических масок шестистрочной шкалы.
    if "struct FGaugePartialMask" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsGaugeMasks import TABLE as GAUGE_MASKS, render as render_gauge_masks
        text,bindings=render_gauge_masks(data_by_slot[23])
        write(GAUGE_MASKS[1],text)
        symbols.update(bindings)
        special[23,0xE95]=(0xE9C,GAUGE_MASKS[1],0xE973)
    # Физическая пара байтов, выбираемых вместе с адресом в ACTION.
    if "struct FPreferredBytePair" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionPreferredByteState import TABLE as PREFERRED_BYTES, render as render_preferred_bytes
        text,bindings=render_preferred_bytes(data_by_slot[17])
        write(PREFERRED_BYTES[1],text)
        symbols.update(bindings)
        special[17,0x3C10]=(0x3C12,PREFERRED_BYTES[1],0x9C10)
    # Первые 26 отдельных указателей и 27 физических пар порта и маски, без дублирования кода 704B.
    if "struct FKeyScanInput" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionKeyScanTables import TABLES as KEY_SCAN_TABLES, render as render_key_scan_table, origin as key_scan_origin
        for table in KEY_SCAN_TABLES:
            text,bindings=render_key_scan_table(data_by_slot[17],table)
            write(table[1],text)
            symbols.update(bindings)
            special[17,table[2]]=(table[3],table[1],key_scan_origin(table)+table[2])
    # Физическая пара байтов остатка ракет, Fallback перед Preferred.
    if "struct FMissileStock" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionMissileStockFacts import TABLE as MISSILE_STOCK, render as render_missile_stock
        text,bindings=render_missile_stock(data_by_slot[17])
        write(MISSILE_STOCK[1],text)
        symbols.update(bindings)
        special[17,0x3C12]=(0x3C14,MISSILE_STOCK[1],0x9C12)
    # Физические коды трёх захваченных целей ракет.
    if "struct FMissileTargets" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionMissileLaunchFacts import TABLE as MISSILE_TARGETS, render as render_missile_targets
        text,bindings=render_missile_targets(data_by_slot[17])
        write(MISSILE_TARGETS[1],text)
        symbols.update(bindings)
        special[17,0x3B1B]=(0x3B1E,MISSILE_TARGETS[1],0x9B1B)
    # Физические знаковые поправки перенесённого ядра ACTION.
    if "struct FIndexedDelta" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionTypeDeltaFacts import TABLE as TYPE_DELTAS, render as render_type_deltas
        text,bindings=render_type_deltas(data_by_slot[17])
        write(TYPE_DELTAS[1],text)
        symbols.update(bindings)
        special[17,0x588]=(0x598,TYPE_DELTAS[1],0x634B)
    # Начальные 25 записей и отдельный маркер, реальные вложенные экземпляры.
    if "struct FActionRecord" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionObjectRecords import PATH as OBJECT_RECORDS, render as render_object_records
        text,bindings=render_object_records(data_by_slot[17])
        write(OBJECT_RECORDS,text)
        symbols.update(bindings)
        special[17,0x4100]=(0x4780,OBJECT_RECORDS,0xA100)
    # Пять потоков с доказанными границами, остальные соседние байты не классифицируются.
    if "struct FActionAyFrame" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionAyStreams import GROUPS as AY_STREAM_GROUPS, render as render_ay_streams, bounds as ay_stream_bounds
        for path,streams in AY_STREAM_GROUPS:
            text,bindings=render_ay_streams(data_by_slot[17],streams)
            write(path,text)
            symbols.update(bindings)
            start,end=ay_stream_bounds(streams)
            special[17,start]=(end,path,start+0x6000)
    # Физические 256 нормированных квадратов исходной страницы 9800.
    if "struct FSymmetricSquareValue" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionProjectionClipFacts import TABLE as PROJECTION_SQUARES, render as render_projection_squares
        text,bindings=render_projection_squares(data_by_slot[17])
        write(PROJECTION_SQUARES[1],text)
        symbols.update(bindings)
        special[17,0x3800]=(0x3900,PROJECTION_SQUARES[1],0x9800)
    # Физическая двухбайтовая точка с доказанными потребителями, X перед Y.
    if "struct FActionAimPoint" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionAimPointData import PATH as AIM_POINT_PATH, render as render_aim_point
        text,bindings=render_aim_point(data_by_slot[17])
        write(AIM_POINT_PATH,text)
        symbols.update(bindings)
        special[17,0x3B19]=(0x3B1B,AIM_POINT_PATH,0x9B19)
    # Три физические фазы построителя ACTION, те же поля вложены в runtime-снимок.
    if "struct FRenderPhases" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionRenderPhasesData import PATH as RENDER_PHASES_PATH, render as render_render_phases
        text,bindings=render_render_phases(data_by_slot[17])
        write(RENDER_PHASES_PATH,text)
        symbols.update(bindings)
        special[17,0x3B12]=(0x3B15,RENDER_PHASES_PATH,0x9B12)
    # Физическая таблица OBJECT3D, сохраняются все 128 записей, включая одинаковые указатели.
    if "struct FObjectDataPointer" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionObjectPointersData import TABLE as OBJECT_POINTER_TABLE, render as render_object_pointers
        text,bindings=render_object_pointers(data_by_slot[17])
        write(OBJECT_POINTER_TABLE[1],text)
        symbols.update(bindings)
        special[17,0x3E00]=(0x3F00,OBJECT_POINTER_TABLE[1],0x9E00)
    # Исходные прямые и инверсные маски восьми пиксельных фаз ACTION.
    from ActionClipProductsData import PATH as CLIP_PRODUCTS_PATH, render as render_clip_products
    text,bindings=render_clip_products(data_by_slot[17])
    write(CLIP_PRODUCTS_PATH,text)
    symbols.update(bindings)
    special[17,0x6F2B]=(0x6F3B,CLIP_PRODUCTS_PATH,0xCF2B)
    # Реальные пиксельные маски ACTION внутри невыбираемых областей таблицы.
    from ActionLineMasksData import PATH as LINE_MASKS_PATH, render as render_line_masks
    text,bindings=render_line_masks(data_by_slot[17])
    write(LINE_MASKS_PATH,text)
    symbols.update(bindings)
    special[17,0x8010]=(0x8020,LINE_MASKS_PATH,0xE010)
    # Физические рабочие точки внутри невыбираемых индексов младшей таблицы ACTION.
    from ActionClipPointsData import POINTS as CLIP_POINTS, render as render_clip_point
    for name,offset,path in CLIP_POINTS:
        text,bindings=render_clip_point(data_by_slot[17],name,offset)
        write(path,text);symbols.update(bindings)
        special[17,offset]=(offset+5,path,offset+0x6000)
    # Три физических трёхбайтовых состояния генератора ACTION, девять исходных байтов.
    if "struct FFoldedRandomState" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionFoldedRandomData import TABLES as FOLDED_STATES, render as render_folded_state
        for table in FOLDED_STATES:
            text, bindings = render_folded_state(data_by_slot[17], table)
            write(table[1], text)
            symbols.update(bindings)
            special[17, table[2]] = (table[3], table[1], table[2]+0x6000)
    # Буквальные исходные байты трёх страниц табличного корня, значения не пересоздаются формулой.
    if "struct FRootCacheByte" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsRootCacheData import TABLE as ROOT_CACHE_TABLE, render as render_root_cache
        text, bindings = render_root_cache(data_by_slot[22])
        write(ROOT_CACHE_TABLE[1], text)
        symbols.update(bindings)
        special[22, 0] = (0x300, ROOT_CACHE_TABLE[1], 0xC000)
    # Три физические исходные компоненты в общей RAM ACTION.
    from ActionComponentWorkData import TABLE as COMPONENT_WORK_TABLE, render as render_component_work
    text, bindings = render_component_work(data_by_slot[17])
    write(COMPONENT_WORK_TABLE[1], text)
    symbols.update(bindings)
    special[17, 0x3B1E] = (0x3B27, COMPONENT_WORK_TABLE[1], 0x9B1E)
    # Физический знаковый рабочий вектор после соседнего отдельного блока.
    from ActionWorkVectorData import PATH as WORK_VECTOR, TRANSFORM_PATH, TRANSFORM_MODULE, render as render_work_vector
    text, bindings = render_work_vector(data_by_slot[17], 0x9B6F, TRANSFORM_MODULE, 'ActionPrepareBodyTransform')
    write(TRANSFORM_PATH, text)
    symbols.update(bindings)
    special[17, 0x3B6F] = (0x3B78, TRANSFORM_PATH, 0x9B6F)
    text, bindings = render_work_vector(data_by_slot[17])
    write(WORK_VECTOR, text)
    symbols.update(bindings)
    special[17, 0x3B78] = (0x3B81, WORK_VECTOR, 0x9B78)
    from ActionVisualEffectData import PATH as EFFECTS_PATH, START as EFFECTS_START, END as EFFECTS_END
    from ActionVisualEffectData import render as render_visual_effects
    text, bindings = render_visual_effects(data_by_slot[17])
    write(EFFECTS_PATH, text)
    symbols.update(bindings)
    special[17, EFFECTS_START] = (EFFECTS_END, EFFECTS_PATH, 0xA795)
    # Шесть начальных широких векторов, байты и вложенный физический формат сохраняются.
    from ActionWideVectorsData import PATH as WIDE_VECTORS, render as render_wide_vectors
    text, bindings = render_wide_vectors(data_by_slot[17])
    write(WIDE_VECTORS, text)
    symbols.update(bindings)
    special[17, 0x3B27] = (0x3B6F, WIDE_VECTORS, 0x9B27)
    # Двадцать шесть физических указателей класса до первого RET обработчиков.
    from ActionObjectStateHandlersData import TABLE as STATE_HANDLERS_TABLE, render as render_state_handlers
    text, bindings = render_state_handlers(data_by_slot[17])
    write(STATE_HANDLERS_TABLE[1], text)
    symbols.update(bindings)
    special[17, 0x8F50] = (0x8F7C, STATE_HANDLERS_TABLE[1], 0xEF50)
    from ActionClassHandlersData import TABLE as CLASS_HANDLERS_TABLE, render as render_class_handlers
    text, bindings = render_class_handlers(data_by_slot[17])
    write(CLASS_HANDLERS_TABLE[1], text)
    symbols.update(bindings)
    special[17, 0x72D] = (0x761, CLASS_HANDLERS_TABLE[1], 0x64F0)
    # Двести пятьдесят шесть исходных кодов отношения, без тригонометрического пересчёта.
    from ActionSignedRatioCodesData import TABLE as SIGNED_RATIO_CODES_TABLE, render as render_signed_ratio_codes
    text, bindings = render_signed_ratio_codes(data_by_slot[17])
    write(SIGNED_RATIO_CODES_TABLE[1], text)
    symbols.update(bindings)
    special[17, 0x3A00] = (0x3B00, SIGNED_RATIO_CODES_TABLE[1], 0x9A00)
    token_text, token_records = render_token_tables(language, names)
    write(TOKEN_TABLE_PATH, token_text)
    special[5, 0x935] = (0xA67, TOKEN_TABLE_PATH, 0xC935)
    phase_text, phase_symbols = render_phase_states(data_by_slot[3])
    write(PHASE_STATE_PATH, phase_text)
    symbols.update(phase_symbols)
    special[3, 0x98A] = (0x99C, PHASE_STATE_PATH, 0x6C8A)
    glyph_routes = []
    if re.search(r"\bstruct\s+FGlyphRoute\b", (ROOT / "Includes/Structs/Include.inc").read_text(encoding="utf-8"), re.I):
        route_text, route_symbols, glyph_routes = render_glyph_routes(data_by_slot[4], names)
        write(GLYPH_ROUTE_PATH, route_text)
        symbols.update(route_symbols)
        special[4, 0x3200] = (0x3400, GLYPH_ROUTE_PATH, 0x9200)
    pointer_texts, pointer_symbols, pointer_records = render_pointer_tables(data_by_slot[4])
    for path, text in pointer_texts.items():
        write(path, text)
    symbols.update(pointer_symbols)
    special[4, 0] = (0x300, POINTER_SPRITES, 0x6000)
    special[4, 0x821] = (0x831, POINTER_BACKGROUND, 0x6575)
    mouse_text, mouse_symbols = render_mouse_input(data_by_slot[4])
    write(MOUSE_INPUT_PATH, mouse_text)
    symbols.update(mouse_symbols)
    special[4, 0x831] = (0x83A, MOUSE_INPUT_PATH, 0x6585)
    input_texts, input_symbols = render_pointer_input(data_by_slot[4], names)
    for path, text in input_texts.items():
        write(path, text)
    symbols.update(input_symbols)
    special[4, 0x994] = (0x99A, INPUT_FLAGS, 0x66E8)
    special[4, 0x99A] = (0x9BA, INPUT_DIRECTIONS, 0x66EE)
    special[4, 0x39B6] = (0x39C2, INPUT_KEYS, 0x99B6)
    irq_texts, irq_symbols = render_station_irq_data(data_by_slot[4], names)
    for path, text in irq_texts.items():
        write(path, text)
    symbols.update(irq_symbols)
    special[4, 0x383B] = (0x383F, IRQ_COUNTER, 0x983B)
    special[4, 0x3C13] = (0x3C43, IRQ_STACK, 0x9C13)
    special[4, 0x4102] = (0x4116, WINDOW_CHAIN, 0xA102)
    key_text, key_symbols = render_matrix_keys(data_by_slot[4])
    write(MATRIX_KEYS, key_text)
    symbols.update(key_symbols)
    special[4, 0x36AA] = (0x3728, MATRIX_KEYS, 0x96AA)
    setting_texts, setting_symbols = render_settings(data_by_slot[4])
    for path, text in setting_texts.items():
        write(path, text)
    symbols.update(setting_symbols)
    special[4, 0x3728] = (0x3762, SETTINGS_TEXT, 0x9728)
    special[4, 0x39AE] = (0x39B6, SETTINGS_CHOICES, 0x99AE)
    special[4, 0x39C2] = (0x39C8, SETTINGS_COLORS, 0x99C2)
    special[4, 0x39C8] = (0x3A1E, SETTINGS_CONTROLS, 0x99C8)
    menu_text, menu_symbols, menu_end = render_context_menu(data_by_slot[4])
    write(CONTEXT_MENU_TEXT, menu_text)
    symbols.update(menu_symbols)
    special[4, 0x832E] = (menu_end, CONTEXT_MENU_TEXT, 0xE32E)
    random_text, random_symbols = render_random_states(data_by_slot[4])
    write(RANDOM_STATES, random_text)
    symbols.update(random_symbols)
    special[4, 0x48AC] = (0x48C1, RANDOM_STATES, 0xA8AC)
    signature_text, signature_symbols = render_signature(data_by_slot[4])
    write(CURRENT_SIGNATURE, signature_text)
    symbols.update(signature_symbols)
    special[4, 0x383F] = (0x3844, CURRENT_SIGNATURE, 0x983F)
    market_texts, market_symbols = render_market(data_by_slot[4])
    for path, text in market_texts.items():
        write(path, text)
    symbols.update(market_symbols)
    for start, end, path in MARKET_RANGES:
        special[4, start] = (end, path, start + 0x6000)
    clip_work_texts, clip_work_symbols = render_clip_work(data_by_slot[7])
    for path,text in clip_work_texts.items():
        write(path,text)
    symbols.update(clip_work_symbols)
    special[7, 0x1E2F] = (0x1E39, CLIP_ENDPOINTS, 0xDE2F)
    special[7, 0x1E6B] = (0x1E7B, CLIP_PRODUCTS, 0xDE6B)
    special[7, 0x1E3B] = (0x1E3C, CLIP_OUTPUT_SIZE, 0xDE3B)
    special[7, 0x1E39] = (0x1E3B, CLIP_CORNERS, 0xDE39)
    marker_sprite_texts,marker_sprite_symbols=render_marker_sprites(data_by_slot[7])
    for path,text in marker_sprite_texts.items():
        write(path,text)
    symbols.update(marker_sprite_symbols)
    for begin,end,path in MARKER_SPRITE_RANGES:
        special[7,begin-0xC000]=(end-0xC000,path,begin)
    animated_variant_texts,animated_variant_symbols=render_animated_variants(data_by_slot[7])
    for path,text in animated_variant_texts.items():
        write(path,text)
    symbols.update(animated_variant_symbols)
    for begin,end,path in ANIMATED_VARIANT_RANGES:
        special[7,begin]=(end,path,begin+0xC000)
    arc_workspace_texts,arc_workspace_symbols=render_arc_workspace(data_by_slot[7])
    for path,text in arc_workspace_texts.items():
        write(path,text)
    symbols.update(arc_workspace_symbols)
    special[7,0x1FAB]=(0x1FC3,ARC_WORKSPACE,0xDFAB)
    map_line_texts,map_line_symbols=render_map_line(data_by_slot[7])
    for path,text in map_line_texts.items():
        write(path,text)
    symbols.update(map_line_symbols)
    for start,end,path in MAP_LINE_RANGES:
        special[7,start-0xC000]=(end-0xC000,path,start)
    map_chain_texts,map_chain_symbols=render_map_chain_points(data_by_slot[7])
    for path,text in map_chain_texts.items():
        write(path,text)
    symbols.update(map_chain_symbols)
    for start,end,path in MAP_CHAIN_POINT_RANGES:
        special[7,start-0xC000]=(end-0xC000,path,start)
    auxiliary_map_texts,auxiliary_map_symbols=render_auxiliary_map(data_by_slot[4])
    for path,text in auxiliary_map_texts.items():
        write(path,text)
    symbols.update(auxiliary_map_symbols)
    for begin,end,path in AUXILIARY_MAP_RANGES:
        special[4,begin]=(end,path,begin+0x6000)
    stored_map_order_text, stored_map_order_symbols = render_stored_map_order(data_by_slot[4])
    write(STORED_MAP_ORDER, stored_map_order_text)
    symbols.update(stored_map_order_symbols)
    special[4, 0x3970] = (0x397B, STORED_MAP_ORDER, 0x9970)
    stored_map_point_text, stored_map_point_symbols = render_stored_map_points(data_by_slot[4])
    write(STORED_MAP_POINTS, stored_map_point_text)
    symbols.update(stored_map_point_symbols)
    special[4, 0x390A] = (0x3970, STORED_MAP_POINTS, 0x990A)
    mission_text, mission_text_symbols = render_mission_texts(data_by_slot[4])
    write(MISSION_TEXTS, mission_text)
    symbols.update(mission_text_symbols)
    special[4, 0x4B66] = (0x4C14, MISSION_TEXTS, 0xAB66)
    mission_messages, mission_message_symbols = render_mission_messages(data_by_slot[4])
    for path,text in mission_messages.items():
        write(path,text)
    symbols.update(mission_message_symbols)
    for begin,end,path,module in MISSION_MESSAGES:
        special[4, begin] = (end, path, begin + 0x5D54)
    system_prefix_text, system_prefix_symbols = render_system_prefixes(data_by_slot[7])
    write(SYSTEM_PREFIXES, system_prefix_text)
    symbols.update(system_prefix_symbols)
    special[7, 0x2721] = (0x2779, SYSTEM_PREFIXES, 0xE721)
    mission_offer_text, mission_offer_symbols = render_mission_offer(data_by_slot[4])
    write(MISSION_OFFER, mission_offer_text)
    symbols.update(mission_offer_symbols)
    special[4, 0x38B0] = (0x38C0, MISSION_OFFER, 0x98B0)
    player_rank_text, player_rank_symbols = render_player_ranks(data_by_slot[4])
    write(PLAYER_RANKS, player_rank_text)
    symbols.update(player_rank_symbols)
    special[4, 0x4CE3] = (0x4D35, PLAYER_RANKS, 0xACE3)
    action_key_text, action_key_symbols = render_action_key(data_by_slot[4])
    write(ACTION_FILE_KEY, action_key_text)
    symbols.update(action_key_symbols)
    special[4, 0x21B4] = (0x21BD, ACTION_FILE_KEY, 0x4248)
    final_key_text, final_key_symbols = render_final_key(data_by_slot[4])
    write(FINAL_FILE_KEY, final_key_text)
    symbols.update(final_key_symbols)
    special[4, 0x1119] = (0x1122, FINAL_FILE_KEY, 0x405C)
    expression_stack_text, expression_stack_symbols = render_expression_stack(data_by_slot[5])
    write(EXPRESSION_STACK, expression_stack_text)
    symbols.update(expression_stack_symbols)
    special[5, 0xA67] = (0xA7B, EXPRESSION_STACK, 0xCA67)
    assignment_text, assignment_symbols = render_assignment_scratch(data_by_slot[5])
    write(ASSIGNMENT_SCRATCH, assignment_text)
    symbols.update(assignment_symbols)
    special[5, 0xA7B] = (0xA81, ASSIGNMENT_SCRATCH, 0xCA7B)
    market_script_text, market_script_symbols, market_script_end = render_market_script(data_by_slot[5])
    write(MARKET_SCRIPT, market_script_text)
    symbols.update(market_script_symbols)
    special[5, MARKET_SCRIPT_START] = (market_script_end, MARKET_SCRIPT, 0xC000 + MARKET_SCRIPT_START)
    # Восстановление двух доказанных CP866-потоков описаний в отдельном кандидате.
    from PreviewDescriptionTables import TABLES as PREVIEW_TEXT_TABLES, render as render_preview_text
    for table in PREVIEW_TEXT_TABLES:
        _, path, start, end, _ = table
        text, labels = render_preview_text(data_by_slot[6], table)
        write(path, text)
        symbols.update(labels)
        special[6, start] = (end, path, 0xC000+start)
    # Подтверждённые ценовые строки D3D формируются только в отдельном кандидате.
    from PreviewPriceTable import PATH as PREVIEW_PRICE_PATH, START as PREVIEW_PRICE_START, END as PREVIEW_PRICE_END, render as render_preview_prices
    text, labels = render_preview_prices(data_by_slot[6])
    write(PREVIEW_PRICE_PATH, text)
    symbols.update(labels)
    special[6, PREVIEW_PRICE_START] = (PREVIEW_PRICE_END, PREVIEW_PRICE_PATH, 0xC000+PREVIEW_PRICE_START)
    # Исходные физические параметры, матрица и пары указателей, без подмены загрузочной инициализации.
    from PreviewSceneTables import TABLES as PREVIEW_SCENE_TABLES, render as render_preview_scene
    from PreviewDrawStateTable import TABLE as PREVIEW_DRAW_STATE_TABLE
    from PreviewEdgeData import TABLES as PREVIEW_EDGE_TABLES, MASK_PATH as EDGE_MASK_PATH, render_masks as render_edge_masks, render as render_edge_records
    from PreviewPolygonData import TABLES as PREVIEWPOLYGONDATA_TABLES, render as render_previewpolygondata
    from PreviewFaceGateData import TABLES as PREVIEWFACEGATEDATA_TABLES, render as render_previewfacegatedata
    from PreviewClipWorkData import TABLES as PREVIEWCLIPWORKDATA_TABLES, render as render_previewclipworkdata
    from PreviewClipProductData import TABLES as PREVIEWCLIPPRODUCTDATA_TABLES, render as render_previewclipproductdata
    from PreviewLineWorkData import TABLES as PREVIEWLINEWORKDATA_TABLES, render as render_previewlineworkdata
    from PreviewQueueRenderData import TABLES as PREVIEWQUEUERENDERDATA_TABLES, render as render_previewqueuerenderdata
    from PreviewFrameData import TABLES as PREVIEWFRAMEDATA_TABLES, render as render_previewframedata
    for table in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE, *PREVIEW_EDGE_TABLES, *PREVIEWPOLYGONDATA_TABLES, *PREVIEWFACEGATEDATA_TABLES, *PREVIEWCLIPWORKDATA_TABLES, *PREVIEWCLIPPRODUCTDATA_TABLES, *PREVIEWLINEWORKDATA_TABLES, *PREVIEWQUEUERENDERDATA_TABLES, *PREVIEWFRAMEDATA_TABLES):
        _, path, start, end, _, _, _ = table
        text, labels = (render_previewframedata if table in PREVIEWFRAMEDATA_TABLES else render_previewqueuerenderdata if table in PREVIEWQUEUERENDERDATA_TABLES else render_previewlineworkdata if table in PREVIEWLINEWORKDATA_TABLES else render_previewclipproductdata if table in PREVIEWCLIPPRODUCTDATA_TABLES else render_previewclipworkdata if table in PREVIEWCLIPWORKDATA_TABLES else render_previewfacegatedata if table in PREVIEWFACEGATEDATA_TABLES else render_previewpolygondata if table in PREVIEWPOLYGONDATA_TABLES else render_edge_records if table in PREVIEW_EDGE_TABLES else render_preview_scene)(data_by_slot[6], table)
        write(path, text)
        symbols.update(labels)
        special[6, start] = (end, path, 0xC000+start)
    # Исходные заголовки и группы моделей, ручной экспорт здесь не запускается.
    from PreviewModelGroupTables import tables as preview_model_tables, render as render_preview_model
    for model in preview_model_tables(data_by_slot[6]):
        text, labels = render_preview_model(data_by_slot[6], model)
        write(model['path'], text)
        symbols.update(labels)
        special[6, model['start']] = (model['end'], model['path'], model['pointer'])
    # Исходный рабочий буфер проекции, экспорт на этапе исследования не запускается.
    from PreviewProjectedVertexTable import PATH as PROJECTED_PATH, render as render_projected
    text, labels = render_projected(data_by_slot[6])
    write(PROJECTED_PATH, text)
    symbols.update(labels)
    special[6,0x600] = (0x700,PROJECTED_PATH,0xC600)
    text, labels = render_edge_masks(data_by_slot[6])
    write(EDGE_MASK_PATH,text)
    symbols.update(labels)
    special[6,0xDB0] = (0xDC0,EDGE_MASK_PATH,0xCDB0)
    # Исходная страница свёрнутых квадратов, формула отдельно подтверждена всеми 256 байтами.
    from PreviewSquareTable import PATH as PREVIEW_SQUARE_PATH, START as PREVIEW_SQUARE_START, END as PREVIEW_SQUARE_END, render as render_preview_square
    text, labels = render_preview_square(data_by_slot[6])
    write(PREVIEW_SQUARE_PATH, text)
    symbols.update(labels)
    special[6, PREVIEW_SQUARE_START] = (PREVIEW_SQUARE_END, PREVIEW_SQUARE_PATH, 0xC300)
    # Исходные невыделенные узлы очереди D3D, активные ссылки создаёт код вставки.
    from PreviewQueueTable import PATH as PREVIEW_QUEUE_PATH, START as PREVIEW_QUEUE_START, END as PREVIEW_QUEUE_END, render as render_preview_queue
    text, labels = render_preview_queue(data_by_slot[6])
    write(PREVIEW_QUEUE_PATH, text)
    symbols.update(labels)
    special[6, PREVIEW_QUEUE_START] = (PREVIEW_QUEUE_END, PREVIEW_QUEUE_PATH, 0xC700)
    # Физические пары начальных моделей для шестнадцати уровней системы.
    from ModelAvailabilityTable import PATH as MODEL_AVAILABILITY_PATH, START as MODEL_AVAILABILITY_START, END as MODEL_AVAILABILITY_END, render as render_model_availability
    text, labels = render_model_availability(data_by_slot[4])
    write(MODEL_AVAILABILITY_PATH, text)
    symbols.update(labels)
    special[4, MODEL_AVAILABILITY_START] = (MODEL_AVAILABILITY_END, MODEL_AVAILABILITY_PATH, 0x6000+MODEL_AVAILABILITY_START)
    # Выделение подтверждённого PT3 от исходного адреса #E700 до логического конца MUZ1.C.
    music_end = next(item["length"] for item in disk["entries"] if item["slot"] == 10)
    binary_resources = {(10, 0xC00): (music_end, "Source/Music/Resources/Antichrist.pt3", "PT3")}
    if re.search(r"\bstruct\s+FMusicModuleHeader\b", (ROOT/"Includes/Structs/Include.inc").read_text('utf-8'), re.I):
        from MusicCompositionSource import descriptions as composition_descriptions, render as render_composition
        composition = data_by_slot[10][0xC00:music_end]
        for description in composition_descriptions(composition):
            text, bindings = render_composition(composition, description)
            write(description['path'], text)
            symbols.update(bindings)
            start, length = description['offset'], description['length']
            special[10, 0xC00+start] = (0xC00+start+length, description['path'], 0xE700+start)
        del binary_resources[10, 0xC00]
    binary_resources[7, 0x2900] = (0x2B00, "Source/Map/Resources/Squares.bin", "Z80_SPLIT_WORD_SQUARES")
    binary_resources[7, 0x2B00] = (0x2E00, "Source/Map/Resources/RootSeeds.bin", "ROOT_SEED_AND_SPLIT_OFFSET_PAGES")
    binary_resources[4, 0x2900] = (0x2A00, "Source/Station/Resources/FontWidths.bin", "FONT_WIDTHS_256")
    binary_resources[4, 0x2A00] = (0x3200, "Source/Station/Resources/FontGlyphs.bin", "FONT_256_GLYPHS_8_ROWS")
    for frame in range(3):
        offset = 0x2A9 + frame * 0x1800
        binary_resources[(29, offset)] = (offset + 0x1800, f"Source/Final/Resources/Frame{frame}.bitmap", "ZX_BITMAP")

    # Сохранение каждого исходного байта ровно один раз, без подстановки целых программ из оригинала.
    source_map = []
    units = []
    # Подготовка физических записей отдельной копии 3DPART только внутри кандидата экспорта.
    from ThreeDOverlayData import export_data as export_three_d_overlay_data
    export_three_d_overlay_data(data_by_slot[19],special,write,symbols)
    screen_records = []
    for item in disk["entries"]:
        if item["deleted"]:
            continue
        slot = item["slot"]
        data = data_by_slot[slot]
        stem = re.sub(r"[^A-Za-z0-9]", "", item["name"]) or "File"
        unit_path = f"Source/Files/{slot:02d}_{stem}.inc"
        lines = ["; -----------------------------------------",
                 f"; запись {slot}, {item['name']}.{item['extension']}",
                 f"; логическая длина {item['length']}, полный секторный размер {len(data)}",
                 "; -----------------------------------------"]
        offset = 0
        part = 0
        chunks = [b for b in BLOCKS if b["slot"] == slot]
        while offset < len(data):
            if (slot, offset) in binary_resources:
                end, resource_path, resource_format = binary_resources[(slot, offset)]
                target = ROOT / resource_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data[offset:end])
                lines.extend([asm(f"assert $ == #{offset:04X}"),
                              asm("; исходный ресурс " + resource_format),
                              asm('incbin "../' + resource_path[7:] + '"')])
                source_map.append(dict(slot=slot, offset=offset, length=end-offset, kind="binary_resource",
                                       path=resource_path, origin=next((b["origin"] + offset - b["offset"] for b in chunks
                                           if b["offset"] <= offset < b["offset"] + b["length"]), None), format=resource_format,
                                       sha256=hashlib.sha256(data[offset:end]).hexdigest()))
                offset = end
                continue
            if (slot, offset) in special:
                end, path, origin = special[(slot,offset)]
                lines.extend([asm(f"assert $ == #{offset:04X}"), asm(f"disp #{origin:04X}"),
                              asm('include "../'+path[7:]+'"'), asm("ent")])
                source_map.append(dict(slot=slot,offset=offset,length=end-offset,kind="typed_data",path=path,
                                       origin=origin,sha256=hashlib.sha256(data[offset:end]).hexdigest()))
                offset = end
                continue
            if offset == 0 and slot in (9, 25, 26, 27, 28):
                sizes = ([13, 11, 11, 12, 8, 14, 19, 15, 15, 13, 19, 12, 16, 20, 21, 20]
                         if slot == 9 else [len(data)//256])
                include, records = export_screens(slot, data, sizes)
                screen_records.extend(records)
                lines.append(asm('include "../' + include[7:] + '"'))
                source_map.append(dict(slot=slot, offset=0, length=len(data), kind="resource",
                                       path=include, origin=None,
                                       sha256=hashlib.sha256(data).hexdigest()))
                offset = len(data)
                continue
            found = instructions.get((slot, offset))
            if found:
                function, first = found
                size = function["end_offset"] - offset
                lines.extend([asm(f"assert $ == #{offset:04X}"),
                              asm(f"disp #{first['address']:04X}"),
                              asm('include "../' + function["path"][7:] + '"',
                                  f"({include_order[function['path']]}) жёсткий порядок, последовательное исполнение"
                                  if function["path"] in include_order else None),
                              asm("ent")])
                source_map.append(dict(slot=slot, offset=offset, length=size, kind="code",
                                       path=function["path"], origin=first["address"],
                                       sha256=hashlib.sha256(data[offset:offset+size]).hexdigest()))
                offset += size
            else:
                begin = offset
                while (offset < len(data) and (slot, offset) not in instructions
                       and (slot, offset) not in special and (slot, offset) not in binary_resources):
                    offset += 1
                size = offset - begin
                binary_path = f"Source/Resources/{slot:02d}_{stem}/Unclassified{part:03d}.bin"
                path = ROOT / binary_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data[begin:offset])
                lines.extend([asm(f"assert $ == #{begin:04X}"),
                              asm("; Unknown, исходные байты вне подтверждённого прямого потока управления"),
                              asm('incbin "../' + binary_path[7:] + '"')])
                source_map.append(dict(slot=slot, offset=begin, length=size, kind="unclassified",
                                       path=binary_path, origin=None,
                                       sha256=hashlib.sha256(data[begin:offset]).hexdigest()))
                part += 1
        lines.append(asm(f"assert $ == #{len(data):04X}"))
        write(unit_path, "\n".join(lines))
        units.append(dict(slot=slot, path=unit_path, offset=item["offset"], length=len(data)))

    # Создание сборочной точки по схеме SAVETRD и встроенного упаковщика из DisasmElite.
    builder = ["; -----------------------------------------", "; сборка исходного Awakenv02.trd средствами SjASMPlus",
               "; адреса DISP восстанавливают только размещение, заданное оригинальными загрузчиками",
               "; -----------------------------------------", asm("DEVICE ZXSPECTRUM48"),
               asm('include "../Includes/Const/Include.inc"'),
               asm('include "../Includes/Structs/Include.inc"'),
               asm('include "../Includes/Variables/Include.inc"'),
               asm("LUA PASS1"), '                    dofile("Tools/pack.lua")',
               "                    reset_report()", asm("ENDLUA"),
               asm('EMPTYTRD "Awakenv02.trd", "AWAKEN"')]
    for unit in units:
        builder.extend(["", asm(f"; сборка исходных секторов записи {unit['slot']}"),
                        asm("ORG 0"), asm('include "../' + unit["path"] + '"'),
                        asm(f"assert $ == #{unit['length']:04X}"),
                        asm(f'SAVETRD "Awakenv02.trd", "S{unit["slot"]:02d}.C", 0, {unit["length"]}')])
    builder.extend(["", asm("IF _ERRORS = 0"), asm("LUA PASS3"),
                    '                    dofile("Tools/pack.lua")',
                    "                    finish_image()", asm("ENDLUA"), asm("ENDIF")])
    write("Builder/Main.asm", "\n".join(builder))

    # Сохранение реестров для отдельной проверки исходников и документации.
    report = ROOT / "Tools/Disasm/Reports"
    public = [{k:v for k,v in f.items() if k != "instructions"} for f in functions]
    for filename, value in (("Functions.json", public), ("SourceMap.json", source_map),
                            ("Symbols.json", symbols), ("BuildUnits.json", units),
                            ("Screens.json", screen_records), ("InterfaceItems.json", interface),
                            ("TokenBindings.json", token_records), ("GlyphRoutes.json", glyph_routes), ("PointerRows.json", pointer_records)):
        write(str((report / filename).relative_to(ROOT)), json.dumps(value, ensure_ascii=False, indent=2))
    preserved = [c for c in disk["components"] if not any(
        c["offset"] == u["offset"] for u in units)]
    layout = ["-- Исходные физические компоненты, активные файлы собираются из Source.", "return {"]
    for component in preserved:
        layout.append(f'    {{offset={component["offset"]}, size={component["size"]}, path="{component["path"]}"}},')
    layout.append("}")
    write("Tools/Disasm/Disk/Layout.lua", "\n".join(layout))
    build_units = ["-- Порядок SAVETRD и исходные размещения активных файлов.", "return {"]
    for unit in units:
        build_units.append(f'    {{slot={unit["slot"]}, offset={unit["offset"]}, size={unit["length"]}}},')
    build_units.append("}")
    write("Tools/Disasm/Disk/BuildUnits.lua", "\n".join(build_units))
    print(f"Sources: {len(functions)} fragments, {len(units)} active disk allocations")
    print(f"Described: {sum(f['semantic_status']=='described' for f in functions)}")


from ControlsTextQueueFacts import COMMENTS as CONTROLS_TEXT_QUEUE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_TEXT_QUEUE_COMMENTS)


from ActionTextQueueFacts import COMMENTS as ACTION_TEXT_QUEUE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_TEXT_QUEUE_COMMENTS)


from ControlsTextDisplayFacts import COMMENTS as CONTROLS_TEXT_DISPLAY_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_TEXT_DISPLAY_COMMENTS)


from ControlsBcdCounterFacts import COMMENTS as CONTROLS_BCD_COUNTER_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_BCD_COUNTER_COMMENTS)


from ControlsMarkerFacts import COMMENTS as CONTROLS_MARKER_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_MARKER_COMMENTS)


from ControlsBufferCopyFacts import COMMENTS as CONTROLS_BUFFER_COPY_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_BUFFER_COPY_COMMENTS)


from ControlsBufferPointsFacts import COMMENTS as CONTROLS_BUFFER_POINTS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_BUFFER_POINTS_COMMENTS)


from ActionBitmapTablesFacts import COMMENTS as ACTION_BITMAP_COMMENTS
REGION_COMMENTS.setdefault("ActionBoot",{}).update(ACTION_BITMAP_COMMENTS)


from ControlsDivisionFacts import COMMENTS as CONTROLS_DIVISION_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_DIVISION_COMMENTS)


from ControlsSpanMasksFacts import COMMENTS as CONTROLS_SPAN_MASKS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SPAN_MASKS_COMMENTS)


from ControlsPointRespawnFacts import COMMENTS as CONTROLS_POINT_RESPAWN_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_POINT_RESPAWN_COMMENTS)


from ControlsPointMotionFacts import COMMENTS as CONTROLS_POINT_MOTION_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_POINT_MOTION_COMMENTS)


from ControlsEvenSpanFacts import COMMENTS as CONTROLS_EVEN_SPAN_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_EVEN_SPAN_COMMENTS)


from ControlsInteriorRowsFacts import COMMENTS as CONTROLS_INTERIOR_ROWS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_INTERIOR_ROWS_COMMENTS)


from ControlsSquaresFacts import COMMENTS as CONTROLS_SQUARES_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SQUARES_COMMENTS)


from ControlsRasterStepFacts import COMMENTS as CONTROLS_RASTER_STEP_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_RASTER_STEP_COMMENTS)


from ControlsPushSpansFacts import COMMENTS as CONTROLS_PUSH_SPANS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PUSH_SPANS_COMMENTS)


from ControlsComponentCompareFacts import COMMENTS as CONTROLS_COMPONENT_COMPARE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_COMPONENT_COMPARE_COMMENTS)


from ControlsSmallMasksFacts import COMMENTS as CONTROLS_SMALL_MASKS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SMALL_MASKS_COMMENTS)


from ControlsSmallBodiesFacts import COMMENTS as CONTROLS_SMALL_BODIES_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SMALL_BODIES_COMMENTS)


from ControlsCircleSetupFacts import COMMENTS as CONTROLS_CIRCLE_SETUP_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CIRCLE_SETUP_COMMENTS)


from ControlsCircleSpanFacts import COMMENTS as CONTROLS_CIRCLE_SPAN_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CIRCLE_SPAN_COMMENTS)


from ControlsWordRandomFacts import COMMENTS as CONTROLS_WORD_RANDOM_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_WORD_RANDOM_COMMENTS)


from ActionRegionTypeFacts import COMMENTS as ACTION_REGION_TYPE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_REGION_TYPE_COMMENTS)


from ControlsSeededParametersFacts import COMMENTS as CONTROLS_SEEDED_PARAMETERS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SEEDED_PARAMETERS_COMMENTS)


from ControlsParameterTablesFacts import COMMENTS as CONTROLS_PARAMETER_TABLES_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PARAMETER_TABLES_COMMENTS)


from ActionApplyParametersFacts import COMMENTS as ACTION_APPLY_PARAMETERS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_APPLY_PARAMETERS_COMMENTS)


from ActionParameterActivationFacts import COMMENTS as ACTION_PARAMETER_ACTIVATION_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_PARAMETER_ACTIVATION_COMMENTS)


from ControlsParameterActivationFacts import COMMENTS as CONTROLS_PARAMETER_ACTIVATION_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PARAMETER_ACTIVATION_COMMENTS)


from ControlsThreeRowGlyphFacts import COMMENTS as CONTROLS_THREE_ROW_GLYPH_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_THREE_ROW_GLYPH_COMMENTS)


from ControlsGlyphIndicatorsFacts import COMMENTS as CONTROLS_GLYPH_INDICATORS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_GLYPH_INDICATORS_COMMENTS)

from ControlsRasterBackgroundFacts import COMMENTS as CONTROLS_RASTER_BACKGROUND_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_RASTER_BACKGROUND_COMMENTS)

from ControlsObjectProjectionFacts import COMMENTS as CONTROLS_OBJECT_PROJECTION_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_OBJECT_PROJECTION_COMMENTS)


from ControlsSixRowGaugeFacts import COMMENTS as CONTROLS_SIX_ROW_GAUGE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_SIX_ROW_GAUGE_COMMENTS)


from ActionGaugeWrapperFacts import COMMENTS as ACTION_GAUGE_WRAPPER_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_GAUGE_WRAPPER_COMMENTS)


from ActionPreferredByteFacts import COMMENTS as ACTION_PREFERRED_BYTE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_PREFERRED_BYTE_COMMENTS)


from ActionPanelGaugesFacts import COMMENTS as ACTION_PANEL_GAUGES_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_PANEL_GAUGES_COMMENTS)


from ActionNearZeroWordFacts import COMMENTS as ACTION_NEAR_ZERO_WORD_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_NEAR_ZERO_WORD_COMMENTS)

from ActionKeyScanFrameFacts import COMMENTS as ACTION_KEY_SCAN_FRAME_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_SCAN_FRAME_COMMENTS)

from ActionMissileStockFacts import COMMENTS as ACTION_MISSILE_STOCK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_STOCK_COMMENTS)

from ActionMissileLaunchFacts import COMMENTS as ACTION_MISSILE_LAUNCH_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_LAUNCH_COMMENTS)

from ActionMissileConsumeFacts import COMMENTS as ACTION_MISSILE_CONSUME_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_CONSUME_COMMENTS)

from ActionTypeDeltaFacts import COMMENTS as ACTION_TYPE_DELTA_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_TYPE_DELTA_COMMENTS)

from ActionRecordIndexFacts import COMMENTS as ACTION_RECORD_INDEX_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_INDEX_COMMENTS)


from ActionRecordSearchFacts import COMMENTS as ACTION_RECORD_SEARCH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_SEARCH_COMMENTS)


from ActionRecordIteratorFacts import COMMENTS as ACTION_RECORD_ITERATOR_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_ITERATOR_COMMENTS)

from ActionPatchSwapFacts import COMMENTS as ACTION_PATCH_SWAP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PATCH_SWAP_COMMENTS)


from ActionScaledMultiplyFacts import COMMENTS as ACTION_SCALED_MULTIPLY_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SCALED_MULTIPLY_COMMENTS)

from ActionPatchedVectorFacts import COMMENTS as ACTION_PATCHED_VECTOR_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PATCHED_VECTOR_COMMENTS)

from ActionVectorWrapperFacts import COMMENTS as ACTION_VECTOR_WRAPPER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VECTOR_WRAPPER_COMMENTS)

from ActionMissileCreationFacts import COMMENTS as ACTION_MISSILE_CREATION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_CREATION_COMMENTS)

from ActionMissileRequestsFacts import COMMENTS as ACTION_MISSILE_REQUESTS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_REQUESTS_COMMENTS)


from ActionAyEffectsFacts import COMMENTS as ACTION_AY_EFFECTS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_AY_EFFECTS_COMMENTS)


from ActionRecordLinkEventFacts import COMMENTS as ACTION_RECORD_LINK_EVENT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_LINK_EVENT_COMMENTS)

from ActionProjectedCaptureFacts import COMMENTS as ACTION_PROJECTED_CAPTURE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTED_CAPTURE_COMMENTS)

from ActionLogarithmTableFacts import COMMENTS as ACTION_LOGARITHM_TABLE_COMMENTS
REGION_COMMENTS.setdefault('ActionBoot',{}).update(ACTION_LOGARITHM_TABLE_COMMENTS)

from ActionExponentialTableFacts import COMMENTS as ACTION_EXPONENTIAL_TABLE_COMMENTS
REGION_COMMENTS.setdefault('ActionBoot',{}).update(ACTION_EXPONENTIAL_TABLE_COMMENTS)


from ActionLogRatioFacts import COMMENTS as ACTION_LOG_RATIO_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_LOG_RATIO_COMMENTS)


from ActionObjectHeaderFacts import COMMENTS as ACTION_OBJECT_HEADER_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_OBJECT_HEADER_COMMENTS)

from ActionScaleHeaderFacts import COMMENTS as ACTION_SCALE_HEADER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_SCALE_HEADER_COMMENTS)

from ActionProjectedBoundsFacts import COMMENTS as ACTION_PROJECTED_BOUNDS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTED_BOUNDS_COMMENTS)

from ActionProjectionClipFacts import COMMENTS as ACTION_PROJECTION_CLIP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTION_CLIP_COMMENTS)

from ActionVectorReverseFacts import COMMENTS as ACTION_VECTOR_REVERSE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VECTOR_REVERSE_COMMENTS)

from ActionStationTransferFacts import COMMENTS as ACTION_STATION_TRANSFER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_STATION_TRANSFER_COMMENTS)

from ActionCloseRecordFacts import COMMENTS as ACTION_CLOSE_RECORD_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLOSE_RECORD_COMMENTS)


from ActionCloseBoundsFacts import COMMENTS as ACTION_CLOSE_BOUNDS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLOSE_BOUNDS_COMMENTS)

from ActionAimFollowFacts import COMMENTS as ACTION_AIM_FOLLOW_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_AIM_FOLLOW_COMMENTS)


from ActionRenderQueueInsertFacts import COMMENTS as ACTION_RENDER_QUEUE_INSERT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RENDER_QUEUE_INSERT_COMMENTS)

from ActionRenderContinuationFacts import COMMENTS as ACTION_RENDER_CONTINUATION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RENDER_CONTINUATION_COMMENTS)


from ActionRenderQueueControlFacts import COMMENTS as ACTION_RENDER_QUEUE_CONTROL_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RENDER_QUEUE_CONTROL_COMMENTS)

from ActionRenderCoefficientsFacts import COMMENTS as ACTION_RENDER_COEFFICIENTS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RENDER_COEFFICIENTS_COMMENTS)


from ActionRenderMatrixFacts import COMMENTS as ACTION_RENDER_MATRIX_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RENDER_MATRIX_COMMENTS)

from ActionObjectCopyFacts import COMMENTS as ACTION_OBJECT_COPY_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_COPY_COMMENTS)

from ActionPerspectiveFacts import COMMENTS as ACTION_PERSPECTIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PERSPECTIVE_COMMENTS)

from ActionVertexGroupFacts import COMMENTS as ACTION_VERTEX_GROUP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VERTEX_GROUP_COMMENTS)

from ActionVertexProductsFacts import COMMENTS as ACTION_VERTEX_PRODUCTS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VERTEX_PRODUCTS_COMMENTS)

from ActionObjectVerticesFacts import COMMENTS as ACTION_OBJECT_VERTICES_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_VERTICES_COMMENTS)

from ActionVertexAbortFacts import COMMENTS as ACTION_VERTEX_ABORT_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VERTEX_ABORT_COMMENTS)

from ActionVertexCodesFacts import COMMENTS as ACTION_VERTEX_CODES_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VERTEX_CODES_COMMENTS)

from ActionListedCodesFacts import COMMENTS as ACTION_LISTED_CODES_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_LISTED_CODES_COMMENTS)


from ActionSignedMultiplyFacts import COMMENTS as ACTION_SIGNED_MULTIPLY_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SIGNED_MULTIPLY_COMMENTS)

from ActionFaceOrientationFacts import COMMENTS as ACTION_FACE_ORIENTATION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_FACE_ORIENTATION_COMMENTS)


from ActionSignedDivisionFacts import COMMENTS as ACTION_SIGNED_DIVISION_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SIGNED_DIVISION_COMMENTS)


from ActionClipProductsFacts import COMMENTS as ACTION_CLIP_PRODUCTS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLIP_PRODUCTS_COMMENTS)


from ActionClipIntersectionsFacts import COMMENTS as ACTION_CLIP_INTERSECTIONS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLIP_INTERSECTIONS_COMMENTS)


from ActionClipComparisonsFacts import COMMENTS as ACTION_CLIP_COMPARISONS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLIP_COMPARISONS_COMMENTS)


from ActionClipPointWritersFacts import COMMENTS as ACTION_CLIP_POINT_WRITERS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLIP_POINT_WRITERS_COMMENTS)


from ActionClipCasesFacts import COMMENTS as ACTION_CLIP_CASES_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLIP_CASES_COMMENTS)


from ActionPolygonFacts import COMMENTS as ACTION_POLYGON_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_POLYGON_COMMENTS)


from ActionSingleEdgeFacts import COMMENTS as ACTION_SINGLE_EDGE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SINGLE_EDGE_COMMENTS)

from ActionLineRasterFacts import COMMENTS as ACTION_LINE_RASTER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_LINE_RASTER_COMMENTS)

from ActionPolygonPreparationFacts import COMMENTS as ACTION_POLYGON_PREPARATION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_PREPARATION_COMMENTS)

from ActionPolygonRowSelectionFacts import COMMENTS as ACTION_POLYGON_ROW_SELECTION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_ROW_SELECTION_COMMENTS)

from ActionPolygonLeftEdgeFacts import COMMENTS as ACTION_POLYGON_LEFT_EDGE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_LEFT_EDGE_COMMENTS)

from ActionPolygonRightShortStepFacts import COMMENTS as ACTION_POLYGON_RIGHT_SHORT_STEP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_RIGHT_SHORT_STEP_COMMENTS)

from ActionPolygonRightEdgeFacts import COMMENTS as ACTION_POLYGON_RIGHT_EDGE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_RIGHT_EDGE_COMMENTS)

from ActionPolygonFillRowsFacts import COMMENTS as ACTION_POLYGON_FILL_ROWS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_FILL_ROWS_COMMENTS)

from ActionPolygonSelectRightFacts import COMMENTS as ACTION_POLYGON_SELECT_RIGHT_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_SELECT_RIGHT_COMMENTS)

from ActionPolygonWrapLeftFacts import COMMENTS as ACTION_POLYGON_WRAP_LEFT_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_WRAP_LEFT_COMMENTS)

from ActionPolygonWrapRightFacts import COMMENTS as ACTION_POLYGON_WRAP_RIGHT_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_WRAP_RIGHT_COMMENTS)

from ActionPolygonWrapLeftTopFacts import COMMENTS as ACTION_POLYGON_WRAP_LEFT_TOP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_WRAP_LEFT_TOP_COMMENTS)

from ActionPolygonWrapRightTopFacts import COMMENTS as ACTION_POLYGON_WRAP_RIGHT_TOP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_WRAP_RIGHT_TOP_COMMENTS)

from ActionPolygonReturnFacts import COMMENTS as ACTION_POLYGON_RETURN_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_POLYGON_RETURN_COMMENTS)

from ActionPacketRendererFacts import COMMENTS as ACTION_PACKET_RENDERER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PACKET_RENDERER_COMMENTS)

from ActionClippedPacketRendererFacts import COMMENTS as ACTION_CLIPPED_PACKET_RENDERER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLIPPED_PACKET_RENDERER_COMMENTS)


from ActionQueuedObjectFacts import COMMENTS as ACTION_QUEUED_OBJECT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_QUEUED_OBJECT_COMMENTS)


from ActionWorkBufferFacts import COMMENTS as ACTION_WORK_BUFFER_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_WORK_BUFFER_COMMENTS)

from ThreeDOverlayMirrorFacts import COMMENTS as THREED_OVERLAY_COMMENTS
REGION_COMMENTS["ThreeD"]=dict(THREED_OVERLAY_COMMENTS)


from ActionUnpackFacts import COMMENTS as ACTION_UNPACK_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_UNPACK_COMMENTS)


from IntroScreenFacts import COMMENTS as INTRO_SCREEN_COMMENTS
REGION_COMMENTS.setdefault('IntroUnpack', {}).update(INTRO_SCREEN_COMMENTS)


from IntroLookupTransferFacts import COMMENTS as INTRO_LOOKUP_TRANSFER_COMMENTS
REGION_COMMENTS.setdefault('Intro', {}).update(INTRO_LOOKUP_TRANSFER_COMMENTS)


from IntroWaitInterruptFacts import COMMENTS as INTRO_WAIT_INTERRUPT_COMMENTS
REGION_COMMENTS.setdefault('Intro', {}).update(INTRO_WAIT_INTERRUPT_COMMENTS)


from IntroPresentAttributesFacts import COMMENTS as INTRO_PRESENT_ATTRIBUTES_COMMENTS
REGION_COMMENTS.setdefault('Intro', {}).update(INTRO_PRESENT_ATTRIBUTES_COMMENTS)


from IntroInterlacedFrameFacts import COMMENTS as INTRO_INTERLACED_FRAME_COMMENTS
REGION_COMMENTS.setdefault('Intro', {}).update(INTRO_INTERLACED_FRAME_COMMENTS)


from IntroLookupContinuationFacts import COMMENTS as INTRO_LOOKUP_CONTINUATION_COMMENTS
REGION_COMMENTS.setdefault('Intro', {}).update(INTRO_LOOKUP_CONTINUATION_COMMENTS)


from ActionFoldedRandomFacts import COMMENTS as ACTION_FOLDED_RANDOM_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_FOLDED_RANDOM_COMMENTS)

from ActionRandomClusterFacts import COMMENTS as ACTION_RANDOM_CLUSTER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RANDOM_CLUSTER_COMMENTS)


from ActionRecordReuseFacts import COMMENTS as ACTION_RECORD_REUSE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_REUSE_COMMENTS)


from ActionOffsetRestoreFacts import COMMENTS as ACTION_OFFSET_RESTORE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_OFFSET_RESTORE_COMMENTS)

from ActionRecordSelectionFacts import COMMENTS as ACTION_RECORD_SELECTION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_SELECTION_COMMENTS)


from ActionRecordScaleFacts import COMMENTS as ACTION_RECORD_SCALE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_SCALE_COMMENTS)

from ActionIYRecordReuseFacts import COMMENTS as ACTIONIY_RECORD_REUSE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTIONIY_RECORD_REUSE_COMMENTS)

from ActionClassReuseFacts import COMMENTS as ACTION_CLASS_REUSE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS_REUSE_COMMENTS)


from ActionRejectRecordFacts import COMMENTS as ACTION_REJECT_RECORD_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_REJECT_RECORD_COMMENTS)

from ActionRecordWarningReturnFacts import COMMENTS as ACTION_RECORD_WARNING_RETURN_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_WARNING_RETURN_COMMENTS)


from ActionRecordUpdateFacts import COMMENTS as ACTION_RECORD_UPDATE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_UPDATE_COMMENTS)


from ActionRecordBaseResetFacts import COMMENTS as ACTION_RECORD_BASE_RESET_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_BASE_RESET_COMMENTS)


from ActionClass14ReuseFacts import COMMENTS as ACTION_CLASS14_REUSE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLASS14_REUSE_COMMENTS)


from ActionBankedBufferInitFacts import COMMENTS as ACTION_BANKED_BUFFER_INIT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BANKED_BUFFER_INIT_COMMENTS)


from ActionThirdGlyphPublishFacts import COMMENTS as ACTION_THIRD_GLYPH_PUBLISH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_THIRD_GLYPH_PUBLISH_COMMENTS)

from ActionThirdGlyphStackFacts import COMMENTS as ACTION_THIRD_GLYPH_STACK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_THIRD_GLYPH_STACK_COMMENTS)


from ActionThirdGlyphVectorFacts import COMMENTS as ACTION_THIRD_GLYPH_VECTOR_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_THIRD_GLYPH_VECTOR_COMMENTS)


from ActionCachedRootFacts import COMMENTS as ACTION_CACHED_ROOT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CACHED_ROOT_COMMENTS)


from ActionComponentEncodingFacts import COMMENTS as ACTION_COMPONENT_ENCODING_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_COMPONENT_ENCODING_COMMENTS)

from ActionComponentStackFacts import COMMENTS as ACTION_COMPONENT_STACK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_COMPONENT_STACK_COMMENTS)


from ActionComponentTransformFacts import COMMENTS as ACTION_COMPONENT_TRANSFORM_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_COMPONENT_TRANSFORM_COMMENTS)


from ControlsProjectionAlgorithmFacts import COMMENTS as CONTROLS_PROJECTION_ALGORITHM_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PROJECTION_ALGORITHM_COMMENTS)


from ControlsProjectionGateFacts import COMMENTS as CONTROLS_PROJECTION_GATE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PROJECTION_GATE_COMMENTS)


from ActionClassDispatchFacts import COMMENTS as ACTION_CLASS_DISPATCH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLASS_DISPATCH_COMMENTS)

from ActionLinkOverrideFacts import COMMENTS as ACTION_LINK_OVERRIDE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_LINK_OVERRIDE_COMMENTS)

from ActionRecordsExcept6And7Facts import COMMENTS as ACTION_RECORDS_EXCEPT6_AND7_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORDS_EXCEPT6_AND7_COMMENTS)

from ActionRecords6Or7Facts import COMMENTS as ACTION_RECORDS6_OR7_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORDS6_OR7_COMMENTS)

from ActionRecords5Or14Facts import COMMENTS as ACTION_RECORDS5_OR14_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORDS5_OR14_COMMENTS)

from ActionRandomFilteredRecordFacts import COMMENTS as ACTION_RANDOM_FILTERED_RECORD_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RANDOM_FILTERED_RECORD_COMMENTS)

from ActionClass9LinkFacts import COMMENTS as ACTION_CLASS9_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS9_LINK_COMMENTS)

from ActionIgnoredClassesFacts import COMMENTS as ACTION_IGNORED_CLASSES_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_IGNORED_CLASSES_COMMENTS)

from ActionClass0LinkFacts import COMMENTS as ACTION_CLASS0_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS0_LINK_COMMENTS)

from ActionPreferredApplyFacts import COMMENTS as ACTION_PREFERRED_APPLY_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PREFERRED_APPLY_COMMENTS)

from ActionPreferredChanceFacts import COMMENTS as ACTION_PREFERRED_CHANCE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PREFERRED_CHANCE_COMMENTS)

from ActionPreferredZeroBridgeFacts import COMMENTS as ACTION_PREFERRED_ZERO_BRIDGE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PREFERRED_ZERO_BRIDGE_COMMENTS)

from ActionPreferredSevenBridgeFacts import COMMENTS as ACTION_PREFERRED_SEVEN_BRIDGE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_PREFERRED_SEVEN_BRIDGE_COMMENTS)


from ActionPreferredDispatchFacts import COMMENTS as ACTION_PREFERRED_DISPATCH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_PREFERRED_DISPATCH_COMMENTS)


from ActionAbsSigned32Facts import COMMENTS as ACTION_ABS_SIGNED32_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_ABS_SIGNED32_COMMENTS)


from ActionContextWordPairsFacts import COMMENTS as ACTION_CONTEXT_WORD_PAIRS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CONTEXT_WORD_PAIRS_COMMENTS)


from ActionVectorHighMaximumFacts import COMMENTS as ACTION_VECTOR_HIGH_MAXIMUM_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_VECTOR_HIGH_MAXIMUM_COMMENTS)


from ActionSignedRatioCodeFacts import COMMENTS as ACTION_SIGNED_RATIO_CODE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SIGNED_RATIO_CODE_COMMENTS)


from ActionHalfDeltaCodesFacts import COMMENTS as ACTION_HALF_DELTA_CODES_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_HALF_DELTA_CODES_COMMENTS)


from ActionRecordCodeStepFacts import COMMENTS as ACTION_RECORD_CODE_STEP_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_CODE_STEP_COMMENTS)


from ActionClass3LinkCountFacts import COMMENTS as ACTION_CLASS3_LINK_COUNT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLASS3_LINK_COUNT_COMMENTS)


from ActionFoldedNearWordsFacts import COMMENTS as ACTION_FOLDED_NEAR_WORDS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_FOLDED_NEAR_WORDS_COMMENTS)


from ActionClampVectorWordsFacts import COMMENTS as ACTION_CLAMP_VECTOR_WORDS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLAMP_VECTOR_WORDS_COMMENTS)


from ActionWideTargetStepFacts import COMMENTS as ACTION_WIDE_TARGET_STEP_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_WIDE_TARGET_STEP_COMMENTS)


from ActionNearVectorSearchFacts import COMMENTS as ACTION_NEAR_VECTOR_SEARCH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_NEAR_VECTOR_SEARCH_COMMENTS)


from ActionSelectWideTargetFacts import COMMENTS as ACTION_SELECT_WIDE_TARGET_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SELECT_WIDE_TARGET_COMMENTS)


from ActionControlDecayFacts import COMMENTS as ACTION_CONTROL_DECAY_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CONTROL_DECAY_COMMENTS)

from ActionKeyTurnNegativeFacts import COMMENTS as ACTION_KEY_TURN_NEGATIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_TURN_NEGATIVE_COMMENTS)

from ActionKeyTurnPositiveFacts import COMMENTS as ACTION_KEY_TURN_POSITIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_TURN_POSITIVE_COMMENTS)

from ActionKeyXNegativeFacts import COMMENTS as ACTION_KEYX_NEGATIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEYX_NEGATIVE_COMMENTS)

from ActionKeyXPositiveFacts import COMMENTS as ACTION_KEYX_POSITIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEYX_POSITIVE_COMMENTS)

from ActionKeyYNegativeFacts import COMMENTS as ACTION_KEYY_NEGATIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEYY_NEGATIVE_COMMENTS)

from ActionKeyYPositiveFacts import COMMENTS as ACTION_KEYY_POSITIVE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEYY_POSITIVE_COMMENTS)

from ActionKeyGaugeIncreaseFacts import COMMENTS as ACTION_KEY_GAUGE_INCREASE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_GAUGE_INCREASE_COMMENTS)

from ActionKeyGaugeDecreaseFacts import COMMENTS as ACTION_KEY_GAUGE_DECREASE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_GAUGE_DECREASE_COMMENTS)

from ActionBankedCallbackReturnFacts import COMMENTS as ACTION_BANKED_CALLBACK_RETURN_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_BANKED_CALLBACK_RETURN_COMMENTS)


from ActionBankedCallbackFacts import COMMENTS as ACTION_BANKED_CALLBACK_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BANKED_CALLBACK_COMMENTS)


from ControlsCircleInteriorFullFacts import COMMENTS as CONTROLS_CIRCLE_INTERIOR_FULL_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CIRCLE_INTERIOR_FULL_COMMENTS)


from ControlsCircleHalfFacts import COMMENTS as CONTROLS_CIRCLE_HALF_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CIRCLE_HALF_COMMENTS)


from ControlsStationRelocationFacts import COMMENTS as CONTROLS_STATION_RELOCATION_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_STATION_RELOCATION_COMMENTS)


from ControlsStationPrepareFacts import COMMENTS as CONTROLS_STATION_PREPARE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_STATION_PREPARE_COMMENTS)


from ControlsClippedCircleHalfFacts import COMMENTS as CONTROLS_CLIPPED_CIRCLE_HALF_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CLIPPED_CIRCLE_HALF_COMMENTS)


from ControlsCircleKernelsFacts import COMMENTS as CONTROLS_CIRCLE_KERNELS_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CIRCLE_KERNELS_COMMENTS)


from ActionSubtractWorkVectorFacts import COMMENTS as ACTION_SUBTRACT_WORK_VECTOR_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SUBTRACT_WORK_VECTOR_COMMENTS)


from ActionRefreshPanelFacts import COMMENTS as ACTION_REFRESH_PANEL_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_REFRESH_PANEL_COMMENTS)


from ControlsVerticalCircleSliceFacts import COMMENTS as CONTROLS_VERTICAL_CIRCLE_SLICE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_VERTICAL_CIRCLE_SLICE_COMMENTS)


from ControlsHorizontalCircleFacts import COMMENTS as CONTROLS_HORIZONTAL_CIRCLE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_HORIZONTAL_CIRCLE_COMMENTS)


from ControlsCornerCircleSliceFacts import COMMENTS as CONTROLS_CORNER_CIRCLE_SLICE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_CORNER_CIRCLE_SLICE_COMMENTS)


from ControlsFullWidthCircleFacts import COMMENTS as CONTROLS_FULL_WIDTH_CIRCLE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_FULL_WIDTH_CIRCLE_COMMENTS)


from ControlsLargeCircleFacts import COMMENTS as CONTROLS_LARGE_CIRCLE_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_LARGE_CIRCLE_COMMENTS)


from ControlsBodyDrawFacts import COMMENTS as CONTROLS_BODY_DRAW_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_BODY_DRAW_COMMENTS)


from ControlsProjectDrawBodyFacts import COMMENTS as CONTROLS_PROJECT_DRAW_BODY_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PROJECT_DRAW_BODY_COMMENTS)


from ActionDrawBankedBodyFacts import COMMENTS as ACTION_DRAW_BANKED_BODY_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_DRAW_BANKED_BODY_COMMENTS)

from ActionRestoreBodyStackFacts import COMMENTS as ACTION_RESTORE_BODY_STACK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RESTORE_BODY_STACK_COMMENTS)


from ActionBodyTransformFacts import COMMENTS as ACTION_BODY_TRANSFORM_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BODY_TRANSFORM_COMMENTS)

from ActionObjectOffsetRiseFacts import COMMENTS as ACTION_OBJECT_OFFSET_RISE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_OFFSET_RISE_COMMENTS)

from ActionObjectOffsetFallFacts import COMMENTS as ACTION_OBJECT_OFFSET_FALL_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_OFFSET_FALL_COMMENTS)

from ActionObjectPhaseWaitFacts import COMMENTS as ACTION_OBJECT_PHASE_WAIT_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_PHASE_WAIT_COMMENTS)

from ActionObjectOffsetTransferFacts import COMMENTS as ACTION_OBJECT_OFFSET_TRANSFER_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_OFFSET_TRANSFER_COMMENTS)

from ActionObjectOffsetVectorFacts import COMMENTS as ACTION_OBJECT_OFFSET_VECTOR_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_OFFSET_VECTOR_COMMENTS)

from ActionObjectOffsetCoefficientsFacts import COMMENTS as ACTION_OBJECT_OFFSET_COEFFICIENTS_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OBJECT_OFFSET_COEFFICIENTS_COMMENTS)


from ActionClass18StateFacts import COMMENTS as ACTION_CLASS18_STATE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_CLASS18_STATE_COMMENTS)

from ActionVisualEffectResumeFacts import COMMENTS as ACTION_VISUAL_EFFECT_RESUME_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_VISUAL_EFFECT_RESUME_COMMENTS)


from ActionWideProjectionLoopFacts import COMMENTS as ACTION_WIDE_PROJECTION_LOOP_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_WIDE_PROJECTION_LOOP_COMMENTS)


from ActionBankedBasisRotationFacts import COMMENTS as ACTION_BANKED_BASIS_ROTATION_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BANKED_BASIS_ROTATION_COMMENTS)


from ActionNonemptyRenderFrameFacts import COMMENTS as ACTION_NONEMPTY_RENDER_FRAME_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_NONEMPTY_RENDER_FRAME_COMMENTS)

from ActionLargeEffectContinuationFacts import COMMENTS as ACTION_LARGE_EFFECT_CONTINUATION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_LARGE_EFFECT_CONTINUATION_COMMENTS)


from ActionLargeEffectEntryFacts import COMMENTS as ACTION_LARGE_EFFECT_ENTRY_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_LARGE_EFFECT_ENTRY_COMMENTS)

from ActionRecordEffectResumeFacts import COMMENTS as ACTION_RECORD_EFFECT_RESUME_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_EFFECT_RESUME_COMMENTS)


from ActionRecordEffectThresholdFacts import COMMENTS as ACTION_RECORD_EFFECT_THRESHOLD_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_RECORD_EFFECT_THRESHOLD_COMMENTS)


from ActionObjectStateReturnFacts import COMMENTS as ACTION_OBJECT_STATE_RETURN_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_OBJECT_STATE_RETURN_COMMENTS)


from ActionNoiseExitFacts import COMMENTS as ACTION_NOISE_EXIT_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_NOISE_EXIT_COMMENTS)


from ActionBodyModeTransitionFacts import COMMENTS as ACTION_BODY_MODE_TRANSITION_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BODY_MODE_TRANSITION_COMMENTS)


from ActionBodyMotionFacts import COMMENTS as ACTION_BODY_MOTION_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_BODY_MOTION_COMMENTS)


from ControlsTargetOverlayFacts import COMMENTS as CONTROLS_TARGET_OVERLAY_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_TARGET_OVERLAY_COMMENTS)


from ActionMotionWithoutKeysFacts import COMMENTS as ACTION_MOTION_WITHOUT_KEYS_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_MOTION_WITHOUT_KEYS_COMMENTS)


from ControlsRadarLoopFacts import COMMENTS as CONTROLS_RADAR_LOOP_COMMENTS
REGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_RADAR_LOOP_COMMENTS)


from ActionVisualEffectListFacts import COMMENTS as ACTION_VISUAL_EFFECT_LIST_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_VISUAL_EFFECT_LIST_COMMENTS)


from ActionSpawnRecordFinishFacts import COMMENTS as ACTION_SPAWN_RECORD_FINISH_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SPAWN_RECORD_FINISH_COMMENTS)


from ActionSpawnScheduleFacts import COMMENTS as ACTION_SPAWN_SCHEDULE_COMMENTS
REGION_COMMENTS.setdefault("Action", {}).update(ACTION_SPAWN_SCHEDULE_COMMENTS)

from ActionOverlayProjectionFacts import COMMENTS as ACTION_OVERLAY_PROJECTION_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_OVERLAY_PROJECTION_COMMENTS)

from ActionDiagnosticQueueFacts import COMMENTS as ACTION_DIAGNOSTIC_QUEUE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_DIAGNOSTIC_QUEUE_COMMENTS)

from ActionDeltaRatioFacts import COMMENTS as ACTION_DELTA_RATIO_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_DELTA_RATIO_COMMENTS)

from ActionDirectDecimalScrollFacts import COMMENTS as ACTION_DIRECT_DECIMAL_SCROLL_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_DIRECT_DECIMAL_SCROLL_COMMENTS)

from ActionDirectDecimalPlainFacts import COMMENTS as ACTION_DIRECT_DECIMAL_PLAIN_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_DIRECT_DECIMAL_PLAIN_COMMENTS)

from ActionApproachWordFacts import COMMENTS as ACTION_APPROACH_WORD_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_APPROACH_WORD_COMMENTS)

from ActionRecordDistanceFacts import COMMENTS as ACTION_RECORD_DISTANCE_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_DISTANCE_COMMENTS)

from ActionSelectedRecordStepFacts import COMMENTS as ACTION_SELECTED_RECORD_STEP_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_SELECTED_RECORD_STEP_COMMENTS)

from ActionClass18ProximityFacts import COMMENTS as ACTION_CLASS18_PROXIMITY_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS18_PROXIMITY_COMMENTS)

from ActionSelectClass8Facts import COMMENTS as ACTION_SELECT_CLASS8_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_SELECT_CLASS8_COMMENTS)

from ActionSelectedRecordProximityFacts import COMMENTS as ACTION_SELECTED_RECORD_PROXIMITY_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_SELECTED_RECORD_PROXIMITY_COMMENTS)

from ActionClass2LinkFacts import COMMENTS as ACTION_CLASS2_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS2_LINK_COMMENTS)

from ActionClass5LinkFacts import COMMENTS as ACTION_CLASS5_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS5_LINK_COMMENTS)

from ActionClass8LinkFacts import COMMENTS as ACTION_CLASS8_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS8_LINK_COMMENTS)

from ActionClass7LinkFacts import COMMENTS as ACTION_CLASS7_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS7_LINK_COMMENTS)

from ActionClass6LinkFacts import COMMENTS as ACTION_CLASS6_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS6_LINK_COMMENTS)

from ActionClass1LinkFacts import COMMENTS as ACTION_CLASS1_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS1_LINK_COMMENTS)

from ActionClass4LinkFacts import COMMENTS as ACTION_CLASS4_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS4_LINK_COMMENTS)

from ActionClass3LinkFacts import COMMENTS as ACTION_CLASS3_LINK_COMMENTS
REGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLASS3_LINK_COMMENTS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Новая папка внутри Tools/Disasm/Research/Candidates")
    arguments = parser.parse_args()
    ROOT = create_candidate(PROJECT_ROOT, arguments.output, "source")
    main()
