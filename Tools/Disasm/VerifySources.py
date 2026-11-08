"""Статическая сверка исходников с исходными байтами и реестром, без сборки."""

from pathlib import Path
import hashlib
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research"))
from MarketScriptTable import PATH as MARKET_SCRIPT_PATH, START as MARKET_SCRIPT_START, parse as parse_market_script


def structure_symbols():
    """Чтение DB/DW/DS и вложенных STRUCT из фактических объявлений, без внешнего реестра."""
    symbols = {}
    current = None
    offset = 0
    for line in (ROOT / "Includes/Structs/Include.inc").read_text(encoding="utf-8").splitlines():
        code = line.split(";", 1)[0].strip()
        declaration = re.fullmatch(r"struct\s+(\w+)", code, re.I)
        if declaration:
            current, offset = declaration[1].upper(), 0
        elif current and code.lower() == "ends":
            symbols[current] = offset
            current = None
        elif current and code:
            field = re.fullmatch(r"(\w+)\s+(db|dw|ds|text)\s+(.+)", code, re.I)
            if not field:
                nested = re.fullmatch(r"(\w+)\s+(\w+)", code)
                if not nested or nested[2].upper() not in symbols:
                    raise ValueError("Не поддержано поле структуры: " + code)
                prefix=current+'.'+nested[1].upper();kind=nested[2].upper()
                symbols[prefix]=offset
                # Создание относительных имён вложенных полей по уже объявленной реальной структуре.
                children=[(name[len(kind):],value) for name,value in symbols.items() if name.startswith(kind+'.')]
                for suffix,value in children:symbols[prefix+suffix]=offset+value
                offset+=symbols[kind]
                continue
            symbols[current + "." + field[1].upper()] = offset
            if field[2].lower() in ("ds", "text"):
                count = field[3].split(",", 1)[0].strip().replace("#", "0x")
                offset += int(count, 0)
            else:
                offset += (1 if field[2].lower() == "db" else 2) * len(field[3].split(","))
    return symbols


def read_json(name):
    return json.loads((ROOT / "Tools/Disasm/Reports" / name).read_text(encoding="utf-8"))


