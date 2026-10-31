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
    """Чтение простых DB/DW/DS полей из фактических объявлений структур."""
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
                raise ValueError("Не поддержано поле структуры: " + code)
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
        operation = re.sub(r"\bF[A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)?\b",
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
    for screen in screens:
        path = ROOT/screen["path"]
        text = path.read_text(encoding="utf-8")
        text = "\n".join(line.split(";", 1)[0] for line in text.splitlines())
        header = re.search(r"FPackedHeader\s*\{([^}]+)\}",text)[1]
        values = [number(v) for v in header.split(",")]
        raw = b"".join(v.to_bytes(2,"little") for v in values)
        for name in re.findall(r'incbin\s+"([^"]+)"',text,re.I):
            raw += (path.parent/name).read_bytes()
        offset = screen["offset"]
        if raw != sources[screen["slot"]][offset:offset+screen["allocated_size"]]:
            raise ValueError("Экранный ресурс отличается от оригинала")
    report = dict(method="text_and_resource_comparison_without_assembly", passed=True,
                  instruction_count=code_count, active_allocations=len(coverage),
                  covered_bytes=sum(len(c) for c in coverage.values()),
                  interface_records=len(records), script_token_records=len(tokens), texture_phase_records=len(phases), glyph_route_records=len(glyph_routes), packed_screens=len(screens),
                  pointer_records=pointer_counts, mouse_records=mouse_records, pointer_input_records=pointer_input_records, station_irq_records=station_irq_records, matrix_key_records=matrix_key_records, setting_records=setting_records, setting_text_bytes=setting_text_bytes, context_menu_bytes=context_menu_bytes, random_state_records=random_state_records, signature_input_records=signature_input_records, market_records=market_records, assignment_records=assignment_records, action_file_keys=action_file_keys, final_file_keys=final_file_keys, expression_stack_records=expression_stack_records, rank_threshold_records=rank_threshold_records, rank_text_bytes=rank_text_bytes, mission_offer_records=mission_offer_records, system_prefix_bytes=system_prefix_bytes, mission_message_bytes=mission_message_bytes, mission_text_bytes=mission_text_bytes, stored_map_point_records=stored_map_point_records, stored_map_order_records=stored_map_order_records, clip_work_records=clip_work_records, clip_output_size_bytes=clip_output_size_bytes, semantic_completeness_proved=False)
    report['map_line_records'] = map_line_records
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
    report['preview_scene_records'] = preview_scene_records
    report['preview_model_group_records'] = preview_model_records
    report['preview_projected_vertices'] = preview_projected_vertices
    report['preview_pixel_masks'] = preview_pixel_masks
    (ROOT/"Tools/Disasm/Reports/SourceVerification.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
