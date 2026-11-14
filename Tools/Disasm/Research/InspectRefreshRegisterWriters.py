"""Явные записи R в разобранном коде и условное исполнение фрагмента TR-DOS.

Документация: ../../../Docs/ActionNoiseExit.md#источники-старшего-бита-r
"""
from hashlib import sha256
import json
from pathlib import Path

from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from skoolkit import ROM48, ROM128
from skoolkit.simutils import R


def positions(data, needle):
    return [index for index in range(len(data) - len(needle) + 1)
            if data[index:index + len(needle)] == needle]


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    flow = json.loads((reports / 'ControlFlow.json').read_bytes())
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entries = {entry['slot']: entry for entry in manifest['entries']}
    writers, checked = [], 0
    # Сверка каждого зарегистрированного опкода с оригинальным физическим образом.
    for region in flow:
        for row in region['instructions']:
            raw = bytes.fromhex(row['hex'])
            offset = entries[row['slot']]['offset'] + row['offset']
            assert disk[offset:offset + len(raw)] == raw
            if row['operation'] == 'LD R,A':
                writers.append(dict(region=region['name'], address=row['address'],
                                    slot=row['slot'], file_offset=row['offset']))
            checked += 1
    assert not writers and checked == 50957
    roms = []
    # Поиск во всех байтах выбранных ROM, совпадение в общем случае ещё не является точкой исполнения.
    for path in (Path(ROM48), *(Path(value) for value in ROM128),
                 ROOT / 'Tools/Disasm/Research/Runtime/Unreal/rom/trdos504t.rom'):
        data = path.read_bytes()
        sites = positions(data, bytes.fromhex('ED4F'))
        is_dos = path.name == 'trdos504t.rom'
        assert len(data) == 16384 and sites == ([0x2EBF] if is_dos else [])
        roms.append(dict(path=path.resolve().relative_to(ROOT).as_posix(),
                         sha256=sha256(data).hexdigest(), bytes=len(data),
                         raw_ED4F_offsets=sites))
        if is_dos:
            dos = data
    assert dos[0x2EBE:0x2EC4] == bytes.fromhex('F1ED4FF1ED47')
    memory = list(dos) + [0] * 49152
    cpu = Simulator(memory)
    cases = 0
    # Проверка восстановления R из явно подготовленного слова AF, полный вызов TR-DOS не подменяется этим входом.
    for value in range(256):
        memory[0xBFF0:0xBFF2] = [0x37, value]
        before = memory.copy()
        cpu.registers[:] = get_registers(dict(SP=0xBFF0, R=0x5A, AF=0xA569), None, False)
        cpu.run(start=0x2EBE, stop=0x2EC1)
        assert cpu.registers[PC] == 0x2EC1 and cpu.registers[SP] == 0xBFF2
        assert cpu.registers[:2] == [value, 0x37] and cpu.registers[R] == value
        assert memory == before
        cases += 1
    report = dict(passed=True, original_disk_sha256=manifest['sha256'],
        registered_regions_checked=len(flow), original_instructions_checked=checked,
        registered_LD_R_A_writers=writers, selected_roms=roms,
        trdos_fragment=dict(start=0x2EBE, stop=0x2EC1,
            original_bytes_hex='F1ED4F', cases=cases, all_256_R_values_restored=True,
            stack_AF_word_explicitly_prepared=True, whole_dos_entry_executed=False,
            native_game_reaches_this_fragment_proved=False),
        raw_disk_ED4F_offsets=positions(disk, bytes.fromhex('ED4F')),
        raw_disk_pair_is_not_instruction_proof=True,
        generated_modified_or_other_entry_code_excluded=False,
        native_refresh_bit7_reachability_proved=False,
        native_execution=False, assembly_executed=False)
    (reports / 'RefreshRegisterWritersInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('50957 original instructions, no registered LD R,A, 256 TR-DOS fragment cases passed')


if __name__ == '__main__':
    main()