def main():
    source_map = read_json("SourceMap.json")
    flow = read_json("ControlFlow.json")
    instructions = {(i["slot"],i["offset"]):i for r in flow for i in r["instructions"]}
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    sources = {e["slot"]:(ROOT / (e["path"]+".sectors.bin")).read_bytes() for e in manifest["entries"]}
    symbols = read_json("Symbols.json")
    symbols.update({"TrDos.Dispatch":0x3D13,"StationState.CurrentPage":0x6306,
                    "StationState.ItemIndex":0x8500,"StationState.DirtyCells":0x8600,
                    "StationState.Items":0xF0FD,"StationState.DrawList":0xF3DE})
    symbols = {key.upper():value for key,value in symbols.items()}
    symbols.update(structure_symbols())
    # Чтение адресных привязок из исходника, без выделения памяти и ассемблирования.
    for include in ("Includes/Variables/Include.inc", "Includes/Const/Include.inc"):
        current_module = None
        for line in (ROOT / include).read_text(encoding="utf-8").splitlines():
            code = line.split(";", 1)[0].strip()
            module = re.fullmatch(r"module\s+(\w+)", code, re.I)
            binding = re.fullmatch(r"(\w+)\s+equ\s+#([0-9A-Fa-f]+)", code, re.I)
            if module:
                current_module = module[1].upper()
            elif code.lower() == "endmodule":
                current_module = None
            elif current_module and binding:
                symbols[current_module + "." + binding[1].upper()] = int(binding[2], 16)

    def number(expression):
        expression = expression.strip()
        if expression.startswith("@"):
            return symbols[expression[1:].upper()]
        if expression.startswith("#"):
            return int(expression[1:],16)
        return int(expression)

    def normalize(operation):
        operation = operation.upper()
        operation = re.sub(r"@[A-Z_][A-Z0-9_.]*",lambda m:f"#{number(m[0]):04X}",operation)
        # Преобразование именованных полей в смещения для сверки с исходными командами.
        operation = re.sub(r"\bF[A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)*\b",
                           lambda m: "#" + format(symbols[m[0]], "X") if m[0] in symbols else m[0], operation)
        operation = re.sub(r"#([0-9A-F]+)\s*\+\s*([0-9]+)",
                           lambda m: "#" + format(int(m[1], 16) + int(m[2]), "X"), operation)
        operation = re.sub(r"#([0-9A-F]+)\s*\+\s*#([0-9A-F]+)",
                           lambda m: "#" + format(int(m[1], 16) + int(m[2], 16), "X"), operation)
        # Вычисление именованного адреса перед таблицей без подмены исходной инструкции.
        operation = re.sub(r"#([0-9A-F]+)\s*-\s*([0-9]+)",
                           lambda m: "#" + format((int(m[1], 16) - int(m[2])) & 0xFFFF, "X"), operation)
        operation = re.sub(r"#([0-9A-F]+)\s*-\s*#([0-9A-F]+)",
                           lambda m: "#" + format((int(m[1], 16) - int(m[2], 16)) & 0xFFFF, "X"), operation)
        operation = re.sub(r",\s*-#([0-9A-F]+)$",
                           lambda m: ",#" + format(-int(m[1], 16) & 0xFFFF, "X"), operation)
        operation = re.sub(r",\s*([0-9]+)\s*-\s*#([0-9A-F]+)$",
                           lambda m: ",#" + format((int(m[1]) - int(m[2], 16)) & 0xFFFF, "X"), operation)
        operation = re.sub(r"#([0-9A-F]+)", lambda m: "#" + format(int(m[1], 16), "X"), operation)
        operation = re.sub(r"(?<![#A-Z0-9_])\b[0-9]+\b(?![A-Z0-9_])",
                           lambda m: "#" + format(int(m[0]), "X"), operation)
        return re.sub(r"\s+", "", operation)

    # Проверка физических текстовых потоков станции без подстановки перевода в образ.
    from StationPanelTextResources import RESOURCES as PANEL_TEXTS, path as panel_path, records as panel_records
    for start,end,name,count,separator,consumer in PANEL_TEXTS:
        raw=(ROOT/panel_path(name)).read_bytes()
        assert raw==sources[4][start:end] and len(panel_records(raw,separator))==count
        rows=[p for p in source_map if p['path']==panel_path(name)]
        assert len(rows)==1 and rows[0]['kind']=='binary_resource'
        assert (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)

    # Проверка подписей интерфейса и общих физических ограничителей LF.
    from StationInterfaceTextResources import RESOURCES as INTERFACE_TEXTS, path as interface_text_path, verify as verify_interface_texts
    verify_interface_texts(sources[4])
    for start,end,name,consumer,lf,cr in INTERFACE_TEXTS:
        assert (ROOT/interface_text_path(name)).read_bytes()==sources[4][start:end]
        rows=[p for p in source_map if p['path']==interface_text_path(name)]
        assert len(rows)==1 and rows[0]['kind']=='binary_resource'
        assert (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)

    code_count = 0
    coverage = {e["slot"]:bytearray(e["allocated_length"]) for e in manifest["entries"] if not e["deleted"]}
    for item in source_map:
        slot, offset, length = item["slot"], item["offset"], item["length"]
        data = sources[slot][offset:offset+length]
        # Проверка непересекающегося полного покрытия каждой действующей области.
        if any(coverage[slot][offset:offset+length]):
            raise ValueError("Пересечение исходных диапазонов")
        coverage[slot][offset:offset+length] = b"\x01"*length
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("Контрольная сумма исходного диапазона не совпала")
        if item["kind"] in ("unclassified", "binary_resource"):
            if (ROOT/item["path"]).read_bytes() != data:
                raise ValueError("Изменились сохраняемые исходные байты " + item["path"])
        elif item["kind"] == "code":
            actual = []
            for line in (ROOT/item["path"]).read_text(encoding="utf-8").splitlines():
                if not line.strip() or line.lstrip().startswith(";"):
                    continue
                operation = line[16:].split(";",1)[0].strip()
                if not operation or operation.lower().startswith(("module ","endmodule")):
                    continue
                actual.append(normalize(operation))
            expected = []
            position = offset
            while position < offset+length:
                instruction = instructions[(slot,position)]
                raw = bytes.fromhex(instruction["hex"])
                if sources[slot][position:position+len(raw)] != raw:
                    raise ValueError("Декодированные байты не совпали с оригиналом")
                expected.append(normalize(instruction["operation"]))
                position += len(raw)
            if actual != expected:
                raise ValueError("Текст инструкций отличается от исходной разметки " + item["path"])
            code_count += len(actual)
    if not all(all(c) for c in coverage.values()):
        raise ValueError("Неполное покрытие действующих областей")

    # Проверка разнесённых физических указателей музыкальных эффектов, код между ними не считается таблицей.
    from MusicEffectTables import TABLES as MUSIC_EFFECT_TABLES, parse as parse_music_effect_table
    music_effect_records = 0
    for table in MUSIC_EFFECT_TABLES:
        module, path, start, entries = table
        matches = [item for item in source_map if item['path'] == path]
        if not matches:
            continue
        assert len(matches) == 1
        item = matches[0]
        raw, labels = parse_music_effect_table((ROOT/path).read_text('utf-8'), table, symbols)
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (10, start-0xDB00, len(entries)*2, start)
        assert raw == sources[10][start-0xDB00:start-0xDB00+len(raw)]
        assert all(symbols.get(k) == v for k, v in labels.items())
        assert symbols['FMUSICEFFECTTARGET'] == 2 and symbols['FMUSICEFFECTTARGET.HANDLER'] == 0
        music_effect_records += len(entries)
    assert music_effect_records in (0, 21)

    # Проверка физических таблиц музыки, размеров полей и каждого исходного байта.
    from MusicPlayerTables import TABLES as MUSIC_PLAYER_TABLES, parse as parse_music_player_table
    music_player_records = {}
    for table in MUSIC_PLAYER_TABLES:
        module, path, start, end, structure, fields, names = table
        matches = [item for item in source_map if item['path'] == path]
        if not matches:
            continue
        assert len(matches) == 1
        item = matches[0]
        raw, labels = parse_music_player_table((ROOT/path).read_text('utf-8'), table)
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (10, start, end-start, 0xDB00+start)
        assert raw == sources[10][start:end]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        field_offset = 0
        for name, width, _ in fields:
            assert symbols[structure.upper()+'.'+name.upper()] == field_offset
            field_offset += width
        assert symbols[structure.upper()] == field_offset
        music_player_records[path] = len(names)
    assert len(music_player_records) in (0, 6)

    # Проверка двух байтов каждого элемента очереди банка 1 и отдельного конечного маркера.
    from ControlsTextQueueFacts import TABLE as TEXT_QUEUE_TABLE, parse as parse_text_queue
    text_queue_records = 0
    queue_entries = [item for item in source_map if item['path'] == TEXT_QUEUE_TABLE[1]]
    if queue_entries:
        assert len(queue_entries) == 1
        item = queue_entries[0]
        raw, labels = parse_text_queue((ROOT/TEXT_QUEUE_TABLE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (23, 0x11A2, 34, 0xEC80)
        assert raw == sources[23][0x11A2:0x11C4]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FTEXTQUEUEITEM'] == 2 and symbols['FTEXTQUEUEITEM.HIGHKIND'] == 0 and symbols['FTEXTQUEUEITEM.LOWVALUE'] == 1
        assert symbols['FTEXTQUEUEINSERTFRAME'] == 8
        assert [symbols['FTEXTQUEUEINSERTFRAME.'+name] for name in ('SAVEDAF','SAVEDBC','SAVEDHL','CALLERRETURN')] == [0,2,4,6]
        if 'FACTIONTEXTQUEUEFRAME' in symbols:
            assert symbols['FACTIONTEXTQUEUEFRAME'] == 8
            assert [symbols['FACTIONTEXTQUEUEFRAME.'+name] for name in ('SAVEDHL','SAVEDBC','SAVEDAF','CALLERRETURN')] == [0,2,4,6]
        text_queue_records = 17

    # Проверка восьми физических фаз XOR-маркера, всех четырёх полей и исходных 32 байтов.
    from ControlsMarkerFacts import TABLE as MARKER_TABLE, parse as parse_marker
    marker_records = 0
    marker_entries = [item for item in source_map if item['path'] == MARKER_TABLE[1]]
    if marker_entries:
        assert len(marker_entries) == 1
        item = marker_entries[0]
        raw, labels = parse_marker((ROOT / MARKER_TABLE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (23, 0x160F, 32, 0xF0ED)
        assert raw == sources[23][0x160F:0x162F]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FMARKERPHASEMASKS'] == 4
        assert [symbols['FMARKERPHASEMASKS.' + name] for name in ('VERTICAL', 'CENTRALLEFT', 'CENTRALMIDDLE', 'CENTRALRIGHT')] == [0, 1, 2, 3]
        marker_records = 8

    # Проверка 35 физических записей Y,X и исходных нулевых инициализаторов.
    from ControlsBufferPointsFacts import TABLE as BUFFER_POINTS_TABLE, parse as parse_buffer_points
    buffer_point_records = 0
    buffer_point_entries = [item for item in source_map if item['path'] == BUFFER_POINTS_TABLE[1]]
    if buffer_point_entries:
        assert len(buffer_point_entries) == 1
        item = buffer_point_entries[0]
        raw, labels = parse_buffer_points((ROOT / BUFFER_POINTS_TABLE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0x500, 70, 0xC500)
        assert raw == sources[22][0x500:0x546]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FBUFFERPOINT'] == 2 and symbols['FBUFFERPOINT.Y'] == 0 and symbols['FBUFFERPOINT.X'] == 1
        buffer_point_records = 35

    # Проверка 256 физических знаковых отсчётов исходной синусоиды ACTION.
    from ActionSineTable import TABLE as ACTION_SINE_TABLE, parse as parse_action_sine, validate as validate_action_sine
    action_sine_records = 0
    action_sine_entries = [item for item in source_map if item['path'] == ACTION_SINE_TABLE[1]]
    if action_sine_entries:
        assert len(action_sine_entries) == 1
        item = action_sine_entries[0]
        raw, labels = parse_action_sine((ROOT / ACTION_SINE_TABLE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3900, 256, 0x9900)
        assert raw == validate_action_sine(sources[17])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FFIXEDSINEVALUE'] == 1 and symbols['FFIXEDSINEVALUE.VALUE'] == 0
        action_sine_records = 256

    # Проверка трёх физических записей LowWord и FoldByte, не адресных псевдонимов.
    from ActionFoldedRandomData import TABLES as FOLDED_STATES, parse as parse_folded_state
    folded_random_records = 0
    for table in FOLDED_STATES:
        entries = [item for item in source_map if item['path']==table[1]]
        if not entries:
            continue
        assert len(entries)==1
        item=entries[0]
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,table[2],3,table[2]+0x6000)
        raw,bindings=parse_folded_state((ROOT/table[1]).read_text('utf-8'),table)
        assert raw==sources[17][table[2]:table[3]]
        assert all(symbols.get(key.upper())==value for key,value in bindings.items())
        assert symbols['FFOLDEDRANDOMSTATE']==3
        assert symbols['FFOLDEDRANDOMSTATE.LOWWORD']==0 and symbols['FFOLDEDRANDOMSTATE.FOLDBYTE']==2
        folded_random_records+=1

    # Проверка двух физических слов состояния генератора ACTION.
    from ActionWordRandomState import TABLE as WORD_RANDOM, parse as parse_word_random
    word_random_records = 0
    entries = [item for item in source_map if item['path'] == WORD_RANDOM[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_word_random((ROOT/WORD_RANDOM[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B15, 4, 0x9B15)
        assert raw == sources[17][0x3B15:0x3B19]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FWORDRANDOMSTATE'] == 4
        assert symbols['FWORDRANDOMSTATE.FIRST'] == 0 and symbols['FWORDRANDOMSTATE.SECOND'] == 2
        word_random_records = 1

    # Проверка 256 исходных кодов отношения, без генерации идеальной тригонометрической таблицы.
    from ActionSignedRatioCodesData import TABLE as RATIO_CODES, parse as parse_ratio_codes, validate as validate_ratio_codes
    signed_ratio_code_records = 0
    entries = [item for item in source_map if item['path'] == RATIO_CODES[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_ratio_codes((ROOT / RATIO_CODES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x3A00,256,0x9A00)
        assert raw == validate_ratio_codes(sources[17])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FSIGNEDRATIOCODE'] == 1 and symbols['FSIGNEDRATIOCODE.CODE'] == 0
        signed_ratio_code_records = 256

    # Проверка ровно 26 физических адресов классов, без соседних инструкций.
    from ActionObjectStateHandlersData import TABLE as STATE_HANDLERS, parse as parse_state_handlers
    state_handler_records = 0
    entries = [item for item in source_map if item['path'] == STATE_HANDLERS[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_state_handlers((ROOT / STATE_HANDLERS[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x8F50, 44, 0xEF50)
        assert raw == sources[17][0x8F50:0x8F7C]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FOBJECTSTATEHANDLER'] == 2 and symbols['FOBJECTSTATEHANDLER.HANDLER'] == 0
        state_handler_records = 22

    from ActionClassHandlersData import TABLE as CLASS_HANDLERS, parse as parse_class_handlers
    class_handler_records = 0
    entries = [item for item in source_map if item['path'] == CLASS_HANDLERS[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_class_handlers((ROOT / CLASS_HANDLERS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x72D,52,0x64F0)
        assert raw == sources[17][0x72D:0x761]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FCLASSHANDLER'] == 2 and symbols['FCLASSHANDLER.HANDLER'] == 0
        class_handler_records = 26

    # Проверка трёх физических FComponent24, старших знаковых слов и сохранённых младших байтов.
    from ActionComponentWorkData import TABLE as COMPONENT_WORK, parse as parse_component_work, validate as validate_component_work
    component_work_records = 0
    component_entries = [item for item in source_map if item['path'] == COMPONENT_WORK[1]]
    if component_entries:
        assert len(component_entries) == 1
        item = component_entries[0]
        raw, labels = parse_component_work((ROOT / COMPONENT_WORK[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B1E, 9, 0x9B1E)
        assert raw == validate_component_work(sources[17])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FCOMPONENT24'] == 3
        assert [symbols['FCOMPONENT24.'+field] for field in ('LOW','MIDDLE','HIGH')] == [0,1,2]
        component_work_records = 3

    # Проверка всех физических байтов и вложенных полей шести исходных широких векторов.
    from ActionWideVectorsData import PATH as WIDE_VECTORS, parse as parse_wide_vectors
    wide_vector_records = 0
    wide_entries = [item for item in source_map if item['path'] == WIDE_VECTORS]
    if wide_entries:
        assert len(wide_entries) == 1
        item = wide_entries[0]
        raw, labels = parse_wide_vectors((ROOT / WIDE_VECTORS).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, 0x3B27, 72, 0x9B27)
        assert raw == sources[17][0x3B27:0x3B6F]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FACTIONWIDECOMPONENT'] == 4 and symbols['FACTIONWIDEVECTOR'] == 12
        for component in range(3):
            assert symbols['FACTIONWIDEVECTOR.COMPONENT'+str(component)] == 4*component
            for byte in range(4):
                assert symbols['FACTIONWIDEVECTOR.COMPONENT'+str(component)+'.BYTE'+str(byte)] == 4*component+byte
        wide_vector_records = 6

    # Проверка физического 24-битного рабочего вектора и смещений всех вложенных полей.
    from ActionWorkVectorData import PATH as WORK_VECTOR, MODULE as WORK_MODULE, TRANSFORM_PATH, TRANSFORM_MODULE, parse as parse_work_vector
    signed_work_vector_records = 0
    for path, origin, module in ((WORK_VECTOR, 0x9B78, WORK_MODULE), (TRANSFORM_PATH, 0x9B6F, TRANSFORM_MODULE)):
        work_entries = [item for item in source_map if item['path'] == path]
        if not work_entries:
            continue
        assert len(work_entries) == 1
        item = work_entries[0]
        raw, labels = parse_work_vector((ROOT / path).read_text('utf-8'), origin, module)
        start = origin - 0x6000
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, start, 9, origin)
        assert raw == sources[17][start:start+9]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FACTIONWORKCOMPONENT24'] == 3 and symbols['FACTIONWORKVECTOR24'] == 9
        assert symbols['FACTIONWORKCOMPONENT24.LOWWORD'] == 0 and symbols['FACTIONWORKCOMPONENT24.HIGH'] == 2
        for component in range(3):
            assert symbols['FACTIONWORKVECTOR24.COMPONENT'+str(component)] == 3*component
        signed_work_vector_records += 1

    from ActionVisualEffectData import PATH as EFFECTS_PATH, START as EFFECTS_START, END as EFFECTS_END
    from ActionVisualEffectData import parse as parse_visual_effects
    visual_effect_records = 0
    visual_effect_entries = [item for item in source_map if item['path'] == EFFECTS_PATH]
    if visual_effect_entries:
        assert len(visual_effect_entries) == 1
        item = visual_effect_entries[0]
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (17, EFFECTS_START, EFFECTS_END - EFFECTS_START, 0xA795)
        raw, labels = parse_visual_effects((ROOT / EFFECTS_PATH).read_text('utf-8'))
        assert raw == sources[17][EFFECTS_START:EFFECTS_END]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FVISUALEFFECT'] == 18
        visual_effect_records = 8

    # Проверка трёх физических страниц корня, включая особый старший диапазон и исходные исключения.
    from ControlsRootCacheData import TABLE as ROOT_CACHE, parse as parse_root_cache, validate as validate_root_cache
    root_cache_records = 0
    root_cache_entries = [item for item in source_map if item['path'] == ROOT_CACHE[1]]
    if root_cache_entries:
        assert len(root_cache_entries) == 1
        item = root_cache_entries[0]
        raw, labels = parse_root_cache((ROOT / ROOT_CACHE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0, 768, 0xC000)
        assert raw == validate_root_cache(sources[22])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FROOTCACHEBYTE'] == 1 and symbols['FROOTCACHEBYTE.VALUE'] == 0
        root_cache_records = 768

    # Проверка обеих физических плоскостей квадратов и всех 512 экземпляров структуры.
    from ControlsSquareTable import TABLE as SQUARE_TABLE, parse as parse_squares, validate as validate_squares
    square_records = 0
    square_entries = [item for item in source_map if item['path'] == SQUARE_TABLE[1]]
    if square_entries:
        assert len(square_entries) == 1
        item = square_entries[0]
        raw, labels = parse_squares((ROOT / SQUARE_TABLE[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0x300, 512, 0xC300)
        assert raw == validate_squares(sources[22])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FSQUARETABLEBYTE'] == 1 and symbols['FSQUARETABLEBYTE.VALUE'] == 0
        square_records = 512

    # Проверка затравок малых масок и реально записываемых 12 строковых байтов.
    from ControlsSmallMaskTables import TABLES as SMALL_MASK_TABLES, parse as parse_small_masks, validate as validate_small_masks
    small_mask_records = 0
    for table in SMALL_MASK_TABLES:
        matches = [item for item in source_map if item['path'] == table[1]]
        if not matches:
            continue
        validate_small_masks(sources[22])
        assert len(matches) == 1
        item = matches[0]
        raw, labels = parse_small_masks((ROOT / table[1]).read_text('utf-8'), table)
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, table[2], table[3]-table[2], 0xC000+table[2])
        assert raw == sources[22][table[2]:table[3]]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols[table[4].upper()] == 1 and symbols[(table[4]+'.'+table[5][0][0]).upper()] == 0
        small_mask_records += len(table[6])

    # Проверка физического экземпляра входных полей проекции без типизации неизвестного рабочего хвоста.
    from ControlsBodyProjection import TABLE as BODY_PROJECTION, parse as parse_body_projection
    body_projection_records = 0
    projection_entries = [item for item in source_map if item['path'] == BODY_PROJECTION[1]]
    if projection_entries:
        assert len(projection_entries) == 1
        item = projection_entries[0]
        raw, labels = parse_body_projection((ROOT / BODY_PROJECTION[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0x117D, 4, 0xD17D)
        assert raw == sources[22][0x117D:0x1181]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FBODYPROJECTION'] == 4
        assert [symbols['FBODYPROJECTION.'+name.upper()] for name,_,_ in BODY_PROJECTION[5]] == [0,1,2,3]
        body_projection_records = 1

    # Проверка каждого поля физической рабочей записи большого контура.
    from ControlsCircleWork import TABLE as CIRCLE_WORK, parse as parse_circle_work
    circle_work_records = 0
    entries = [item for item in source_map if item['path'] == CIRCLE_WORK[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_circle_work((ROOT/CIRCLE_WORK[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (22, 0x1181, 12, 0xD181)
        assert raw == sources[22][0x1181:0x118D]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FCIRCLERASTERWORK'] == 12
        offset = 0
        for name, width, _ in CIRCLE_WORK[5]:
            assert symbols['FCIRCLERASTERWORK.'+name.upper()] == offset
            offset += width
        circle_work_records = 1

    # Проверка пятнадцати физических правил формирования параметров.
    from ControlsParameterCoefficients import TABLE as PARAMETER_RULES, parse as parse_parameter_rules
    parameter_rule_records = 0
    entries = [item for item in source_map if item['path'] == PARAMETER_RULES[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_parameter_rules((ROOT/PARAMETER_RULES[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (23, 0x486, 45, 0xDF64)
        assert raw == sources[23][0x486:0x4B3]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FPARAMETERCOEFFICIENT'] == 3
        assert [symbols['FPARAMETERCOEFFICIENT.'+name.upper()] for name,_,_ in PARAMETER_RULES[5]] == [0,1,2]
        parameter_rule_records = 15

    # Проверка всех физических фаз четырёх трёхстрочных знаков.
    from ControlsThreeRowGlyphs import TABLE as THREE_ROW_RULES, parse as parse_three_row_rules
    three_row_glyph_records = 0
    entries = [item for item in source_map if item['path'] == THREE_ROW_RULES[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_three_row_rules((ROOT/THREE_ROW_RULES[1]).read_text('utf-8'))
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (23, 0x6D3, 192, 0xE1B1)
        assert raw == sources[23][0x6D3:0x793]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        assert symbols['FTHREEROWGLYPHPHASE'] == 6
        assert [symbols['FTHREEROWGLYPHPHASE.'+name.upper()] for name,_,_ in THREE_ROW_RULES[5]] == [0,1,2,3,4,5]
        three_row_glyph_records = 32

    # Проверка четырёх физических записей входов трёх знаков.
    from ActionGlyphIndicatorState import PATH as GLYPH_INPUT_PATH, STRUCTURES as GLYPH_INPUT_STRUCTURES, parse as parse_glyph_inputs
    glyph_input_records = 0
    entries = [item for item in source_map if item['path'] == GLYPH_INPUT_PATH]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_glyph_inputs((ROOT/GLYPH_INPUT_PATH).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x3B81,12,0x9B81)
        assert raw == sources[17][0x3B81:0x3B8D]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        for name,fields in GLYPH_INPUT_STRUCTURES.items():
            assert symbols[name.upper()] == 3
            assert [symbols[name.upper()+'.'+field.upper()] for field,_ in fields] == [0,1,2]
        glyph_input_records = 4

    # Проверка шестнадцати физических адресов для RET, смысл полных хвостов не подменяется этой проверкой.
    from ControlsRasterReturns import TABLE as RASTER_RETURNS, parse as parse_raster_returns
    raster_return_records = 0
    entries = [item for item in source_map if item['path'] == RASTER_RETURNS[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw,labels = parse_raster_returns((ROOT/RASTER_RETURNS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (23,0x793,32,0xE271)
        assert raw == sources[23][0x793:0x7B3]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FRETURNDISPATCHENTRY'] == 2 and symbols['FRETURNDISPATCHENTRY.TARGET'] == 0
        raster_return_records = 16

    # Проверка 672 физических байтов указателей, масок и фаз объектных значков.
    from ControlsObjectGlyphData import TABLES as OBJECT_GLYPH_TABLES, parse as parse_object_glyph_data
    object_glyph_records = 0
    for table in OBJECT_GLYPH_TABLES:
        entries = [item for item in source_map if item['path']==table[1]]
        if entries:
            assert len(entries)==1
            item=entries[0]
            raw,labels=parse_object_glyph_data((ROOT/table[1]).read_text('utf-8'),table)
            assert (item['slot'],item['offset'],item['length'],item['origin'])==(23,table[2],table[3]-table[2],0xDADE+table[2])
            assert raw==sources[23][table[2]:table[3]]
            assert all(symbols.get(key.upper())==value for key,value in labels.items())
            assert symbols[table[4].upper()]==sum(field[1] for field in table[5])
            offset=0
            for name,width,note in table[5]:
                assert symbols[table[4].upper()+'.'+name.upper()]==offset
                offset+=width
            object_glyph_records+=len(table[6])

    # Проверка семи физических масок частичного столбца шкалы.
    from ControlsGaugeMasks import TABLE as GAUGE_MASKS, parse as parse_gauge_masks
    gauge_mask_records=0
    entries=[item for item in source_map if item['path']==GAUGE_MASKS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_gauge_masks((ROOT/GAUGE_MASKS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(23,0xE95,7,0xE973)
        assert raw==sources[23][0xE95:0xE9C]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FGAUGEPARTIALMASK']==1 and symbols['FGAUGEPARTIALMASK.PATTERN']==0
        gauge_mask_records=7

    # Проверка физической пары Preferred/Fallback, игровая семантика здесь не подменяется.
    from ActionPreferredByteState import TABLE as PREFERRED_BYTES, parse as parse_preferred_bytes
    preferred_byte_records=0
    entries=[item for item in source_map if item['path']==PREFERRED_BYTES[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_preferred_bytes((ROOT/PREFERRED_BYTES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3C10,2,0x9C10)
        assert raw==sources[17][0x3C10:0x3C12]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FPREFERREDBYTEPAIR']==2
        assert symbols['FPREFERREDBYTEPAIR.PREFERRED']==0 and symbols['FPREFERREDBYTEPAIR.FALLBACK']==1
        preferred_byte_records=1

    # Проверка 26 отдельных указателей и 27 пар IN, перекрывающееся слово 704B/704C не эмитируется повторно.
    from ActionKeyScanTables import TABLES as KEY_SCAN_TABLES, parse as parse_key_scan_table, origin as key_scan_origin
    key_scan_records=0
    for table in KEY_SCAN_TABLES:
        entries=[item for item in source_map if item['path']==table[1]]
        if entries:
            assert len(entries)==1
            item=entries[0]
            raw,labels=parse_key_scan_table((ROOT/table[1]).read_text('utf-8'),table)
            assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,table[2],table[3]-table[2],key_scan_origin(table)+table[2])
            assert raw==sources[17][table[2]:table[3]]
            assert all(symbols.get(key.upper())==value for key,value in labels.items())
            assert symbols[table[4].upper()]==2
            offset=0
            for field,width,note in table[5]:
                assert symbols[table[4].upper()+'.'+field.upper()]==offset
                offset+=width
            key_scan_records+=len(table[6])

    # Проверка физической пары двух байтов остатка ракет и обратного порядка полей.
    from ActionMissileStockFacts import TABLE as MISSILE_STOCK, parse as parse_missile_stock
    missile_stock_records=0
    entries=[item for item in source_map if item['path']==MISSILE_STOCK[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_missile_stock((ROOT/MISSILE_STOCK[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3C12,2,0x9C12)
        assert raw==sources[17][0x3C12:0x3C14]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FMISSILESTOCK']==2 and symbols['FMISSILESTOCK.FALLBACK']==0 and symbols['FMISSILESTOCK.PREFERRED']==1
        missile_stock_records=1

    # Проверка трёх физических кодов захвата, исходные значения не заменяются.
    from ActionMissileLaunchFacts import TABLE as MISSILE_TARGETS, parse as parse_missile_targets
    missile_target_records=0
    entries=[item for item in source_map if item['path']==MISSILE_TARGETS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_missile_targets((ROOT/MISSILE_TARGETS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3B1B,3,0x9B1B)
        assert raw==sources[17][0x3B1B:0x3B1E]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FMISSILETARGETS']==3
        assert [symbols['FMISSILETARGETS.TARGET'+str(i)] for i in range(3)]==[0,1,2]
        missile_target_records=1

    # Проверка шестнадцати знаковых поправок и исходного физического смещения.
    from ActionTypeDeltaFacts import TABLE as TYPE_DELTAS, parse as parse_type_deltas
    type_delta_records=0
    entries=[i for i in source_map if i['path']==TYPE_DELTAS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_type_deltas((ROOT/TYPE_DELTAS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x588,16,0x634B)
        assert raw==sources[17][0x588:0x598]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FINDEXEDDELTA']==1 and symbols['FINDEXEDDELTA.DELTA']==0
        type_delta_records=16

    # Проверка всех байтов физических записей и вложенных смещений по реальным STRUCT.
    from ActionObjectRecords import PATH as OBJECT_RECORDS, parse as parse_object_records, SCHEMA as OBJECT_STRUCTS, layout as object_layout
    object_records=0
    entries=[i for i in source_map if i['path']==OBJECT_RECORDS]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_object_records((ROOT/OBJECT_RECORDS).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x4100,1664,0xA100)
        assert raw==sources[17][0x4100:0x4780]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        for structure in OBJECT_STRUCTS:
            size,fields=object_layout(structure)
            assert symbols[structure.upper()]==size
            assert all(symbols.get((structure+'.'+field).upper())==value for field,value in fields.items())
        object_records=26

    # Проверка пяти исходных потоков, физических строк, терминаторов и каждого поля STRUCT.
    from ActionAyStreams import GROUPS as AY_STREAM_GROUPS, parse as parse_ay_streams, bounds as ay_stream_bounds
    ay_stream_records=0
    for path,streams in AY_STREAM_GROUPS:
        entries=[i for i in source_map if i['path']==path]
        if not entries:continue
        assert len(entries)==1
        start,end=ay_stream_bounds(streams);item=entries[0]
        raw,labels=parse_ay_streams((ROOT/path).read_text('utf-8'),streams)
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,start,end-start,start+0x6000)
        assert raw==sources[17][start:end]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FACTIONAYFRAME']==4
        for offset,field in enumerate(('ToneLow','ToneHigh','MixerBits','Volume')):
            assert symbols[('FActionAyFrame.'+field).upper()]==offset
        ay_stream_records+=sum(s[2] for s in streams)

    # Проверка всех исходных байтов нормированных квадратов и каждого физического поля.
    from ActionProjectionClipFacts import TABLE as PROJECTION_SQUARES, parse as parse_projection_squares
    projection_square_values=0
    entries=[i for i in source_map if i['path']==PROJECTION_SQUARES[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_projection_squares((ROOT/PROJECTION_SQUARES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3800,256,0x9800)
        assert raw==sources[17][0x3800:0x3900]
        assert list(raw)==[min(i,255-i)**2//127 for i in range(256)]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FSYMMETRICSQUAREVALUE']==1 and symbols['FSYMMETRICSQUAREVALUE.VALUE']==0
        projection_square_values=256

    # Проверка всех исходных little-endian указателей OBJECT3D и полей реальных STRUCT.
    from ActionObjectPointersData import TABLE as OBJECT_POINTER_TABLE, parse as parse_object_pointers
    pointer_path=OBJECT_POINTER_TABLE[1]
    pointer_records=[i for i in source_map if i['path']==pointer_path]
    assert len(pointer_records)==1
    pointer_item=pointer_records[0]
    assert (pointer_item['slot'],pointer_item['offset'],pointer_item['length'],pointer_item['origin'])==(17,0x3E00,256,0x9E00)
    pointer_raw,pointer_labels=parse_object_pointers((ROOT/pointer_path).read_text('utf-8'))
    assert pointer_raw==sources[17][0x3E00:0x3F00]
    assert all(symbols.get(k.upper())==v for k,v in pointer_labels.items())
    assert symbols['FOBJECTDATAPOINTER']==2 and symbols['FOBJECTDATAPOINTER.TARGET']==0

    # Проверка реальных четырёх FClipProduct, всех полей и физических исходных байтов.
    from ActionClipProductsData import PATH as CLIP_PRODUCTS_PATH, parse as parse_clip_products
    clip_raw,clip_labels=parse_clip_products((ROOT/CLIP_PRODUCTS_PATH).read_text('utf-8'))
    assert clip_raw==sources[17][0x6F2B:0x6F3B]
    assert all(symbols.get(k.upper())==v for k,v in clip_labels.items())
    assert symbols['FCLIPPRODUCT']==4 and symbols['FCLIPPRODUCT.LOWWORD']==0 and symbols['FCLIPPRODUCT.HIGHWORD']==2
    clip_items=[x for x in source_map if x['path']==CLIP_PRODUCTS_PATH]
    assert len(clip_items)==1 and (clip_items[0]['offset'],clip_items[0]['length'],clip_items[0]['origin'])==(0x6F2B,16,0xCF2B)

    # Проверка шестнадцати FLinePixelMask, всех полей и физических исходных байтов.
    from ActionLineMasksData import PATH as LINE_MASKS_PATH, parse as parse_line_masks
    line_mask_raw,line_mask_labels=parse_line_masks((ROOT/LINE_MASKS_PATH).read_text('utf-8'))
    assert line_mask_raw==sources[17][0x8010:0x8020]
    assert all(symbols.get(k.upper())==v for k,v in line_mask_labels.items())
    assert symbols['FLINEPIXELMASK']==1 and symbols['FLINEPIXELMASK.MASK']==0
    line_mask_items=[x for x in source_map if x['path']==LINE_MASKS_PATH]
    assert len(line_mask_items)==1 and (line_mask_items[0]['offset'],line_mask_items[0]['length'],line_mask_items[0]['origin'])==(0x8010,16,0xE010)

    # Проверка кодов корабля и скиммера по всей физической раскладке исходного документа.
    from ActionEquipmentData import TABLES as EQUIPMENT_TABLES, parse as parse_equipment
    for table in EQUIPMENT_TABLES:
        raw,labels=parse_equipment((ROOT/table[1]).read_text('utf-8'),table)
        assert raw==sources[17][table[2]:table[3]]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==table[1]]
        assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(table[2],table[3]-table[2],table[2]+0x6000)
    assert symbols['FEQUIPMENTCODE']==1 and symbols['FEQUIPMENTCODE.VALUE']==0

    # Проверка девяти физических слов базиса и их двух байтовых полей.
    from ActionRenderBasisData import TABLE as RENDER_BASIS_TABLE, parse as parse_render_basis
    raw,labels=parse_render_basis((ROOT/RENDER_BASIS_TABLE[1]).read_text('utf-8'))
    assert raw==sources[17][0x3B00:0x3B12]
    assert all(symbols.get(k.upper())==v for k,v in labels.items())
    assert symbols['FBASISWORD']==2 and symbols['FBASISWORD.LOW']==0 and symbols['FBASISWORD.HIGH']==1
    rows=[p for p in source_map if p['path']==RENDER_BASIS_TABLE[1]]
    assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(0x3B00,18,0x9B00)

    # Проверка физических десяти исходных пропусков и завершающего кода списка.
    from ActionCandidateListData import TABLE as CANDIDATE_LIST_TABLE, parse as parse_candidate_list
    raw,labels=parse_candidate_list((ROOT/CANDIDATE_LIST_TABLE[1]).read_text('utf-8'))
    assert raw==sources[17][0x401C:0x4027]==bytes([255])*10+bytes([254])
    assert all(symbols.get(k.upper())==v for k,v in labels.items())
    assert symbols['FCANDIDATECODE']==1 and symbols['FCANDIDATECODE.CODE']==0
    rows=[p for p in source_map if p['path']==CANDIDATE_LIST_TABLE[1]]
    assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(0x401C,11,0xA01C)

    # Проверка физических STRUCT двух малых ресурсов связанных состояний.
    from ActionLinkedStateData import TABLES as LINKED_STATE_TABLES, parse as parse_linked_state_data
    for table in LINKED_STATE_TABLES:
        _,path,start,end,_,_,_=table
        raw,labels=parse_linked_state_data((ROOT/path).read_text('utf-8'),table)
        assert raw==sources[17][start:end]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==path]
        assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)
    assert symbols['FOVERLAYLINE']==4 and symbols['FCLASSSPAWNBYTE']==1

    # Проверка двух физических точек, их вложенных координат и кода, а не только адресных EQU.
    from ActionClipPointsData import POINTS as CLIP_POINTS, parse as parse_clip_point
    for name,offset,path in CLIP_POINTS:
        point_raw,point_labels=parse_clip_point((ROOT/path).read_text('utf-8'),name,offset)
        assert point_raw==sources[17][offset:offset+5]
        assert all(symbols.get(k.upper())==v for k,v in point_labels.items())
        items=[x for x in source_map if x['path']==path]
        assert len(items)==1 and (items[0]['offset'],items[0]['length'],items[0]['origin'])==(offset,5,offset+0x6000)
    assert symbols['FRENDERPROJECTEDPOINT']==5 and symbols['FRENDERPROJECTEDPOINT.CLIPCODE']==4

    # Проверка отдельно собираемых физических записей побайтовой копии 3DPART, со своими метками слота 19.
    from ThreeDOverlayData import verify_data as verify_three_d_overlay_data
    verify_three_d_overlay_data(ROOT,sources,source_map,symbols)

    # Проверка физических заголовков, групп и примитивов всех потоков OBJECT3D.
    from ActionModelPhysicalData import parse as parse_action_model
    models=[item for item in source_map if item['slot']==24 and item['kind']=='typed_data']
    assert len(models)==95 and sum(item['length'] for item in models)==9317
    for item in models:
        raw,labels=parse_action_model((ROOT/item['path']).read_text('utf-8'))
        assert raw==sources[24][item['offset']:item['offset']+item['length']]
        assert all(symbols.get(name.upper())==address for name,address in labels.items())
    assert symbols['FACTIONMODELHEADER']==2 and symbols['FACTIONMODELGROUP']==4
    assert symbols['FACTIONMODELGROUP.MASK']==0 and symbols['FACTIONMODELGROUP.COMPONENT2']==3

    # Проверка физических строк палитры и двух анимаций VOXAL.
    from VoxelPhysicalData import TABLES as VOXEL_ROWS, parse as parse_voxel_rows
    for module,path,start,end,width,count in VOXEL_ROWS:
        rows=[item for item in source_map if item['path']==path]
        assert len(rows)==1 and rows[0]['slot']==20 and rows[0]['offset']==start
        raw,labels=parse_voxel_rows((ROOT/path).read_text('utf-8'))
        assert len(raw)==width*count and raw==sources[20][start:end]
        assert all(symbols.get(name.upper())==address for name,address in labels.items())
    assert symbols['FEFFECTBYTEROW16']==16 and symbols['FEFFECTBYTEROW32']==32
    assert symbols['FEFFECTBYTEROW16.PAIR15']==15 and symbols['FEFFECTBYTEROW32.PAIR31']==31

    # Проверка всех шести ключей ресурсов перенесённого загрузчика полёта.
    from ActionBootFileKeys import PATH as action_boot_file_keys_path, parse as parse_action_boot_keys, render as render_action_boot_keys
    action_boot_keys_raw=sources[17][0x113:0x149]
    assert parse_action_boot_keys((ROOT/action_boot_file_keys_path).read_text('utf-8'))==action_boot_keys_raw
    _, action_boot_keys_labels=render_action_boot_keys(action_boot_keys_raw)
    assert all(symbols[key.upper()]==value for key,value in action_boot_keys_labels.items())

    # Проверка исходного bitmap вступления, физических строк атрибутов и всего прочитанного упакованного потока.
    from IntroScreenResources import BITMAP as intro_bitmap, ATTRIBUTES as intro_attributes
    from IntroScreenResources import PACKED as intro_packed, TAIL as intro_screen_tail
    from IntroScreenResources import parse_attributes as parse_intro_attributes, render_attributes as render_intro_attributes
    assert (ROOT/intro_bitmap).read_bytes()==sources[3][0xB31:0x2331]
    assert parse_intro_attributes((ROOT/intro_attributes).read_text('utf-8'))==sources[3][0x2331:0x2631]
    _, intro_screen_labels=render_intro_attributes(sources[3][0x2331:0x2631])
    assert all(symbols[key.upper()]==value for key,value in intro_screen_labels.items())
    assert (ROOT/intro_packed).read_bytes()==sources[3][0x26CB:0x2C6B]
    assert (ROOT/intro_screen_tail).read_bytes()==sources[3][0x2C6B:0x2D00]

    # Проверка двух физических экранов выбора, без предположения об их загрузке.
    from PublishChooseScreens import parse_attributes as parse_choose_attributes
    for slot,name in ((31,'choose1'),(32,'choose2')):
        prefix=f'Source/Resources/{slot}_{name}/'
        assert (ROOT/(prefix+'Bitmap.bin')).read_bytes()==sources[slot][:6144]
        assert parse_choose_attributes((ROOT/(prefix+'Attributes.asm')).read_text('utf-8'))==sources[slot][6144:6912]
    assert symbols['FCHOOSESCREENATTRIBUTES']==32

    # Проверка отдельной дисковой копии начального блока полётного состояния.
    mirror=(ROOT/'Source/Resources/18_DATAS/ActionInitialBlock.bin').read_bytes()
    assert mirror==sources[18][:0x1C2D]==sources[17][0x2C00:0x482D]
    assert (ROOT/'Source/Resources/18_DATAS/SectorTail.bin').read_bytes()==sources[18][0x1C2D:]

    # Проверка каждого физического поля SAVE по общим структурам станции.
    from SavedStateLayout import SLOTS as SAVE_SLOTS, structures as save_structures, parse as parse_save
    save_types = save_structures()
    for slot, name in SAVE_SLOTS:
        for item in source_map:
            if item['slot'] != slot or item['kind'] != 'typed_data':
                continue
            text = (ROOT / item['path']).read_text('utf-8')
            raw, labels = parse_save(text, save_types)
            assert raw == sources[slot][item['offset']:item['offset'] + item['length']]
            module = re.search(r'module\s+(\w+)', text)[1]
            for label, relative in labels.items():
                assert symbols[(module + '.' + label).upper()] == item['offset'] + relative

    # Проверка связанного набора BAR и BD, геометрии каждого кадра и сохранения неизвестных хвостов.
    from FighterAssetData import parse as parse_fighter, decode as decode_fighter
    bar = sources[39][:3076]
    banks = [sources[40 + bank][:length] for bank, length in enumerate((16268,16152,16248,12048))]
    _, _, sprites, _ = decode_fighter(bar, banks)
    text = (ROOT/'Source/Resources/39_BAR/PoseSequences.asm').read_text('utf-8')
    actual, labels = parse_fighter(text)
    assert actual == bar
    for label, offset in labels.items():
        assert symbols[('FighterPoseData.' + label).upper()] == offset
    assert symbols['FFIGHTERPOSEPOINTER'] == 2 and symbols['FFIGHTERPOSEHEADER'] == 4
    assert symbols['FFIGHTERPOSESTEP'] == 14
    for field, offset in (('BANKINDEX',9),('SPRITEADDRESS',10),('WIDTHBYTES',12),('HEIGHT',13)):
        assert symbols['FFIGHTERPOSESTEP.' + field] == offset
    for bank, offset, width, height in sprites:
        path = f'Source/Resources/{40+bank}_BD{bank}/Sprite{offset:04X}.bin'
        assert (ROOT/path).read_bytes() == banks[bank][offset:offset + 2*width*height]

    # Проверка трёх исходных диагностических строк и управляющих CR/LF.
    from DiagnosticMessages import PATH as diagnostic_path, DATA as diagnostic_data, LABELS as diagnostic_labels, parse as parse_diagnostic
    raw, labels = parse_diagnostic((ROOT/diagnostic_path).read_text('utf-8'))
    assert raw == diagnostic_data == sources[17][0x4CD6:0x4CEA]
    assert labels == diagnostic_labels
    assert all(symbols[('ActionDiagnosticMessages.'+label).upper()]==address for label,address in labels.items())

    # Проверка 728 байтов физического состояния игрока и его дисковых копий.
    from PlayerSavedFields import verify_all as verify_player_saved_fields, TABLES as PLAYER_SAVED_TABLES
    assert verify_player_saved_fields() == 728
    for slot,name in ((4,'STATIONF'),*SAVE_SLOTS):
        for _,module,_,_ in PLAYER_SAVED_TABLES:
            path=('Source/Station/Data/' if slot==4 else f'Source/Resources/{slot}_{name}/')+module+'.asm'
            item=next(item for item in source_map if item['path']==path)
            raw,labels=parse_save((ROOT/path).read_text('utf-8'),save_types)
            prefix=module if slot==4 else name.title()+module
            base=item['origin'] if item['origin'] is not None else item['offset']
            assert all(symbols[(prefix+'.'+label).upper()]==base+offset for label,offset in labels.items())

    # Проверка всех физических шаблонов, ограничителей и пар параметров создания.
    from SpawnPhysicalRows import TABLES as SPAWN_TABLES, TYPES as SPAWN_TYPES, parse as parse_spawn
    for start,end,module,path in SPAWN_TABLES:
        raw,labels=parse_spawn((ROOT/path).read_text('utf-8'))
        offset=start-0x6000+0x23D
        assert raw==sources[17][offset:offset+end-start]
        assert all(symbols[(module+'.'+label).upper()]==start+relative for label,relative in labels.items())
    for kind,fields in SPAWN_TYPES.items():
        offset=0
        for field,size in fields:
            assert symbols[(kind+'.'+field).upper()]==offset
            offset+=size
        assert symbols[kind.upper()]==offset

    # Проверка синусоиды D3D и двух восьмифазных форм прицельного значка.
    from OverlayPreviewTables import TABLES as OVERLAY_PREVIEW_TABLES, parse as parse_overlay_preview, verify_originals as verify_overlay_preview
    verify_overlay_preview()
    for slot,offset,origin,size,module,path,kind in OVERLAY_PREVIEW_TABLES:
        raw,labels=parse_overlay_preview((ROOT/path).read_text('utf-8'))
        assert raw==sources[slot][offset:offset+size]
        assert all(symbols[(module+'.'+label).upper()]==origin+position for label,position in labels.items())
    assert symbols['FOVERLAYGLYPHPHASE']==16

    # Проверка исходного BASIC и адреса, указанного обеими формами числа USR.
    from BasicProgramData import PARTS as BASIC_PROGRAM_PARTS, parse as parse_basic_program, original_program
    original_program()
    for start,end,origin,name,_ in BASIC_PROGRAM_PARTS:
        text=(ROOT/f'Source/Basic/Data/{name}.asm').read_text('utf-8')
        raw,labels=parse_basic_program(text,origin)
        assert raw==sources[3][start:end]
        module=re.search(r'module (\w+)',text)[1]
        assert all(symbols[(module+'.'+label).upper()]==address for label,address in labels.items())
    assert symbols['FBASICLINEHEADER']==4 and symbols['FBASICSMALLINTEGER']==5

    # Проверка физических параметров вступления и каждой исходной записи, включая два состояния фаз.
    from IntroPhysicalParameters import BLOCKS as intro_parameter_blocks, TYPES as intro_parameter_types
    from IntroPhysicalParameters import parse as parse_intro_parameters, render as render_intro_parameters, source_path
    for block in intro_parameter_blocks:
        offset, length, _, filename = block
        raw = sources[3][offset:offset+length]
        assert parse_intro_parameters(block, (ROOT/source_path(filename)).read_text('utf-8')) == raw
        _, labels = render_intro_parameters(block, raw)
        assert all(symbols[key.upper()] == value for key, value in labels.items())
    for name, field, _ in intro_parameter_types:
        assert symbols[name.upper()] == 1 and symbols[(name+'.'+field).upper()] == 0

    # Проверка исходных отсчётов, нулевая вторая половина не заменяется результатом исполнения.
    from IntroCoordinateSeed import PATH as intro_coordinate_path, parse as parse_intro_coordinate_seed
    assert parse_intro_coordinate_seed((ROOT/intro_coordinate_path).read_text('utf-8'))==sources[3][256:512]
    assert symbols['FINTROCOORDINATESAMPLE']==1
    assert all(symbols[f'INTROCOORDINATESEED.INDEX{index:02X}']==0x6400+index for index in range(256))

    # Проверка реального служебного маркера автозапуска сразу после логического BASIC.
    autostart=(ROOT/'Source/Basic/Data/Autostart.asm').read_text('utf-8')
    values=re.search(r'Entry:\s+FTrDosBasicAutostart\s*\{([^}]+)\}', '\n'.join(line.partition(';')[0] for line in autostart.splitlines()))[1]
    fields=[int(value.strip()[1:],16) for value in values.split(',')]
    assert fields==[0x80,0xAA,20] and sources[3][119:123]==bytes((fields[0],fields[1],fields[2]&255,fields[2]>>8))
    assert symbols['FTRDOSBASICAUTOSTART']==4 and symbols['FTRDOSBASICAUTOSTART.LINENUMBER']==2
    assert symbols['BASICPROGRAMAUTOSTART.ENTRY']==119

    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.
    from ActionRenderPhasesData import PATH as RENDER_PHASES_PATH, parse as parse_render_phases
    phase_records=[i for i in source_map if i['path']==RENDER_PHASES_PATH]
    assert len(phase_records)==1
    phase_item=phase_records[0]
    assert (phase_item['slot'],phase_item['offset'],phase_item['length'],phase_item['origin'])==(17,0x3B12,3,0x9B12)
    phase_raw,phase_labels=parse_render_phases((ROOT/RENDER_PHASES_PATH).read_text('utf-8'))
    assert phase_raw==sources[17][0x3B12:0x3B15]
    assert all(symbols.get(k.upper())==v for k,v in phase_labels.items())
    assert symbols['FRENDERPHASES']==3 and symbols['FACTIONRENDERNODE']==14
    for index in range(3):
        assert symbols['FRENDERPHASES.PHASE'+str(index)]==index
        assert symbols['FACTIONRENDERNODE.PHASES.PHASE'+str(index)]==5+index

    # Проверка двух исходных байтов сопровождающей точки и физических полей X/Y.
    from ActionAimPointData import PATH as AIM_POINT_PATH, parse as parse_aim_point
    aim_records=[i for i in source_map if i['path']==AIM_POINT_PATH]
    assert len(aim_records)==1
    aim_item=aim_records[0]
    assert (aim_item['slot'],aim_item['offset'],aim_item['length'],aim_item['origin'])==(17,0x3B19,2,0x9B19)
    aim_raw,aim_labels=parse_aim_point((ROOT/AIM_POINT_PATH).read_text('utf-8'))
    assert aim_raw==sources[17][0x3B19:0x3B1B]
    assert all(symbols.get(k.upper())==v for k,v in aim_labels.items())
    assert (symbols['FACTIONAIMPOINT'],symbols['FACTIONAIMPOINT.X'],symbols['FACTIONAIMPOINT.Y'])==(2,0,1)

    # Проверка физических записей композиции и точной грамматики фактических DB-команд.
    from MusicCompositionSource import descriptions as composition_descriptions, parse as parse_composition, STRUCTURES as COMPOSITION_STRUCTURES
    composition = sources[10][0xC00:0x1C29]
    music_composition_parts = 0
    for item_description in composition_descriptions(composition):
        path = item_description['path']
        matches = [item for item in source_map if item['path'] == path]
        if not matches:
            continue
        assert len(matches) == 1
        item = matches[0]
        start, length = item_description['offset'], item_description['length']
        raw, labels = parse_composition((ROOT/path).read_text('utf-8'), composition, item_description)
        assert (item['slot'], item['offset'], item['length'], item['origin']) == (10, 0xC00+start, length, 0xE700+start)
        assert raw == composition[start:start+length]
        assert all(symbols.get(key.upper()) == value for key, value in labels.items())
        music_composition_parts += 1
    assert music_composition_parts in (0, 72)
    if music_composition_parts:
        for structure, fields in COMPOSITION_STRUCTURES.items():
            offset = 0
            for name, width, directive, note in fields:
                assert symbols[structure.upper()+'.'+name.upper()] == offset
                offset += width
            assert symbols[structure.upper()] == offset

    # Проверка фактически записанного CP866-сценария по DB и адресам его именованных входов.
    market_script_bytes = 0
    market_script_labels = 0
    script_entries = [item for item in source_map if item["path"] == MARKET_SCRIPT_PATH]
    if script_entries:
        if len(script_entries) != 1:
            raise ValueError("Сценарий зарегистрирован неоднозначно")
        item = script_entries[0]
        raw, labels = parse_market_script((ROOT / MARKET_SCRIPT_PATH).read_text(encoding="utf-8"))
        end = sources[5].index(0, MARKET_SCRIPT_START) + 1
        if (item["slot"], item["offset"], item["length"], item["origin"]) != (5, MARKET_SCRIPT_START, end - MARKET_SCRIPT_START, 0xC000 + MARKET_SCRIPT_START):
            raise ValueError("Неверная физическая граница сценария")
        if raw != sources[5][MARKET_SCRIPT_START:end]:
            raise ValueError("Изменились исходные байты сценария LANG")
        if any(symbols.get(key.upper()) != value for key, value in labels.items()):
            raise ValueError("Адреса меток сценария отличаются от реестра")
        market_script_bytes = len(raw)
        market_script_labels = len(labels)

    # Проверка фактических DB двух описательных CP866-потоков и физических адресов всех записей.
    from PreviewDescriptionTables import TABLES as PREVIEW_TEXT_TABLES, parse as parse_preview_text
    preview_description_bytes = 0
    preview_description_labels = 0
    for _, path, start, end, _ in PREVIEW_TEXT_TABLES:
        entries = [item for item in source_map if item['path'] == path]
        if not entries:
            continue
        if len(entries) != 1:
            raise ValueError('Неоднозначная регистрация описаний D3D')
        item = entries[0]
        raw, labels = parse_preview_text((ROOT/path).read_text(encoding='utf-8'), 0xC000+start)
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, start, end-start, 0xC000+start):
            raise ValueError('Изменилось физическое размещение описаний D3D')
        if raw != sources[6][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились байты либо метки описаний D3D')
        preview_description_bytes += len(raw)
        preview_description_labels += len(labels)

    # Проверка фактических байтов CP866 цен и их управляющих разделителей.
    from PreviewPriceTable import PATH as PREVIEW_PRICE_PATH, START as PREVIEW_PRICE_START, END as PREVIEW_PRICE_END, parse as parse_preview_prices
    preview_price_bytes = 0
    preview_price_labels = 0
    price_entries = [item for item in source_map if item['path'] == PREVIEW_PRICE_PATH]
    if price_entries:
        if len(price_entries) != 1:
            raise ValueError('Неоднозначная регистрация цен D3D')
        item = price_entries[0]
        raw, labels = parse_preview_prices((ROOT/PREVIEW_PRICE_PATH).read_text(encoding='utf-8'), 0xC000+PREVIEW_PRICE_START)
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, PREVIEW_PRICE_START, PREVIEW_PRICE_END-PREVIEW_PRICE_START, 0xC000+PREVIEW_PRICE_START):
            raise ValueError('Изменилось размещение цен D3D')
        if raw != sources[6][PREVIEW_PRICE_START:PREVIEW_PRICE_END] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились исходные байты либо метки цен D3D')
        preview_price_bytes = len(raw)
        preview_price_labels = len(labels)

    # Проверка шестнадцати физических пар начальных моделей рынка по полям структуры.
    from ModelAvailabilityTable import PATH as MODEL_AVAILABILITY_PATH, START as MODEL_AVAILABILITY_START, END as MODEL_AVAILABILITY_END, FIELDS as MODEL_AVAILABILITY_FIELDS
    model_availability_records = 0
    availability_entries = [item for item in source_map if item['path'] == MODEL_AVAILABILITY_PATH]
    if availability_entries:
        if len(availability_entries) != 1:
            raise ValueError('Неоднозначная регистрация доступности моделей')
        item = availability_entries[0]
        if (item['slot'], item['offset'], item['length'], item['origin']) != (4, MODEL_AVAILABILITY_START, 32, 0x94BC):
            raise ValueError('Изменились границы доступности моделей')
        text = '\n'.join(line.split(';',1)[0] for line in (ROOT/MODEL_AVAILABILITY_PATH).read_text(encoding='utf-8').splitlines())
        records_available = re.findall(r'(Level[0-9]{2}):\s+FModelAvailability\s*\{([^}]+)\}', text)
        if len(records_available) != 16 or symbols['FMODELAVAILABILITY'] != 2:
            raise ValueError('Изменился размер структуры либо число уровней')
        raw = bytearray()
        for i,(label,arguments) in enumerate(records_available):
            if label != 'Level'+str(i+1).zfill(2):
                raise ValueError('Неверный порядок уровней доступности')
            values = [number(value) for value in arguments.split(',')]
            if len(values) != 2:
                raise ValueError('Изменилось число полей доступности')
            address = 0x94BC+2*i
            if symbols['MODELAVAILABILITY.'+label.upper()] != address:
                raise ValueError('Изменилась база физической записи доступности')
            for offset,field in enumerate(MODEL_AVAILABILITY_FIELDS):
                if symbols['FMODELAVAILABILITY.'+field.upper()] != offset or symbols['MODELAVAILABILITY.'+label.upper()+'.'+field.upper()] != address+offset:
                    raise ValueError('Изменилось смещение поля доступности')
            raw.extend(values)
        if raw != sources[4][MODEL_AVAILABILITY_START:MODEL_AVAILABILITY_END]:
            raise ValueError('Изменились исходные пары доступности моделей')
        model_availability_records = len(records_available)

    # Проверка физических исходных параметров, матрицы и пар указателей моделей по реальным полям.
    from PreviewSceneTables import TABLES as PREVIEW_SCENE_TABLES, parse as parse_preview_scene
    from PreviewDrawStateTable import TABLE as PREVIEW_DRAW_STATE_TABLE
    from PreviewEdgeData import TABLES as PREVIEW_EDGE_TABLES
    from PreviewPolygonData import TABLES as PREVIEWPOLYGONDATA_TABLES
    from PreviewFaceGateData import TABLES as PREVIEWFACEGATEDATA_TABLES
    from PreviewClipWorkData import TABLES as PREVIEWCLIPWORKDATA_TABLES
    from PreviewClipProductData import TABLES as PREVIEWCLIPPRODUCTDATA_TABLES
    from PreviewLineWorkData import TABLES as PREVIEWLINEWORKDATA_TABLES
    from PreviewQueueRenderData import TABLES as PREVIEWQUEUERENDERDATA_TABLES
    from PreviewFrameData import TABLES as PREVIEWFRAMEDATA_TABLES
    preview_scene_records = {}
    for module,path,start,end,structure,fields,names in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE, *PREVIEW_EDGE_TABLES, *PREVIEWPOLYGONDATA_TABLES, *PREVIEWFACEGATEDATA_TABLES, *PREVIEWCLIPWORKDATA_TABLES, *PREVIEWCLIPPRODUCTDATA_TABLES, *PREVIEWLINEWORKDATA_TABLES, *PREVIEWQUEUERENDERDATA_TABLES, *PREVIEWFRAMEDATA_TABLES):
        entries = [item for item in source_map if item['path'] == path]
        if not entries:
            continue
        if len(entries) != 1:
            raise ValueError('Неоднозначная регистрация '+module)
        item = entries[0]
        if (item['slot'],item['offset'],item['length'],item['origin']) != (6,start,end-start,0xC000+start):
            raise ValueError('Изменилось физическое размещение '+module)
        raw,labels = parse_preview_scene((ROOT/path).read_text(encoding='utf-8'), (module,path,start,end,structure,fields,names))
        if raw != sources[6][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились исходные байты либо адреса '+module)
        offset = 0
        for field,width,_ in fields:
            if symbols.get(structure.upper()+'.'+field.upper()) != offset:
                raise ValueError('Изменилось поле '+structure)
            offset += width
        if symbols.get(structure.upper()) != offset:
            raise ValueError('Изменился размер '+structure)
        preview_scene_records[module] = len(names)

    # Проверка физической таблицы HELP с отдельным адресом загрузки банка 7.
    from HelpLineIndexFacts import TABLE as HELP_LINE_TABLE
    module,path,start,end,structure,fields,names = HELP_LINE_TABLE
    entries = [item for item in source_map if item['path'] == path]
    if len(entries) != 1 or (entries[0]['slot'],entries[0]['offset'],entries[0]['length'],entries[0]['origin']) != (8,start,end-start,0xDB00+start):
        raise ValueError('Изменилось размещение таблицы HELP')
    raw,labels = parse_preview_scene((ROOT/path).read_text('utf-8'), HELP_LINE_TABLE, 0xDB00)
    if raw != sources[8][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
        raise ValueError('Изменились указатели либо поля HELP')
    if symbols.get('FHELPLINEPOINTER') != 2 or symbols.get('FHELPLINEPOINTER.TEXTADDRESS') != 0:
        raise ValueError('Изменилась структура указателя HELP')

    # Проверка трёх физических четырёхбайтовых обозначений клавиш в фиксированном банке 2.
    from KeyLabelFacts import TABLE as KEY_LABEL_TABLE
    module,path,start,end,structure,fields,names = KEY_LABEL_TABLE
    entries = [item for item in source_map if item['path'] == path]
    if len(entries) != 1 or (entries[0]['slot'],entries[0]['offset'],entries[0]['length'],entries[0]['origin']) != (4,start,end-start,0x6000+start):
        raise ValueError('Изменилось размещение клавишных обозначений')
    raw,labels = parse_preview_scene((ROOT/path).read_text('utf-8'), KEY_LABEL_TABLE, 0x6000)
    if raw != sources[4][start:end] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
        raise ValueError('Изменились клавишные обозначения либо их поля')
    if symbols.get(structure.upper()) != 4 or any(symbols.get(structure.upper()+'.'+field.upper()) != index for index,(field,_,_) in enumerate(fields)):
        raise ValueError('Изменилась структура клавишного обозначения')

    # Проверка реальных структур, меток и каждого исходного байта префиксов моделей.
    from PreviewModelGroupTables import tables as preview_model_tables, parse as parse_preview_model, STRUCTURES as PREVIEW_MODEL_STRUCTURES
    preview_model_records = {}
    for model in preview_model_tables(sources[6]):
        entries = [item for item in source_map if item['path'] == model['path']]
        if not entries:
            continue
        if len(entries) != 1:
            raise ValueError('Неоднозначная регистрация групп модели')
        item = entries[0]
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, model['start'], model['end']-model['start'], model['pointer']):
            raise ValueError('Изменилось физическое размещение групп модели')
        raw, labels = parse_preview_model((ROOT/model['path']).read_text('utf-8'), model)
        if raw != sources[6][model['start']:model['end']] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились исходные байты или метки групп модели')
        preview_model_records[model['name']] = len(model['groups'])
    if preview_model_records:
        for structure,fields in PREVIEW_MODEL_STRUCTURES:
            offset = 0
            for field,width,meaning in fields:
                if symbols.get(structure.upper()+'.'+field.upper()) != offset:
                    raise ValueError('Изменилось поле структуры модели')
                offset += width
            if symbols.get(structure.upper()) != offset:
                raise ValueError('Изменился размер структуры модели')

    # Проверка физических пятибайтовых записей и хвоста исходной страницы проекции.
    from PreviewProjectedVertexTable import PATH as PROJECTED_PATH, FIELDS as PROJECTED_FIELDS, parse as parse_projected
    preview_projected_vertices = 0
    projected_entries = [item for item in source_map if item['path'] == PROJECTED_PATH]
    if projected_entries:
        if len(projected_entries) != 1:
            raise ValueError('Неоднозначный буфер проекции')
        item = projected_entries[0]
        if (item['slot'],item['offset'],item['length'],item['origin']) != (6,0x600,256,0xC600):
            raise ValueError('Изменилось размещение исходного буфера проекции')
        raw, labels = parse_projected((ROOT/PROJECTED_PATH).read_text('utf-8'))
        if raw != sources[6][0x600:0x700] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились байты или метки исходного буфера проекции')
        offset = 0
        for field,width,meaning in PROJECTED_FIELDS:
            if symbols.get('FPREVIEWPROJECTEDVERTEX.'+field.upper()) != offset:
                raise ValueError('Изменилось поле пятибайтовой записи')
            offset += width
        if symbols.get('FPREVIEWPROJECTEDVERTEX') != 5:
            raise ValueError('Изменился размер пятибайтовой записи')
        preview_projected_vertices = 51

    # Проверка двух исходных таблиц пиксельных масок и их фактического размещения.
    from PreviewEdgeData import MASK_PATH, parse_bytes as parse_mask_bytes
    preview_pixel_masks = 0
    mask_entries = [item for item in source_map if item['path'] == MASK_PATH]
    if mask_entries:
        if len(mask_entries) != 1:
            raise ValueError('Неоднозначная регистрация масок рёбер')
        item = mask_entries[0]
        if (item['slot'],item['offset'],item['length'],item['origin']) != (6,0xDB0,16,0xCDB0):
            raise ValueError('Изменилось размещение масок рёбер')
        raw, labels = parse_mask_bytes((ROOT/MASK_PATH).read_text('utf-8'),0xCDB0)
        if raw != sources[6][0xDB0:0xDC0] or raw != bytes([128>>i for i in range(8)]+[255^(128>>i) for i in range(8)]):
            raise ValueError('Изменились исходные маски пикселя')
        if any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились метки масок пикселя')
        preview_pixel_masks = 16

    # Проверка исходных DB свёрнутых квадратов и точной целочисленной формулы всей страницы.
    from PreviewSquareTable import PATH as PREVIEW_SQUARE_PATH, START as PREVIEW_SQUARE_START, END as PREVIEW_SQUARE_END, parse as parse_preview_square
    preview_square_bytes = 0
    square_entries = [item for item in source_map if item['path'] == PREVIEW_SQUARE_PATH]
    if square_entries:
        if len(square_entries) != 1:
            raise ValueError('Неоднозначная регистрация свёрнутых квадратов')
        item = square_entries[0]
        raw, labels = parse_preview_square((ROOT/PREVIEW_SQUARE_PATH).read_text(encoding='utf-8'), 0xC300)
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, PREVIEW_SQUARE_START, PREVIEW_SQUARE_END-PREVIEW_SQUARE_START, 0xC300):
            raise ValueError('Изменилось размещение свёрнутых квадратов D3D')
        if raw != sources[6][PREVIEW_SQUARE_START:PREVIEW_SQUARE_END] or raw != bytes(min(i,255-i)**2//127 for i in range(256)):
            raise ValueError('Изменились исходные байты таблицы квадратов D3D')
        if labels != {'FoldedSquare127.Values':0xC300} or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились адресные метки таблицы квадратов')
        preview_square_bytes = len(raw)

    # Проверка физических узлов очереди D3D, полей структуры и исходных невыделенных значений.
    from PreviewQueueTable import PATH as PREVIEW_QUEUE_PATH, START as PREVIEW_QUEUE_START, END as PREVIEW_QUEUE_END, FIELDS as PREVIEW_QUEUE_FIELDS, parse as parse_preview_queue
    preview_queue_records = 0
    queue_entries = [item for item in source_map if item['path'] == PREVIEW_QUEUE_PATH]
    if queue_entries:
        if len(queue_entries) != 1:
            raise ValueError('Неоднозначная регистрация очереди D3D')
        item = queue_entries[0]
        if (item['slot'], item['offset'], item['length'], item['origin']) != (6, PREVIEW_QUEUE_START, PREVIEW_QUEUE_END-PREVIEW_QUEUE_START, 0xC700):
            raise ValueError('Изменилось физическое размещение очереди D3D')
        raw, labels = parse_preview_queue((ROOT/PREVIEW_QUEUE_PATH).read_text(encoding='utf-8'))
        if raw != sources[6][PREVIEW_QUEUE_START:PREVIEW_QUEUE_END] or any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились исходные байты либо метки узлов D3D')
        offset = 0
        for field,width,_ in PREVIEW_QUEUE_FIELDS:
            if symbols.get('FPREVIEWQUEUENODE.'+field.upper()) != offset:
                raise ValueError('Изменилось физическое поле узла D3D')
            offset += width
        if symbols.get('FPREVIEWQUEUENODE') != offset or offset != 14:
            raise ValueError('Изменился размер физического узла D3D')
        preview_queue_records = 18

    # Проверка физических инициализаторов интерфейса по полям его структуры.
    text = (ROOT/"Source/Station/Data/InterfaceItems.asm").read_text(encoding="utf-8")
    text = "\n".join(line.split(";",1)[0] for line in text.splitlines())
    records = re.findall(r"FInterfaceItem\s*\{([^}]+)\}",text)
    widths = [1]*6+[2]+[1]*4+[2,2]
    packed = bytearray()
    for record in records:
        values = [number(value) for value in record.split(",")]
        if len(values) != len(widths):
            raise ValueError("Неверное число полей FInterfaceItem")
        for value,width in zip(values,widths):
            packed += value.to_bytes(width,"little")
    packed += b"\x80"
    if packed != sources[4][0x90FD:0x90FD+len(packed)] or len(records) != 46:
        raise ValueError("Инициализаторы интерфейса отличаются от оригинала")

    # Проверка каждого физического экземпляра таблиц токенов по исходному символу и адресу.
    token_text = (ROOT / "Source/Text/Data/TokenBindings.asm").read_text(encoding="utf-8")
    token_text = "\n".join(line.split(";", 1)[0] for line in token_text.splitlines())
    tokens = re.findall(r"FScriptToken\s*\{([^}]+)\}", token_text)
    token_bytes = bytearray()
    for token in tokens:
        values = [number(value) for value in token.split(",")]
        if len(values) != 2:
            raise ValueError("Неверное число полей FScriptToken")
        token_bytes += values[0].to_bytes(1, "little") + values[1].to_bytes(2, "little")
    if len(tokens) != 102 or token_bytes != sources[5][0x935:0xA67]:
        raise ValueError("Физические записи токенов отличаются от оригинала")

    # Проверка трёх физических записей фазы по исходным словам Phase, Step и StepDelta.
    phase_text = (ROOT / "Source/Intro/Data/TexturePhases.asm").read_text(encoding="utf-8")
    phase_text = "\n".join(line.split(";", 1)[0] for line in phase_text.splitlines())
    phases = re.findall(r"FTexturePhase\s*\{([^}]+)\}", phase_text)
    phase_bytes = bytearray()
    for phase in phases:
        values = [number(value) for value in phase.split(",")]
        if len(values) != 3:
            raise ValueError("Неверное число полей FTexturePhase")
        phase_bytes += b"".join(value.to_bytes(2, "little") for value in values)
    if len(phases) != 3 or phase_bytes != sources[3][0x98A:0x99C]:
        raise ValueError("Физические записи фаз отличаются от оригинала")

    # Проверка всех физических переходов глифа, если в выпуске уже выделена эта таблица.
    glyph_routes = []
    glyph_path = ROOT / "Source/Station/Data/GlyphRoutes.asm"
    if glyph_path.exists():
        text = "\n".join(line.split(";", 1)[0] for line in glyph_path.read_text(encoding="utf-8").splitlines())
        glyph_routes = re.findall(r"FGlyphRoute\s*\{([^}]+)\}", text)
        route_bytes = bytearray()
        for route in glyph_routes:
            values = [number(value) for value in route.split(",")]
            if len(values) != 2:
                raise ValueError("Неверное число полей FGlyphRoute")
            route_bytes += b"".join(value.to_bytes(2, "little") for value in values)
        if len(glyph_routes) != 128 or route_bytes != sources[4][0x3200:0x3400]:
            raise ValueError("Таблица переходов глифа отличается от оригинала")
        if symbols["FGLYPHROUTE"] != 4 or symbols["FGLYPHFRAME"] != 16:
            raise ValueError("Не совпали размеры записи перехода или кадра глифа")

    # Проверка физических полей масок указателя и восьми пар сохранённого фона.
    pointer_counts = {}
    for path, structure, offset, length, count, field_count in (
            ("Source/Station/Data/PointerSprites.asm", "FPointerRasterRow", 0, 0x300, 192, 4),
            ("Source/Station/Data/PointerBackground.asm", "FPointerSavedRow", 0x821, 16, 8, 2)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";", 1)[0] for line in (ROOT / path).read_text(encoding="utf-8").splitlines())
        entries = re.findall(structure + r"\s*\{([^}]+)\}", text)
        raw = bytearray()
        for record in entries:
            values = [number(value) for value in record.split(",")]
            if len(values) != field_count:
                raise ValueError("Неверное число полей " + structure)
            raw.extend(values)
        if len(entries) != count or raw != sources[4][offset:offset+length]:
            raise ValueError("Физические записи указателя отличаются от оригинала " + path)
        if symbols[structure.upper()] != field_count:
            raise ValueError("Не совпал физический размер " + structure)
        pointer_counts[structure] = len(entries)

    # Проверка единственного физического состояния мыши по девяти исходным байтам.
    mouse_records = 0
    mouse_path = "Source/Station/Data/MouseInput.asm"
    if any(item["path"] == mouse_path for item in source_map):
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / mouse_path).read_text(encoding="utf-8").splitlines())
        mouse = re.findall(r"FMouseInput\s*\{([^}]+)\}",text)
        raw = bytes(number(v) for record in mouse for v in record.split(","))
        if len(mouse) != 1 or symbols["FMOUSEINPUT"] != 9 or raw != sources[4][0x831:0x83A]:
            raise ValueError("Физическая запись мыши отличается от оригинала")
        mouse_records = len(mouse)

    # Проверка физических флагов, направлений и клавиш по их реальным размерам и исходным байтам.
    pointer_input_records = {}
    for path, structure, offset, size, count, widths in (
            ("Source/Station/Data/InputFlags.asm","FInputFlags",0x994,6,1,[1]*6),
            ("Source/Station/Data/PointerDirections.asm","FPointerDirection",0x99A,32,16,[2]),
            ("Source/Station/Data/PointerKeys.asm","FKeyBinding",0x39B6,12,6,[1,1])):
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / path).read_text(encoding="utf-8").splitlines())
        records_input = re.findall(structure+r"\s*\{([^}]+)\}",text)
        raw = bytearray()
        for record in records_input:
            values = [number(v) for v in record.split(",")]
            if len(values) != len(widths):
                raise ValueError("Не совпало число полей "+structure)
            for value,width in zip(values,widths):raw.extend(value.to_bytes(width,"little"))
        if len(records_input) != count or symbols[structure.upper()] != sum(widths) or raw != sources[4][offset:offset+size]:
            raise ValueError("Физические записи ввода отличаются от оригинала "+path)
        pointer_input_records[structure] = len(records_input)

    # Проверка физического BCD-счётчика, собственного стека ISR и цепочки возвратов рисователя.
    station_irq_records = {}
    for path, structure, offset, size, count, widths in (
            ("Source/Station/Data/StationTimer.asm","FStationBcdCounter",0x383B,4,1,[1]*4),
            ("Source/Station/Data/InterruptStack.asm","FStationIrqStorage",0x3C13,48,1,[2]*24),
            ("Source/Station/Data/WindowFillChain.asm","FWindowReturnChain",0x4102,20,1,[2]*10)):
        if not any(item["path"] == path for item in source_map):continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / path).read_text(encoding="utf-8").splitlines())
        entries_irq = re.findall(structure+r"\s*\{([^}]+)\}",text)
        raw = bytearray()
        for record in entries_irq:
            values = [number(v) for v in record.split(",")]
            if len(values) != len(widths):raise ValueError("Не совпало число полей "+structure)
            for value,width in zip(values,widths):raw.extend(value.to_bytes(width,"little"))
        if len(entries_irq) != count or symbols[structure.upper()] != sum(widths) or raw != sources[4][offset:offset+size]:
            raise ValueError("Физические записи ISR отличаются от оригинала "+path)
        station_irq_records[structure] = len(entries_irq)

    # Проверка якоря и всех 62 позиций кодов, нулевые пары являются исходными физическими записями.
    matrix_key_records = 0
    matrix_path = "Source/Station/Data/KeyboardCodes.asm"
    if any(item["path"] == matrix_path for item in source_map):
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / matrix_path).read_text(encoding="utf-8").splitlines())
        keys = re.findall(r"FKeyBinding\s*\{([^}]+)\}",text)
        raw = bytearray()
        for record in keys:
            values = [number(v) for v in record.split(",")]
            if len(values) != 2:raise ValueError("Не совпало число полей сигнатуры клавиши")
            raw.extend(values)
        if len(keys) != 63 or raw != sources[4][0x36AA:0x3728]:
            raise ValueError("Физические коды клавиш отличаются от оригинала")
        matrix_key_records = len(keys)

    # Проверка тегированных слов настроек, включая ещё не установленные игровые назначения второго блока.
    setting_records = {}
    for path, offset, count in (("Source/Station/Data/InterfaceChoices.asm",0x39AE,4),
                                ("Source/Station/Data/InterfaceColors.asm",0x39C2,3),
                                ("Source/Station/Data/ControlOptions.asm",0x39C8,43)):
        if not any(item["path"] == path for item in source_map):continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / path).read_text(encoding="utf-8").splitlines())
        entries = re.findall(r"FSettingWord\s*\{([^}]+)\}",text)
        raw = bytearray()
        for record in entries:
            values = [number(v) for v in record.split(",")]
            if len(values) != 2:raise ValueError("Не совпало число полей FSettingWord")
            raw.extend(values)
        if len(entries) != count or symbols["FSETTINGWORD"] != 2 or raw != sources[4][offset:offset+2*count]:
            raise ValueError("Физические настройки отличаются от оригинала "+path)
        setting_records[path] = len(entries)
    # Проверка исходных изменяемых подписей, строковые литералы и байтовые управляющие коды сохраняются.
    setting_text_bytes = 0
    path = "Source/Station/Data/SettingsText.asm"
    if any(item["path"] == path for item in source_map):
        raw = bytearray()
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            operation = re.search(r'\bdb\s+(.+)',line.split(";",1)[0],re.I)
            if operation:
                for quoted,encoded in re.findall(r'"([^"]*)"|#([0-9A-Fa-f]+)',operation[1]):
                    raw.extend(quoted.encode("ascii") if not encoded else bytes([int(encoded,16)]))
        if raw != sources[4][0x3728:0x3762]:raise ValueError("Подписи настроек отличаются от оригинала")
        setting_text_bytes = len(raw)

    # Проверка восьми исходных команд контекстного меню с семью CR и завершающим LF.
    context_menu_bytes = 0
    path = "Source/Station/Data/ContextMenuText.asm"
    if any(item["path"] == path for item in source_map):
        raw = bytearray()
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            operation = re.search(r'\bdb\s+(.+)',line.split(";",1)[0],re.I)
            if operation:raw.extend(int(v,16) for v in re.findall(r'#([0-9A-Fa-f]+)',operation[1]))
        end = sources[4].index(10,0x832E)+1
        if raw != sources[4][0x832E:end] or raw.count(13) != 7 or raw.count(10) != 1:
            raise ValueError("Команды контекстного меню отличаются от оригинала")
        context_menu_bytes = len(raw)

    # Проверка семи физических трёхбайтовых состояний, код генератора не заменяет их исходные значения.
    random_state_records = 0
    path = "Source/Station/Data/RandomStates.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        rows = re.findall(r"FRandomState\s*\{([^}]+)\}", text)
        raw = bytearray()
        for row in rows:
            values = [number(value) for value in row.split(",")]
            if len(values) != 2:
                raise ValueError("Не совпали поля FRandomState")
            raw.extend(values[0].to_bytes(2, "little"))
            raw.append(values[1])
        if len(rows) != 7 or raw != sources[4][0x48AC:0x48C1]:
            raise ValueError("Состояния генератора отличаются от оригинала")
        random_state_records = len(rows)

    # Проверка исходного пятибайтового входа характеристики по трём физическим полям.
    signature_input_records = 0
    path = "Source/Station/Data/CurrentSignature.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        records_found = re.findall(r"FSignatureInput\s*\{([^}]+)\}", text)
        if len(records_found) != 1:
            raise ValueError("Не найден единственный FSignatureInput")
        values = [number(value) for value in records_found[0].split(",")]
        if len(values) != 3:
            raise ValueError("Не совпали поля FSignatureInput")
        raw = values[0].to_bytes(2, "little") + values[1].to_bytes(2, "little") + bytes([values[2]])
        if raw != sources[4][0x383F:0x3844]:
            raise ValueError("Вход характеристики отличается от оригинала")
        signature_input_records = 1

    # Проверка физических категорий и тридцати двухбайтовых правил и строк рынка.
    market_records = {}
    for path, structure, start, end in (
        ("Source/Station/Data/MarketCategories.asm", None, 0x34DC, 0x34F7),
        ("Source/Station/Data/MarketRules.asm", "FMarketRule", 0x3518, 0x3554),
        ("Source/Station/Data/MarketRows.asm", "FMarketRow", 0x3555, 0x3592)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = (ROOT / path).read_text(encoding="utf-8")
        raw = bytearray()
        count = 0
        for line in text.splitlines():
            code = line.split(";", 1)[0]
            record = re.search((structure or "NoStructure") + r"\s*\{([^}]+)\}", code)
            byte = re.search(r"\bdb\s+(#[0-9A-Fa-f]+)\s*$", code, re.I)
            if record:
                values = [number(value) for value in record[1].split(",")]
                if len(values) != 2:
                    raise ValueError("Неверное число полей " + structure)
                raw.extend(values)
                count += 1
            elif byte:
                raw.append(number(byte[1]))
        if raw != sources[4][start:end]:
            raise ValueError("Не совпали физические байты рынка " + path)
        if structure and count != 30:
            raise ValueError("Не найдено 30 физических записей " + structure)
        market_records[structure or "CategoryBytes"] = count if structure else len(raw)

    # Проверка физического шестибайтового рабочего экземпляра присваивания.
    assignment_records = 0
    path = "Source/Text/Data/AssignmentScratch.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        found = re.findall(r"FAssignmentExpression\s*\{([^}]+)\}", text)
        if len(found) != 1:
            raise ValueError("Не найден физический FAssignmentExpression")
        values = [number(value) for value in found[0].split(",")]
        if len(values) != 3:
            raise ValueError("Неверное число полей FAssignmentExpression")
        raw = b"".join(value.to_bytes(2, "little") for value in values)
        if raw != sources[5][0xA7B:0xA81]:
            raise ValueError("Изменились исходные байты рабочего экземпляра присваивания")
        assignment_records = 1

    # Проверка десяти физических слов стека выражений, без утверждения о допустимой глубине.
    expression_stack_records = 0
    path = "Source/Text/Data/ExpressionStack.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        found = re.findall(r"FExpressionStackStorage\s*\{([^}]+)\}", text)
        if len(found) != 1:
            raise ValueError("Не найден физический FExpressionStackStorage")
        values = [number(value) for value in found[0].split(",")]
        if len(values) != 10:
            raise ValueError("Неверное число слов стека выражений")
        raw = b"".join(value.to_bytes(2, "little") for value in values)
        if raw != sources[5][0xA67:0xA7B]:
            raise ValueError("Изменились исходные слова стека выражений")
        expression_stack_records = 1

    # Проверка физического имени ACTION, размер текста и байт типа заданы STRUCT.
    action_file_keys = 0
    path = "Source/StationExit/Data/ActionFileName.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        found = re.findall(r'FTrDosFileKey\s*\{\s*\{\s*"([^"]*)"\s*\}\s*,\s*#([0-9A-Fa-f]+)\s*\}', text)
        if len(found) != 1 or len(found[0][0]) != 8:
            raise ValueError("Не найден физический девятибайтовый FTrDosFileKey")
        raw = found[0][0].encode("ascii") + bytes([int(found[0][1], 16)])
        if raw != sources[4][0x21B4:0x21BD]:
            raise ValueError("Изменились имя либо тип ACTION")
        action_file_keys = 1

    # Проверка исходного общего имени SAVE1 как физического FTrDosFileKey.
    save_slot_file_keys = 0
    path = "Source/Station/Data/SaveSlotFileName.asm"
    entries = [item for item in source_map if item['path'] == path]
    if entries:
        if len(entries) != 1 or (entries[0]['slot'], entries[0]['offset'], entries[0]['length'], entries[0]['origin']) != (4, 0x17DC, 9, 0x7530):
            raise ValueError('Изменилось размещение ключа SAVE1')
        text = (ROOT / path).read_text(encoding='utf-8')
        found = re.findall(r'FTrDosFileKey\s*\{\s*\{\s*"([^"]*)"\s*\}\s*,\s*#([0-9A-Fa-f]+)\s*\}', text)
        if len(found) != 1 or len(found[0][0]) != 8:
            raise ValueError('Не найден физический ключ SAVE1')
        raw = found[0][0].encode('ascii') + bytes([int(found[0][1], 16)])
        if raw != sources[4][0x17DC:0x17E5] or symbols.get('SAVESLOTFILENAME.ENTRY') != 0x7530:
            raise ValueError('Изменились имя, тип либо адрес ключа SAVE1')
        save_slot_file_keys = 1

    # Проверка физического имени FINALF в перенесённом финальном выходе.
    final_file_keys = 0
    path = "Source/StationFinalExit/Data/FinalFileName.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        found = re.findall(r'FTrDosFileKey\s*\{\s*\{\s*"([^"]*)"\s*\}\s*,\s*#([0-9A-Fa-f]+)\s*\}', text)
        if len(found) != 1 or len(found[0][0]) != 8:
            raise ValueError("Не найден физический ключ FINALF")
        raw = found[0][0].encode("ascii") + bytes([int(found[0][1], 16)])
        if raw != sources[4][0x1119:0x1122]:
            raise ValueError("Изменились имя либо тип FINALF")
        final_file_keys = 1

    # Проверка семи LF-строк, шести физических порогов и подписи ранга.
    rank_threshold_records = 0
    rank_text_bytes = 0
    path = "Source/Station/Data/PlayerRanks.asm"
    if any(item["path"] == path for item in source_map):
        raw = bytearray()
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            code = line.split(";", 1)[0].strip()
            item = re.fullmatch(r"\w+:\s+(db|FRankThreshold)\s+(.+)", code, re.I)
            if not item:
                continue
            values = item[2].strip().strip("{}").strip()
            data = bytes(number(value) for value in values.split(","))
            if item[1].lower() == "frankthreshold":
                if len(data) != 2:
                    raise ValueError("Неверный размер физического порога ранга")
                rank_threshold_records += 1
            else:
                rank_text_bytes += len(data)
            raw.extend(data)
        if rank_threshold_records != 6 or rank_text_bytes != 70 or raw != sources[4][0x4CE3:0x4D35]:
            raise ValueError("Изменились исходные строки либо пороги рангов")

    # Проверка полного исходного экземпляра состояния предложения, включая Unknown-поля.
    mission_offer_records = 0
    path = "Source/Station/Data/MissionOffer.asm"
    if any(item["path"] == path for item in source_map):
        text = (ROOT / path).read_text(encoding="utf-8")
        text = "\n".join(line.split(";", 1)[0] for line in text.splitlines())
        found = re.findall(r"FMissionOfferState\s*\{([^}]+)\}", text)
        if len(found) != 1:
            raise ValueError("Не найден физический FMissionOfferState")
        values = [number(value) for value in found[0].split(",")]
        if len(values) != 9:
            raise ValueError("Неверное число физических полей предложения")
        raw = b"".join(value.to_bytes(2, "little") for value in values[:7]) + bytes(values[7:])
        if raw != sources[4][0x38B0:0x38C0]:
            raise ValueError("Изменились исходные поля состояния предложения")
        mission_offer_records = 1

    # Проверка начального LF и всех шестнадцати исходных префиксов имени системы.
    system_prefix_bytes = 0
    path = "Source/Map/Data/SystemPrefixes.asm"
    if any(item["path"] == path for item in source_map):
        raw = bytearray()
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
            code = line.split(";", 1)[0].strip()
            found = re.fullmatch(r"\w+:\s+db\s+(.+)", code, re.I)
            if found:
                raw.extend(number(value) for value in found[1].split(","))
        if len(raw) != 88 or raw.count(10) != 17 or raw != sources[7][0x2721:0x2779]:
            raise ValueError("Изменились исходные LF-префиксы имени системы")
        system_prefix_bytes = len(raw)

    # Проверка двух исходных предупреждений миссии, включая оба управляющих ограничителя.
    mission_message_bytes = 0
    for path,begin,end in (("Source/Station/Data/MissionTonnageMessage.asm",0x11EE,0x11F9),
                           ("Source/Station/Data/MissionCancelMessage.asm",0x1261,0x1271)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = (ROOT / path).read_text(encoding="utf-8")
        found = re.findall(r"^Entry:\s+db\s+([^;\n]+)", text, re.M | re.I)
        if len(found) != 1:
            raise ValueError("Не найдена исходная строка предупреждения миссии")
        raw = bytes(number(value) for value in found[0].split(","))
        if raw != sources[4][begin:end] or raw[0] != 13 or raw[-1] != 10:
            raise ValueError("Изменилось предупреждение миссии")
        mission_message_bytes += len(raw)

    # Проверка исходного байтового размера выходного списка пересечений.
    clip_output_size_bytes = 0
    clip_output_size_path = "Source/Map/Data/ClipOutputSize.asm"
    if any(item["path"] == clip_output_size_path for item in source_map):
        text = (ROOT/clip_output_size_path).read_text(encoding="utf-8")
        values = re.findall(r"^OutputSize:\s+db\s+([^;\n]+)",text,re.M | re.I)
        if len(values) != 1 or bytes([number(values[0])]) != sources[7][0x1E3B:0x1E3C]:
            raise ValueError("Изменён физический счётчик выходных пересечений")
        clip_output_size_bytes = 1

    # Проверка физических экземпляров рабочих точек и произведений в исходных ячейках таблицы.
    clip_work_records = {}
    for path,structure,offset,length,widths,count in (
        ("Source/Map/Data/ClipEndpoints.asm","FProjectedPoint",0x1E2F,10,[2,2,1],2),
        ("Source/Map/Data/ClipProducts.asm","FClipProduct",0x1E6B,16,[2,2],4),
        ("Source/Map/Data/ClipCornerState.asm","FClipCornerState",0x1E39,2,[1,1],1)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(structure+r"\s*\{([^}]+)\}",text)
        raw = bytearray()
        for instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != len(widths):
                raise ValueError("Изменилось число полей рабочего состояния отсечения")
            for value,width in zip(values,widths):
                raw.extend(value.to_bytes(width,"little"))
        if len(instances) != count or symbols[structure.upper()] != sum(widths) or raw != sources[7][offset:offset+length]:
            raise ValueError("Изменились рабочие физические записи отсечения")
        clip_work_records[structure] = count

    # Проверка десяти дополнительных ключей и общих кодов без добавленного ограничителя.
    auxiliary_map_keys = auxiliary_map_code_bytes = 0
    auxiliary_keys_path = "Source/Station/Data/MapAuxiliaryPoints.asm"
    if any(item["path"] == auxiliary_keys_path for item in source_map):
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/auxiliary_keys_path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"Key([0-9]{2}):\s+FMapCoordinateKey\s*\{([^}]+)\}",text)
        if [int(index) for index,_ in instances] != list(range(10)) or symbols["FMAPCOORDINATEKEY"] != 4:
            raise ValueError("Изменились физические дополнительные ключи карты")
        raw = bytearray()
        for _,instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != 2:
                raise ValueError("Изменилось число слов дополнительного ключа")
            raw.extend(values[0].to_bytes(2,"little")+values[1].to_bytes(2,"little"))
        if raw != sources[4][0x397B:0x39A3]:
            raise ValueError("Изменились исходные байты дополнительных ключей")
        auxiliary_map_keys = 10
    auxiliary_codes_path = "Source/Station/Data/MapAuxiliaryCodes.asm"
    if any(item["path"] == auxiliary_codes_path for item in source_map):
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/auxiliary_codes_path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"State:\s+FMapMarkerCodes\s*\{([^}]+)\}",text)
        if len(instances) != 1:
            raise ValueError("Изменилось число экземпляров общих кодов карты")
        values = [number(value) for value in instances[0].split(",")]
        fields = ["ActiveCode","CompletionCode"]+["Unknown"+format(i,"02d") for i in range(2,11)]
        if len(values) != 11 or symbols["FMAPMARKERCODES"] != 11 or bytes(values) != sources[4][0x39A3:0x39AE]:
            raise ValueError("Изменились исходные общие коды карты")
        if any(symbols["FMAPMARKERCODES."+field.upper()] != offset for offset,field in enumerate(fields)):
            raise ValueError("Изменились физические смещения общих кодов карты")
        auxiliary_map_code_bytes = 11

    # Проверка всех исходных фаз шести ресурсов маркеров и их сохранённых конечных байтов.
    marker_sprite_phase_records = 0
    for name,address in (("Selected",0xCDC3),("Secondary",0xCE43),("ActiveAux",0xCEC3),
                         ("Cursor",0xCF43),("Primary",0xCFC3),("Stored",0xD043)):
        path = "Source/Map/Resources/Marker"+name+".asm"
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"Phase([0-7]):\s+FMapMarkerPhase\s*\{([^}]+)\}",text)
        if [int(phase) for phase,_ in instances] != list(range(8)):
            raise ValueError("Изменились физические фазы маркера " + name)
        raw = bytearray()
        for phase,instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != 16:
                raise ValueError("Изменилось число байтов фазы маркера " + name)
            raw.extend(values)
        fields = ["Row"+str(row)+side for row in range(7) for side in ("Left","Right")]+["UnknownTail0","UnknownTail1"]
        if symbols["FMAPMARKERPHASE"] != 16 or any(symbols["FMAPMARKERPHASE."+field.upper()] != offset for offset,field in enumerate(fields)):
            raise ValueError("Изменились поля физической фазы маркера")
        if raw != sources[7][address-0xC000:address-0xC000+128]:
            raise ValueError("Изменились исходные байты маркера " + name)
        marker_sprite_phase_records += 8

    # Проверка циклических смещений, однобайтовых ограничителей и всех трёхстрочных фаз.
    variant_path_points = variant_sprite_phases = 0
    for radius,address in ((7,0xCA45),(10,0xCA7E),(13,0xCACF),(16,0xCB38),(19,0xCBB9),(22,0xCC52)):
        path = "Source/Map/Data/VariantPath"+str(radius)+".asm"
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"Point([0-9]{2}):\s+FMapPathPoint\s*\{([^}]+)\}",text)
        if [int(index) for index,_ in instances] != list(range(4*radius)) or symbols["FMAPPATHPOINT"] != 2:
            raise ValueError("Изменились физические записи циклической траектории")
        if symbols["FMAPPATHPOINT.OFFSETX"] != 0 or symbols["FMAPPATHPOINT.OFFSETY"] != 1:
            raise ValueError("Изменились поля смещений траектории")
        raw = bytearray()
        for _,instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != 2:
                raise ValueError("Изменилось число координат смещения")
            raw.extend(values)
        terminator = re.findall(r"End:\s+db\s+(#[0-9A-F]+)",text,re.I)
        if len(terminator) != 1 or number(terminator[0]) != 0x80:
            raise ValueError("Изменился отдельный байт завершения траектории")
        raw.append(0x80)
        if raw != sources[7][address-0xC000:address-0xC000+8*radius+1]:
            raise ValueError("Изменились исходные смещения траектории")
        variant_path_points += 4*radius
    for name,address in (("Default",0xCD03),("Current",0xCD33),("Stored",0xCD63),("Selected",0xCD93)):
        path = "Source/Map/Resources/Variant"+name+".asm"
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"Phase([0-7]):\s+FMapVariantPhase\s*\{([^}]+)\}",text)
        fields = ["Row"+str(row)+side for row in range(3) for side in ("Left","Right")]
        if [int(index) for index,_ in instances] != list(range(8)) or symbols["FMAPVARIANTPHASE"] != 6:
            raise ValueError("Изменились физические фазы варианта")
        if any(symbols["FMAPVARIANTPHASE."+field.upper()] != offset for offset,field in enumerate(fields)):
            raise ValueError("Изменились поля фазы варианта")
        raw = bytearray()
        for _,instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != 6:
                raise ValueError("Изменилось число байтов трёхстрочной фазы")
            raw.extend(values)
        if raw != sources[7][address-0xC000:address-0xC000+48]:
            raise ValueError("Изменились исходные байты спрайта варианта")
        variant_sprite_phases += 8

    # Проверка всех полей физического снимка дуги, включая исходные ненулевые значения.
    arc_workspace_records = 0
    arc_workspace_path = "Source/Map/Data/ArcWorkspace.asm"
    if any(item["path"] == arc_workspace_path for item in source_map):
        fields = ("AbsY", "AbsX", "QuadrantCode", "Radius", "OffsetY", "OffsetX", "RowY", "CenterX", "StartY",
                  "RasterStack", "SqrtTarget", "LeftMask", "RasterDown", "UpperRow", "LowerRow",
                  "MaxY", "ReferenceX", "HalfY", "HalfXLimit", "HalfXSquare")
        widths = [1]*9 + [2, 2, 1, 1, 2, 2] + [1]*5
        text = "\n".join(line.split(";", 1)[0] for line in (ROOT/arc_workspace_path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"State:\s+FMapArcWorkspace\s*\{([^}]+)\}", text)
        if len(instances) != 1:
            raise ValueError("Изменилось число физических экземпляров состояния дуги")
        values = [number(value) for value in instances[0].split(",")]
        if len(values) != len(fields):
            raise ValueError("Изменилось число полей состояния дуги")
        raw = bytearray()
        for field, width, value in zip(fields, widths, values):
            if symbols["FMAPARCWORKSPACE."+field.upper()] != len(raw):
                raise ValueError("Изменилось физическое смещение поля дуги " + field)
            raw.extend(value.to_bytes(width, "little"))
        if symbols["FMAPARCWORKSPACE"] != 24 or raw != sources[7][0x1FAB:0x1FC3]:
            raise ValueError("Изменились исходные 24 байта состояния дуги")
        arc_workspace_records = 1

    # Проверка физических точек, байтов режима и двух наборов масок рисователя отрезков.
    map_line_records = {}
    for path,structure,offset,length,widths,count in (
        ("Source/Map/Data/MapLinePoints.asm","FClipOutputPoint",0x1E2B,4,[1,1],2),
        ("Source/Map/Data/MapLineMode.asm","FMapLineMode",0x1E3C,2,[1,1],1),
        ("Source/Map/Data/MapLineMasks.asm","FMapLineMaskSet",0x1420,16,[1]*8,2)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(structure+r"\s*\{([^}]+)\}",text)
        raw = bytearray()
        for instance in instances:
            values = [number(value) for value in instance.split(",")]
            if len(values) != len(widths):
                raise ValueError("Изменилось число полей физического состояния отрезка")
            raw.extend(values)
        if len(instances) != count or symbols[structure.upper()] != sum(widths) or raw != sources[7][offset:offset+length]:
            raise ValueError("Изменились физические точки, режим или маски отрезка")
        map_line_records[structure] = count

    # Проверка текущей и предыдущей физических точек открытой цепочки.
    map_chain_point_records = 0
    for path,offset in (("Source/Map/Data/CurrentMapChainPoint.asm",0x1E0B),("Source/Map/Data/PreviousMapChainPoint.asm",0x1E1B)):
        if not any(item["path"] == path for item in source_map):
            continue
        text = "\n".join(line.split(";",1)[0] for line in (ROOT/path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"FProjectedPoint\s*\{([^}]+)\}",text)
        if len(instances) != 1:
            raise ValueError("Изменилось число рабочих точек цепочки")
        values = [number(value) for value in instances[0].split(",")]
        if len(values) != 3 or symbols['FPROJECTEDPOINT'] != 5:
            raise ValueError("Изменились физические поля рабочей точки цепочки")
        raw = values[0].to_bytes(2,'little')+values[1].to_bytes(2,'little')+bytes([values[2]])
        if raw != sources[7][offset:offset+5]:
            raise ValueError("Изменились исходные байты рабочей точки цепочки")
        map_chain_point_records += 1

    # Проверка исходного служебного поля и десяти смещений второго списка.
    stored_map_order_records = 0
    stored_map_order_path = "Source/Station/Data/StoredMapOrder.asm"
    if any(item["path"] == stored_map_order_path for item in source_map):
        text = "\n".join(line.split(";",1)[0] for line in (ROOT / stored_map_order_path).read_text(encoding="utf-8").splitlines())
        instances = re.findall(r"FStoredMapOrder\s*\{([^}]+)\}",text)
        raw = b"".join(bytes(number(value) for value in instance.split(",")) for instance in instances)
        if len(instances) != 1 or symbols["FSTOREDMAPORDER"] != 11 or raw != sources[4][0x3970:0x397B]:
            raise ValueError("Изменилось физическое состояние порядка второго списка")
        stored_map_order_records = 1

    # Проверка физических пятибайтовых записей двух списков карты и отдельных ограничителей.
    stored_map_point_records = 0
    stored_map_point_path = "Source/Station/Data/StoredMapPoints.asm"
    if any(item["path"] == stored_map_point_path for item in source_map):
        text = (ROOT / stored_map_point_path).read_text(encoding="utf-8")
        raw = bytearray()
        for line in text.splitlines():
            match = re.search(r"FStoredMapPoint\s*\{([^}]+)\}",line)
            if match:
                values = [number(value) for value in match[1].split(",")]
                if len(values) != 3:
                    raise ValueError("Изменено число полей сохранённой точки")
                raw.extend(values[0].to_bytes(2,"little")+values[1].to_bytes(2,"little")+bytes([values[2]]))
                stored_map_point_records += 1
            elif re.match(r"^EndByte:",line):
                raw.append(number(line.split("db",1)[1]))
        if stored_map_point_records != 20 or symbols["FSTOREDMAPPOINT"] != 5 or raw != sources[4][0x390A:0x3970]:
            raise ValueError("Изменились физические списки карты")

    # Проверка всех семи LF-потоков условий и выдачи миссионной награды.
    mission_text_bytes = 0
    mission_text_path = "Source/Station/Data/MissionTexts.asm"
    if any(item["path"] == mission_text_path for item in source_map):
        text = (ROOT / mission_text_path).read_text(encoding="utf-8")
        mission_text_records = re.findall(r"^\w+:\s+db\s+([^;\n]+)",text,re.M | re.I)
        raw = b"".join(bytes(number(value) for value in record.split(",")) for record in mission_text_records)
        if len(mission_text_records) != 7 or raw.count(10) != 7 or raw != sources[4][0x4B66:0x4C14]:
            raise ValueError("Изменились исходные строки условий миссии")
        mission_text_bytes = len(raw)

    # Проверка типизированных заголовков, потоков и секторных хвостов всех экранных блоков.
    screens = read_json("Screens.json")
    packed_final_byte_records = 0
    for screen in screens:
        path = ROOT/screen["path"]
        text = path.read_text(encoding="utf-8")
        text = "\n".join(line.split(";", 1)[0] for line in text.splitlines())
        header = re.search(r"FPackedHeader\s*\{([^}]+)\}",text)[1]
        values = [number(v) for v in header.split(",")]
        raw = b"".join(v.to_bytes(2,"little") for v in values)
        final_bytes = re.search(r"FPackedFinalBytes\s*\{([^}]+)\}",text)
        if final_bytes:
            final_words = [number(v) for v in final_bytes[1].split(",")]
            if len(final_words) != 3:
                raise ValueError("Сохранённый конец HR должен содержать три слова")
            raw += b"".join(v.to_bytes(2,"little") for v in final_words)
            packed_final_byte_records += 1
        for name in re.findall(r'incbin\s+"([^"]+)"',text,re.I):
            raw += (path.parent/name).read_bytes()
        offset = screen["offset"]
        if raw != sources[screen["slot"]][offset:offset+screen["allocated_size"]]:
            raise ValueError("Экранный ресурс отличается от оригинала")
    if packed_final_byte_records not in (0, len(screens)):
        raise ValueError("Типизация финальных байтов должна охватывать все HR-ресурсы")
    report = dict(method="text_and_resource_comparison_without_assembly", passed=True,
                  instruction_count=code_count, active_allocations=len(coverage),
                  covered_bytes=sum(len(c) for c in coverage.values()),
                  interface_records=len(records), script_token_records=len(tokens), texture_phase_records=len(phases), glyph_route_records=len(glyph_routes), packed_screens=len(screens),
                  pointer_records=pointer_counts, mouse_records=mouse_records, pointer_input_records=pointer_input_records, station_irq_records=station_irq_records, matrix_key_records=matrix_key_records, setting_records=setting_records, setting_text_bytes=setting_text_bytes, context_menu_bytes=context_menu_bytes, random_state_records=random_state_records, signature_input_records=signature_input_records, market_records=market_records, assignment_records=assignment_records, action_file_keys=action_file_keys, save_slot_file_keys=save_slot_file_keys, final_file_keys=final_file_keys, expression_stack_records=expression_stack_records, rank_threshold_records=rank_threshold_records, rank_text_bytes=rank_text_bytes, mission_offer_records=mission_offer_records, system_prefix_bytes=system_prefix_bytes, mission_message_bytes=mission_message_bytes, mission_text_bytes=mission_text_bytes, stored_map_point_records=stored_map_point_records, stored_map_order_records=stored_map_order_records, clip_work_records=clip_work_records, clip_output_size_bytes=clip_output_size_bytes, semantic_completeness_proved=False)
    report['map_line_records'] = map_line_records
    report['packed_final_byte_records'] = packed_final_byte_records
    report['map_chain_point_records'] = map_chain_point_records
    report['arc_workspace_records'] = arc_workspace_records
    report['marker_sprite_phase_records'] = marker_sprite_phase_records
    report['variant_path_points'] = variant_path_points
    report['variant_sprite_phases'] = variant_sprite_phases
    report['auxiliary_map_keys'] = auxiliary_map_keys
    report['auxiliary_map_code_bytes'] = auxiliary_map_code_bytes
    report['market_script_bytes'] = market_script_bytes
    report['market_script_labels'] = market_script_labels
    report['preview_description_bytes'] = preview_description_bytes
    report['preview_description_labels'] = preview_description_labels
    report['preview_price_bytes'] = preview_price_bytes
    report['preview_price_labels'] = preview_price_labels
    report['model_availability_records'] = model_availability_records
    report['preview_queue_records'] = preview_queue_records
    report['preview_square_bytes'] = preview_square_bytes
    report['key_abbreviation_records'] = 3
    report['help_line_cache_records'] = 1024
    report['preview_scene_records'] = preview_scene_records
    report['preview_model_group_records'] = preview_model_records
    report['preview_projected_vertices'] = preview_projected_vertices
    report['preview_pixel_masks'] = preview_pixel_masks
    report['music_effect_records'] = music_effect_records
    report['music_player_records'] = music_player_records
    report['music_composition_parts'] = music_composition_parts
    report['text_queue_records'] = text_queue_records
    report['marker_phase_records'] = marker_records
    report['buffer_point_records'] = buffer_point_records
    report['action_sine_records'] = action_sine_records
    report['word_random_records'] = word_random_records
    report['folded_random_records'] = folded_random_records
    report['signed_ratio_code_records'] = signed_ratio_code_records
    report['class_handler_records'] = class_handler_records
    report['state_handler_records'] = state_handler_records
    report['component_work_records'] = component_work_records
    report['wide_vector_records'] = wide_vector_records
    report['signed_work_vector_records'] = signed_work_vector_records
    report['visual_effect_records'] = visual_effect_records
    report['root_cache_records'] = root_cache_records
    report['square_table_records'] = square_records
    report['small_mask_records'] = small_mask_records
    report['body_projection_records'] = body_projection_records
    report['circle_work_records'] = circle_work_records
    report['three_row_glyph_records'] = three_row_glyph_records
    report['raster_return_records'] = raster_return_records
    report['object_glyph_records'] = object_glyph_records
    report['gauge_mask_records'] = gauge_mask_records
    report['preferred_byte_records'] = preferred_byte_records
    report['key_scan_records'] = key_scan_records
    report['missile_stock_records'] = missile_stock_records
    report['missile_target_records'] = missile_target_records
    report['type_delta_records'] = type_delta_records
    report['projection_square_values'] = projection_square_values
    report['action_ay_stream_records'] = ay_stream_records
    report['object_data_pointer_records'] = len(OBJECT_POINTER_TABLE[-1])
    report['action_object_records'] = object_records
    report['glyph_input_records'] = glyph_input_records
    report['parameter_rule_records'] = parameter_rule_records
    report['candidate_list_records'] = len(CANDIDATE_LIST_TABLE[-1])
    report['render_basis_word_records'] = len(RENDER_BASIS_TABLE[-1])
    report['equipment_code_records'] = sum(len(table[-1]) for table in EQUIPMENT_TABLES)
    (ROOT/"Tools/Disasm/Reports/SourceVerification.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
