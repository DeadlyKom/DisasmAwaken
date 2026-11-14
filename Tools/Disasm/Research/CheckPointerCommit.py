"""Исходная фиксация BC в PointerXY, точный R и все CPU-записи RAM.

Документация: ../../../Docs/PointerInputs.md#фиксация-координат-и-граница-шага
"""
from hashlib import sha256
import json
from CheckGeometryReturnEntries import ROOT, Simulator, get_registers, Memory


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(x for x in manifest['entries'] if x['slot'] == 4)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    assert len(source) == entry['allocated_length']
    assert disk[entry['offset']:entry['offset'] + len(source)] == source
    assert source[0x97F:0x984] == bytes.fromhex('ed430763c9')
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex('320070')
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    memory[0x6000:0x6000 + len(source)] = source
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    assert bytes(memory[0x66D3:0x66D8]) == source[0x97F:0x984]
    cpu = Simulator(memory)
    initial = get_registers({'HL':0x1357, 'DE':0x2468, 'BC':0x369C, 'AF':0x47AD,
        '^HL':0x5678, '^DE':0x6789, '^BC':0x789A, '^AF':0x89AB,
        'IX':0x9ABC, 'IY':0xABCD, 'SP':0xBFFE}, None, False)
    for value in range(65536):
        high, low = value >> 8, value & 255
        memory[0x6307:0x6309] = bytes.fromhex('a55a')
        memory[0xBFFE:0xC000] = bytes.fromhex('ff3f')
        expected = list(initial)
        expected[0], expected[1] = high, high ^ low
        expected[2], expected[3] = high, low
        expected[14], expected[15] = high, low
        expected[26], expected[27] = low & 1, high % 3
        expected[24] = 0x66D3
        cpu.registers[:] = expected
        memory.writes.clear()
        memory.recording = True
        cpu.run(0x66D3, 0x3FFF)
        memory.recording = False
        expected[12], expected[24] = 0xC000, 0x3FFF
        expected[15] = (low & 0x80) | ((low + 3) & 0x7F)
        assert all(cpu.registers[i] == expected[i] for i in range(len(expected)) if i != 25), value
        assert memory.writes == [(0x6307, low), (0x6308, high)], (value, memory.writes)
        assert memory[0x6307:0x6309] == value.to_bytes(2, 'little')
        assert memory[0xBFFE:0xC000] == bytes.fromhex('ff3f')
    report = dict(passed=True, method='original_relocated_ED43_RET_against_all_BC_words_and_RAM_write_watch',
        cases=65536, all_BC_words=True, all_AF_values_covered=True, all_initial_R_values_covered=True,
        full_joint_BC_AF_R_product=False, exact_registers_except_T_checked=True,
        M1=3, R_bit7_preserved=True, SP_delta=2,
        every_CPU_RAM_write_value_and_order_checked=True, only_PointerXY_written=True,
        no_own_stack_writes=True, return_word_unchanged=True, CPU_write_watch_positive_control=True,
        original_disk_sha256=sha256(disk).hexdigest(), original_code_sha256=sha256(source[0x97F:0x984]).hexdigest(),
        relocated_bytes_matched_physical_source=True, previous_direction_not_executed=True,
        IRQ_or_hardware_input_executed=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/PointerCommitVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('passed','cases','M1','SP_delta','only_PointerXY_written')}))


if __name__ == '__main__':
    main()
