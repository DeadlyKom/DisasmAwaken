"""Исходные указатели, одиночные маски, очистка и двенадцать форм объектного прохода."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records
from ControlsThreeRowGlyphs import FIELDS as GLYPH_FIELDS

SHAPES = ('BarI','BottomT','OpenRight','Solid','LowerLeft','HorzBars',
          'RightBar','Hollow','VerticalBars','Slash','Cross','Plus')
ARCHIVED_POINTER_NAMES = ('MPIRAT','MTRADER','MARMY','MPOLICE','MHUNTER','MPIRAT',
                         'MUFO','MUFO','MOTSHEL','MMIKR',*('MTRADER',)*6,
                         'MUNKNOWN','MROKET','MSTATION','MCARGO')
POINTER_FIELDS = (('Target',2,'адрес восьми фаз значка класса, порядок MOTAB и определения T_* подтверждены'),)
PIXEL_FIELDS = (('Mask',1,'одиночный бит X внутри экранного байта'),)
CLEAR_FIELDS = (('LeftMask',1,'сохраняемые биты левой части строки'),
                ('RightMask',1,'сохраняемые биты правой части строки')) + tuple(
    ('Unknown'+format(i,'02d'),1,'исходный нулевой байт, этот потребитель его не читает') for i in range(2,6))
TABLES = (
    ('ControlsObjectGlyphPointers','Source/Controls/Data/ObjectGlyphPointers.asm',0xB7F,0xBA7,
     'FObjectGlyphPointer',POINTER_FIELDS,tuple('Kind'+format(i,'02X') for i in range(20))),
    ('ControlsObjectPixelMasks','Source/Controls/Data/ObjectPixelMasks.asm',0xBA7,0xBAF,
     'FObjectPixelMask',PIXEL_FIELDS,tuple('Phase'+format(i,'02X') for i in range(8))),
    ('ControlsObjectClearMasks','Source/Controls/Data/ObjectClearMasks.asm',0xBAF,0xBDF,
     'FObjectGlyphClearPhase',CLEAR_FIELDS,tuple('Phase'+format(i,'02X') for i in range(8))),
    ('ControlsObjectGlyphs','Source/Controls/Data/ObjectGlyphs.asm',0xBDF,0xE1F,
     'FThreeRowGlyphPhase',GLYPH_FIELDS,tuple(name+format(i,'02X') for name in SHAPES for i in range(8))))


def render(source, table):
    text, symbols = render_records(source,table,0xDADE)
    if table[0] == 'ControlsObjectGlyphPointers':
        for index,name in enumerate(ARCHIVED_POINTER_NAMES):
            old='исходная физическая запись Kind'+format(index,'02X')
            text=text.replace(old,old+', авторский '+name)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[координаты и значки объектов](../../../Docs/ControlsObjectProjection.md)'), symbols


def parse(text,table):
    module,path,start,end,structure,fields,names=table
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+module and clean.pop(0)=='assert $ == #'+format(0xDADE+start,'04X')
    for name in names:
        assert clean.pop(0)==(name+':').ljust(16)+structure+' {'
        for index,(_,width,_) in enumerate(fields):
            assert re.fullmatch(r'#[0-9A-F]{'+str(width*2)+'}'+(',' if index+1<len(fields) else ''),clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #'+format(0xDADE+end,'04X'),'endmodule']
    return parse_records(text,table,0xDADE)


def verify_archived_roles():
    """Сверка MOTAB, MPALKA, MMASK и всех форм без публикации исходников."""
    from hashlib import sha256
    import json
    from zipfile import ZipFile
    from CheckControlsArchivedHyperEffect import read_entry
    from CheckIntro import ROOT

    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        disk_member = archive.read('awk1.trd')
        _, source, _ = read_entry(disk_member, b'PANEL   a')
        _, definitions, _ = read_entry(disk_member, b'EQUS    a')
        _, model_notes, _ = read_entry(disk_member, b'3DTABS  a')
    lines = source.split(b'\r')
    shape_labels = ('MCARGO', 'MROKET', 'MSTATION', 'MTRADER', 'MARMY', 'MMIKR',
                    'MOTSHEL', 'MHUNTER', 'MUFO', 'MUNKNOWN', 'MPIRAT', 'MPOLICE')
    # Чтение токенизированных байтовых объявлений, выражения и неизвестные команды не исполняются.
    def read_bytes(label, count):
        start = lines.index(label.encode('ascii'))
        data = bytearray()
        for line in lines[start + 1:start + 1 + count]:
            match = re.fullmatch(rb'\x06[\x80-\x8f]\x05g\x06\x83([%#0-9A-F,]+)', line)
            assert match, (label, line)
            for literal in match[1].split(b','):
                value = int(literal[1:], 2) if literal.startswith(b'%') else (
                    int(literal[1:], 16) if literal.startswith(b'#') else int(literal))
                assert 0 <= value <= 255
                data.append(value)
        return bytes(data)

    begin, end = lines.index(b'MOTAB'), lines.index(b'MPALKA')
    pointers = []
    for line in lines[begin + 1:end]:
        match = re.fullmatch(rb'\x06[\x80-\x8f]\x05h\x06\x83(M[A-Z]+)', line)
        if match:
            pointers.append(match[1].decode('ascii'))
        else:
            assert line == b'\x06\x8c\x05\x9f 6:\x05hMTRADER:\x05\xa0'
            pointers.extend(['MTRADER'] * 6)
    assert len(pointers) == 20
    assert pointers == ['MPIRAT', 'MTRADER', 'MARMY', 'MPOLICE', 'MHUNTER', 'MPIRAT',
                        'MUFO', 'MUFO', 'MOTSHEL', 'MMIKR'] + ['MTRADER'] * 6 + [
                        'MUNKNOWN', 'MROKET', 'MSTATION', 'MCARGO']
    assert tuple(pointers) == ARCHIVED_POINTER_NAMES
    # Сверка каждого указателя с текущим адресом физической формы и всех 632 растровых байтов.
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    _, control, _ = read_entry(disk, b'CONTROL C')
    addresses = {label: 0xE6BD + index * 48 for index, label in enumerate(shape_labels)}
    pointer_bytes = b''.join(addresses[label].to_bytes(2, 'little') for label in pointers)
    pixel_masks, clear_masks = read_bytes('MPALKA', 8), read_bytes('MMASK', 8)
    glyphs = b''.join(read_bytes(label, 24) for label in shape_labels)
    expected = pointer_bytes + pixel_masks + clear_masks + glyphs
    assert len(expected) == 672 and expected == control[0xB7F:0xE1F]
    assert len(clear_masks) == 48 and all(clear_masks[i + 2:i + 6] == bytes(4) for i in range(0, 48, 6))
    roles = [dict(class_code=index, archived_label=label, current_address=addresses[label],
                  current_shape=SHAPES[shape_labels.index(label)]) for index, label in enumerate(pointers)]
    # Проверка числовых определений типов, имя MUNKNOWN само по себе не определяет смысл класса.
    type_definitions = {}
    for line in definitions.split(b'\r'):
        match = re.fullmatch(rb'(T_[A-Z0-9]+)\x06[\x80-\x8f]\x05f\x06\x82#([0-9A-F]+)\xfe(.+)', line)
        if match:
            type_definitions[match[1].decode('ascii')] = dict(value=int(match[2], 16),
                comment=match[3].decode('cp866'), raw_hex=line.hex())
    expected_types = dict(T_PIRAT=0, T_TRADER=1, T_MILITARY=2, T_POLICE=3, T_LEGIONER=4,
        T_PIRAT2=5, T_UFO=6, T_UFO2=7, T_HERMIT=8, T_MIKR=9, T_CHIP=16,
        T_ROKET=17, T_STATION=18, T_CARGO=19, T_TRASH=20, T_TARGET=22)
    assert {name:row['value'] for name,row in type_definitions.items()} == expected_types
    assert type_definitions['T_MIKR']['comment'] == 'МИКРО КОРАБЛЬ'
    assert type_definitions['T_CHIP']['comment'] == 'ОСКОЛОК'
    assert 'МИКРО КОРАБЛИКИ\rВЫЛЕТАЮТ ИЗ ДРУГИХ\rIMIK1:'.encode('cp866') in model_notes
    assert roles[9]['archived_label']=='MMIKR' and roles[16]['archived_label']=='MUNKNOWN'
    for role in roles:
        role['type_constants'] = [name for name,row in type_definitions.items() if row['value']==role['class_code']]
    # Связь с текущим создателем, инструкция проверяется в зарегистрированном коде ACTION.
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    action_flow = next(region['instructions'] for region in flow if region['name']=='Action')
    micro_writes = [row for row in action_flow if row['operation']=='LD (IY+#12),#09']
    assert len(micro_writes)==1 and 0xE86B<=micro_writes[0]['address']<0xE91E
    _, action, _ = read_entry(disk, b'ACTION  C')
    writer = micro_writes[0]
    assert writer['slot']==17 and bytes.fromhex(writer['hex'])==bytes.fromhex('FD 36 12 09')
    assert action[writer['offset']:writer['offset']+4]==bytes.fromhex(writer['hex'])
    # Связь ACTN с нынешним LinkFlags и конкретными писателями ракетного состояния.
    record_offsets = {}
    for line in definitions.split(b'\r'):
        match = re.fullmatch(rb'(SUBJ|ACTN|RAND|MSPD|RSPD|LZS|TYPE)\x06[\x80-\x8f]\x05f\x06\x82(\d+)', line)
        if match:
            record_offsets[match[1].decode('ascii')] = int(match[2])
    assert record_offsets == dict(SUBJ=11, ACTN=12, RAND=13, MSPD=15, RSPD=16, LZS=17, TYPE=18)
    definition_rows = definitions.split(b'\r')
    actn = next(i for i,line in enumerate(definition_rows) if line.startswith(b'ACTN\x06'))
    flag_notes = definition_rows[actn+1:actn+4]
    assert flag_notes[:2] == [b'\xfeBITS:', b'\xfe0-ATACK YOU,1-ROKET ATACK,2-ROKET KILLED YOU']
    current_code = {row['address']:row for row in action_flow}
    expected_writers = {0x6127:('LD (IY+#12),#11','fd361211'),
        0x613B:('SET 1,(HL)','cbce'), 0xF585:('SET 1,(IY+#0C)','fdcb0cce'),
        0xF62C:('SET 2,(IY+#0C)','fdcb0cd6')}
    rocket_writers = []
    for address,(operation,code_hex) in expected_writers.items():
        row=current_code[address]
        assert row['operation']==operation and row['hex']==code_hex
        assert action[row['offset']:row['offset']+len(bytes.fromhex(code_hex))]==bytes.fromhex(code_hex)
        rocket_writers.append(dict(address=address,operation=operation,hex=code_hex))
    report = dict(passed=True, archive_sha256=digest, original_disk_sha256=sha256(disk).hexdigest(),
        source='awk1.trd:PANEL.a', matched_bytes=672, matched_pointer_bytes=40,
        pixel_mask_bytes=8, clear_mask_bytes=48, glyph_bytes=576,
        archived_repeat_six_traders_expanded=True, roles=roles,
        clear_phase_declared_bytes=6, clear_phase_zero_tail_bytes=4,
        zero_tail_global_unusedness_proved=False,
        type_definitions=type_definitions, micro_ship_class_code=9, chip_class_code=16,
        current_micro_ship_class_writer=micro_writes[0]['address'],
        current_micro_ship_write_hex=writer['hex'],
        archived_record_offsets=record_offsets,archived_actn_notes_hex=[line.hex() for line in flag_notes],
        current_rocket_class_and_flag_writers=rocket_writers,
        trader_icon_only_alias_codes=list(range(10,16)),
        unresolved_archived_names=[],
        shared_icon_does_not_prove_equal_gameplay_classes=True,
        full_class_behavior_proved=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ArchivedObjectGlyphRolesVerification.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report
