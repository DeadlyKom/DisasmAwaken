"""STATCOMPOS, SSX/SSY/SSZ и третий знак текущего компаса."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


def main():
    path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(path) as archive:
        disk = archive.read('awk1.trd')
        _, source, _ = read_entry(disk, b'SLOWPRO a')
        _, labels, _ = read_entry(disk, b'LABELS  a')
        _, generator, _ = read_entry(disk, b'OBJGENERa')
        _, declarations, _ = read_entry(disk, b'3DTABS  a')
        datas_origin, datas, _ = read_entry(disk, b'DATAS   C')
        sp_origin, sp, _ = read_entry(archive.read('awk5.trd'), b'SP      C')
    rows = source.split(b'\r')
    start = rows.index(b'STATCOMPOS')
    caption = 'НАСТРОЙКА КООРДИНАТ КОМПАСА НА СТАНЦИЮ'.encode('cp866')
    assert rows[start - 1] == caption
    source_block = rows[start:start + 33]
    for symbol in (b'NOSTAT', b'SSX+1', b'SSY+1', b'SSZ+1', b'TTX', b'TTY', b'TTZ'):
        assert any(b'(' + symbol + b')' in row for row in source_block)
    assert any(row.startswith(b'SSZ:') and row.endswith(b'\x05h-LAUNGH-1')
               for row in declarations.split(b'\r'))
    generator_rows = generator.split(b'\r')
    station_start = generator_rows.index(b'STATGEN_')
    assert generator_rows[station_start - 1] == 'ГЕНЕРАЦИЯ СТАНЦИИ'.encode('cp866')
    for symbol in (b'SSX', b'SSY', b'SSZ', b'NOSTAT'):
        assert any(b'(' + symbol + b')' in row for row in generator_rows[station_start:station_start + 15])
    addresses = {}
    for row in labels.split(b'\r'):
        match = re.fullmatch(rb'(SSX|SSY|SSZ|NOSTAT|TTX|TTY|TTZ)\x06.\x04f(\d+)', row)
        if match:
            addresses[match[1].decode()] = int(match[2])
    assert addresses == dict(SSX=0x9B78, SSY=0x9B7B, SSZ=0x9B7E, NOSTAT=0x9B82,
                              TTX=0x9B85, TTY=0x9B84, TTZ=0x9B86)
    flat = flat_action()
    current = bytes(flat[0x6C8F:0x6CD6])
    assert len(current) == 71
    prefix = bytes.fromhex('3a829bb7c02a799b')
    assert current.startswith(prefix) and sp.count(prefix) == 1
    offset = sp.index(prefix)
    old = sp[offset:offset + len(current)]
    replacements = (
        (9, 0xAFD3, 0xAF48, 'Input0'), (15, 0xAFE1, 0xAF56, 'Input1'),
        (21, 0xAFF4, 0xAF69, 'Input2'), (25, 0x6BE1, 0x6CB2, 'SavedCpuSP'),
        (29, 0x6BE0, 0x6CB1, 'RestoreThirdGlyphStack'),
        (32, 0xAFCE, 0xAF43, 'ComputePatchedVector'),
        (39, 0xD9B8, 0xD9B6, 'Output0'), (49, 0x9B84, 0x9B85, 'Third.X'),
        (52, 0xD7C6, 0xD7C4, 'Output1'), (62, 0x9B83, 0x9B84, 'Third.Y'),
        (65, 0xD7A5, 0xD7A3, 'Output2.High'), (68, 0x9B85, 0x9B86, 'Third.SignSource'))
    normalized = bytearray(old)
    for position, before, after, _ in replacements:
        assert int.from_bytes(old[position:position + 2], 'little') == before
        assert int.from_bytes(current[position:position + 2], 'little') == after
        normalized[position:position + 2] = after.to_bytes(2, 'little')
    assert normalized == current
    archived_execution = int.from_bytes(old[29:31], 'little') - 34
    assert archived_execution == 0x6BBE and old[34] == 0x31
    assert int.from_bytes(old[25:27], 'little') == archived_execution + 35
    assert sp_origin + offset - archived_execution == 0x23D
    vector = datas[0x9B78 - datas_origin:0x9B81 - datas_origin]
    assert vector == bytes(flat[0x9B78:0x9B81]) == bytes.fromhex('000000000000fff7ff')
    reports = ROOT / 'Tools/Disasm/Reports'
    for name in ('ActionThirdGlyphVectorVerification', 'ActionThirdGlyphPublishVerification',
                 'ControlsGlyphIndicatorsVerification'):
        assert json.loads((reports / (name + '.json')).read_bytes())['passed']
    report = dict(passed=True, archive_sha256=digest,
                  caption_cp866_hex=caption.hex(), source='awk1.trd:SLOWPRO.a:STATCOMPOS',
                  station_generator='awk1.trd:OBJGENER.a:STATGEN_', authored_addresses=addresses,
                  matched_station_vector_bytes=len(vector), station_vector_hex=vector.hex(),
                  archived_sp_file_offset=offset, archived_sp_physical_address=sp_origin + offset,
                  archived_execution_address=archived_execution, current_execution_address=0x6C8F,
                  matched_code_bytes=len(current), original_archived_code_hex=old.hex(),
                  original_current_code_hex=current.hex(), operand_replacements=replacements,
                  old_sp_destination_layout_differs=True, identical_after_explicit_operand_changes=True,
                  third_indicator_role='station_compass', exact_spatial_units_proved=False,
                  full_native_compass_behavior_proved=False, assembly_executed=False, native_execution=False)
    (reports / 'ActionStationCompassArchiveVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Компас станции: совпали 71 байт после 12 замен операндов и 9 байтов вектора.')


if __name__ == '__main__':
    main()
