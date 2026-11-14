"""Архивный PMLPI и поле 01 текущего набора, без переноса старого поведения в игру."""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckActionParameterActivation import ROOT, flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from skoolkit.simutils import A, F


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        source_disk, compiled_disk = archive.read('awk1.trd'), archive.read('awk5.trd')
    _, declarations, _ = read_entry(source_disk, b'3DTABS  a')
    _, body, _ = read_entry(source_disk, b'BODY    a')
    _, coefficients, _ = read_entry(source_disk, b'SETHJRETa')
    _, compiled, _ = read_entry(compiled_disk, b'SP      C')
    roles = declarations.split(b'\r')
    first = roles.index('МОЩНОСТЬ ЛАЗЕРА ИГРОКА'.encode('cp866'))
    assert roles[first + 1] == 'МОЩНОСТЬ ЛАЗЕРА ПРОТИВНИКА ПО ИГРОКУ'.encode('cp866')
    assert b'PLANDICTAT:' in declarations and b'\x83\x03\x8c,PLANDICTAT\r' in body
    assert b'\rPMLPI\x06\x87\x05\x27\x06\x821\r' in body
    assert b'\x83(PMLPI+1),\x05~\r' in body
    assert b'LEVLTAB\r' in coefficients and b'\x8320,1,1\r\x06\x8c\x05g\x06\x833,2,8\r' in coefficients
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    control = next(entry for entry in manifest['entries'] if entry['slot'] == 23)
    control_data = (ROOT / (control['path'] + '.bin')).read_bytes()
    offset = 0xDF64 - control['parameter']
    assert control_data[offset:offset + 9] == bytes.fromhex('14 01 01 03 02 08 17 02 08')
    old_base = [0] * 65536
    old_base[0x6000:0x6000 + len(compiled)] = compiled
    assert bytes(old_base[0xAD2D:0xAD3F]) == bytes.fromhex('21 A2 9B 7E 32 85 F7 23 7E 32 F5 A9 23 7E 32 81 F7 23')
    assert bytes(old_base[0xA9F1:0xA9F9]) == bytes.fromhex('3A 94 A8 D6 01 32 94 A8')
    current_base = flat_action()
    old, current = Memory(old_base), Memory(current_base)
    historical_cpu, current_cpu = Simulator(old), Simulator(current)
    initial = get_registers(dict(SP=0xBFFE, AF=0xA55A, HL=0x1357, DE=0x2468,
                                BC=0x369C, IX=0xABCD, IY=0x5C3A), None, False)
    baseline = None
    cases = 0
    for power in range(256):
        for memory, saved, address in ((old, old_base, 0x9BA2), (current, current_base, 0x9BA4)):
            memory.recording = False
            memory[:] = saved
            memory[address:address + 15] = [0] * 15
            memory[address + 1] = power
            memory[0xBFFE:0xC000] = [255, 63]
            memory.writes = []
            memory.recording = True
        for cpu, entry, stop in ((historical_cpu, 0xAD2D, 0xAD7D), (current_cpu, 0xAC5D, 0x3FFF)):
            cpu.registers[:] = initial
            cpu.registers[PC] = entry
            for _ in range(100):
                if cpu.registers[PC] == stop:
                    break
                cpu.run()
            else:
                raise AssertionError(('Не завершён установщик', entry, power))
        old.recording = current.recording = False
        assert len(old.writes) == 16 and (0xA9F5, power) in old.writes
        assert len(current.writes) == 15 and current[0x9BA5] == power
        final = list(current)
        final[0x9BA5] = 0
        result = (list(current_cpu.registers), final, list(current.writes))
        if baseline is None:
            baseline = result
        assert result == baseline, power
        for shield in range(256):
            old[0xA894] = shield
            historical_cpu.registers[:] = initial
            historical_cpu.registers[PC] = 0xA9F1
            for _ in range(3):
                historical_cpu.run()
            expected = (shield - power) & 255
            assert historical_cpu.registers[PC] == 0xA9F9
            assert old[0xA894] == historical_cpu.registers[A] == expected
            assert historical_cpu.registers[F] == sub8_flags(shield, power)
            cases += 1
    report = dict(passed=True, source_archive_sha256=digest,
                  declaration='awk1.trd:3DTABS.a:PLANDICTAT', setter_source='awk1.trd:BODY.a',
                  historical_field_offset=1, historical_setter=0xAD2D,
                  current_coefficient_triplet=[3, 2, 8],
                  historical_setter_stop_before_reset_tail=0xAD7D,
                  historical_operand=0xA9F5, historical_shield=0xA894,
                  shield_subtraction_cases=cases, historical_underflow_wrap_preserved=True,
                  current_setter=0xAC5D, current_field=0x9BA5,
                  current_value_variants=256, current_setter_output_independent=True,
                  historical_behavior_restored_in_current_game=False,
                  entire_current_game_unusedness_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ParameterLegacyHitPowerVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
