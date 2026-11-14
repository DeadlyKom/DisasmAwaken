"""Сопоставление архивных PSTARS/ABONS и текущего цикла дополнительных маркеров."""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckStationFlightCycle import ROOT, DISK, payload


def current_marker_cancellation():
    """Исходный цикл и исходные ключи, чётное число совпавших XOR-маркеров и контроль нечётности."""
    from CheckMapScene import marker
    from CheckRowHighlight import make_context
    from CheckMusic import Simulator,get_registers,PC,SP
    _,source,banks=make_context()
    memory=bytearray(65536)
    memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2])
    memory[0xC000:0xC000+len(source)]=source
    sim=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
        'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A},None,False)
    memory[0x7FFE:0x8000]=bytes((255,63));sim.registers[:]=initial
    sim.registers[4]=sim.registers[5]=0;sim.run(start=0xC49B,stop=0x3FFF)
    original_keys=bytes(memory[0x997B:0x99A3]);original_codes=bytes(memory[0x99A3:0x99AF])
    assert original_keys==bytes.fromhex('394B0600')+bytes(36)
    assert original_codes==bytes([0,0]+[1]*8+[0,0x81])
    profiles=[]
    for name,value in (('physical',1),('positive_two',2),('positive_127',127)):
        profiles.append((name,bytes([0,0]+[value]*8+[0,0x81]),8))
    profiles.append(('one_disabled',bytes([0,0,0]+[1]*7+[0,0x81]),7))
    profiles.append(('early_end',bytes([0,0,0x80]+[1]*7+[0,0x81]),0))
    cases=visible_odd=cancelled=0
    for width,height in ((128,96),(208,112)):
        sim.registers[:]=initial;sim.registers[6],sim.registers[7]=height-1,width-1
        sim.registers[4]=sim.registers[5]=0;sim.run(start=0xD0C3,stop=0x3FFF)
        prepared=memory.copy()
        for phase in range(8):
            for dy in (0,1,height-8,height-7,0x100):
                ox,oy=(-3-phase)&65535,(-3-dy)&65535
                for fill in (0,1):
                    baseline=bytes(((index*73+19)&255) if fill else 0 for index in range(6912))
                    for name,codes,calls in profiles:
                        memory[:]=prepared;memory[0x4000:0x5B00]=baseline
                        memory[0x6300:0x6306]=bytes((ox&255,oy&255,ox>>8,oy>>8,width,height))
                        memory[0x99A3:0x99AF]=codes
                        expected=bytearray(baseline);accepted=False
                        # Независимая композиция одинаковых маркеров, штатные ключи не подменяются.
                        for _ in range(calls):accepted=marker(expected,source,0xCEC3,0,0,ox,oy,width,height)
                        snapshot=bytes(memory[0x997B:0x99AF]);sim.registers[:]=initial
                        sim.registers[PC]=0xC0F9;observed_calls=0
                        for _ in range(20000):
                            if sim.registers[PC]==0xC124:break
                            if sim.registers[PC]==0xC231:
                                assert sim.registers[2:6]==[0,0,0,0]
                                observed_calls+=1
                            sim.run()
                        else:raise AssertionError('Цикл дополнительных маркеров не завершился')
                        context=name,width,height,phase,dy,fill
                        assert observed_calls==calls and sim.registers[SP]==0x7FFE,context
                        assert memory[0x4000:0x5B00]==expected,context
                        assert bytes(memory[0x997B:0x99AF])==snapshot,context
                        if calls in (0,8):
                            assert expected==baseline,context
                            cancelled+=calls==8
                        elif accepted:
                            assert expected!=baseline,context
                            visible_odd+=1
                        cases+=1
    assert cases==800 and visible_odd and cancelled
    return dict(passed=True,cases=cases,profiles=[name for name,_,_ in profiles],
        phase_count=8,viewports=[[128,96],[208,112]],bitmap_and_attributes_compared=True,
        original_keys_preserved=True,physical_positive_marker_calls=8,
        eight_identical_XOR_markers_cancel=True,visible_odd_marker_cases=visible_odd,
        even_marker_cases=cancelled,fragment_start=0xC0F9,fragment_stop=0xC124,
        original_marker_called_without_stubs=True,complete_scene_executed=False,
        current_unknown_code_roles_proved=False,irq_executed=False,native_execution=False)


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        disk = archive.read('awk6.trd')
        origin, old_map, _ = read_entry(disk, b'KARTA   C')
        _, declarations, _ = read_entry(disk, b'DATA_M  a')
        _, constants, _ = read_entry(disk, b'EQUS    a')
        _, map_source, _ = read_entry(disk, b'KARTA   a')
        _, older_declarations, _ = read_entry(archive.read('awk1.trd'), b'3DTABS  a')
    # Проверяем ёмкость и объявления обеих параллельных архивных таблиц.
    assert origin == 0xC000 and len(old_map) == len(payload(7)) == 11776
    assert b'PKOL\x06\x88\x05f\x06\x8250\r' in constants
    rows = declarations.split(b'\r')
    point = rows.index(b'PSTARS')
    assert rows[point + 1:point + 3] == [b'\x06\x8c\x05h\x06\x83#4B39,#0006',
                                       b'\x06\x8c\x05i\x06\x83PKOL*4-4']
    code = rows.index(b'ABONS')
    assert rows[code + 1:code + 5] == [b'\x06\x8c\x05g\x06\x832', b'\x06\x8c\x05g\x06\x832',
        b'\x06\x8c\x05i\x06\x83PKOL-2,1', b'\x06\x8c\x05g\x06\x830;END']
    assert 'ЗВЕЗДЫ ГДЕ ЖИВУТ ПЕРСОНАЖИ'.encode('cp866') in declarations
    assert 'СОСТОЯНИЕ 0-НЕДОСТУПЕН 1-ДОСТУПЕН'.encode('cp866') in older_declarations
    assert 'СОСТОЯНИЕ 1-НЕДОСТУПЕН'.encode('cp866') in declarations
    assert '2-ДОСТУПЕН'.encode('cp866') in declarations
    assert b'\x03\x8d,PSTARS\r' in map_source and b'\x03\x8c,ABONS;' in map_source

    # Сравниваем все 43 байта цикла, разрешены только две изменившиеся базы таблиц.
    old_loop, current_loop = old_map[0xF9:0x124], payload(7)[0xF9:0x124]
    assert old_loop[:7] == bytes.fromhex('DD 21 79 99 21 41 9A')
    assert current_loop[:7] == bytes.fromhex('DD 21 7B 99 21 A3 99')
    assert len(current_loop) == len(old_loop) == 43 and old_loop[7:] == current_loop[7:]
    assert current_loop[7:] == bytes.fromhex(
        '7E 23 A7 28 17 FA 24 C1 E5 DD 5E 00 DD 56 01 DD 4E 02 DD 46 03 '
        '21 C3 CE CD 31 C2 E1 01 04 00 DD 09 C3 00 C1')
    old_points, old_codes = int.from_bytes(old_loop[2:4], 'little'), int.from_bytes(old_loop[5:7], 'little')
    current_points, current_codes = int.from_bytes(current_loop[2:4], 'little'), int.from_bytes(current_loop[5:7], 'little')
    assert old_codes - old_points == 50 * 4
    assert current_codes - current_points == 10 * 4
    # Проверяем нынешние ключи и коды по исходному STATIONF, не по оформленным ASM.
    station = payload(4)
    assert station[0x397B:0x39A3] == bytes.fromhex('39 4B 06 00') + bytes(36)
    assert station[0x39A3:0x39AE] == bytes([0, 0] + [1] * 8 + [0])
    assert station[0x39AE] == 0x81
    report = dict(passed=True, method='archived_sources_and_full_original_loop_comparison',
        archive_sha256=digest, original_disk_sha256=sha256(DISK).hexdigest(),
        archived_map='awk6.trd:KARTA.C', loop_start=0xC0F9, loop_bytes=43,
        unchanged_loop_body_bytes=36, archived_loop_hex=old_loop.hex(), current_loop_hex=current_loop.hex(),
        archived_points=old_points, archived_codes=old_codes, archived_capacity=50,
        current_points=current_points, current_codes=current_codes, current_capacity=10,
        archived_contact_code_versions=[[0, 1], [1, 2]],
        current_code_hex=station[0x39A3:0x39AE].hex(), current_following_byte=0x81,
        current_marker_cancellation=current_marker_cancellation(),
        current_contact_gameplay_proved=False, current_unknown_code_roles_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/MapAuxiliaryArchiveLayoutVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Сверены 43 байта цикла PSTARS/ABONS, изменились только базы, ёмкость сокращена с 50 до 10 ключей.')


if __name__ == '__main__':
    main()
