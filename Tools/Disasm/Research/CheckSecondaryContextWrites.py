"""Присваивания LANG за таблицей второго оснащения и их перенос через SAVE."""
import json

from CheckAwakenBasicRun import model_rom_context
from CheckSaveSlotDosRom import MODES, transfer
from CheckScreenUpdate import PortTrace, put
from CheckSecondaryContextAliases import ContextMemory, QUANTITIES, TAIL
from CheckStationFlightCycle import DISK, ENTRIES, ROOT, payload
from ProbeShipPreviewCallbacks import make_context
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, get_registers


STATE = 0x983B
ASSIGNMENT_WRITE = 0xC6E2
SCRIPT = 0xCA8F


class WriteTrace(ContextMemory):
    def __setitem__(self, address, value):
        if isinstance(address, int) and STATE <= address < STATE + 512:
            self.state_writes.append((address, self.registers[PC], value))
        super().__setitem__(address, value)


def run_script(banks, block, assignments):
    memory = WriteTrace(banks=[bytearray(bank) for bank in banks], out7ffd=0x16)
    sim = Simulator(memory)
    sim.set_tracer(PortTrace(sim))
    memory.registers = sim.registers
    memory.reads, memory.script_entries, memory.state_writes = [], [], []
    put(memory, STATE, block)
    memory.state_writes.clear()
    script = ''.join(f'=i{address - QUANTITIES + 1}:{value}\r' for address, value in assignments)
    put(memory, SCRIPT, script.encode('ascii') + b'\0')
    put(memory, 0x7FFE, b'\xFF\x3F')
    memory[0x6306] = 0x16
    sim.registers[:] = get_registers({'SP': 0x7FFE, 'PC': 0xC000, 'IY': 0x5C3A}, None, False)
    for _ in range(25000):
        if sim.registers[PC] == 0x3FFF:
            break
        sim.run()
    else:
        raise AssertionError((script, hex(sim.registers[PC])))

    # Проверяем исходный код цели, выбор инверсии в Store и все записи блока.
    expected = bytearray(block)
    expected_reads, expected_writes = [], []
    for address, value in assignments:
        offset = address - STATE
        old = expected[offset]
        stored = (value & 255) ^ (255 if old & 128 else 0)
        expected_reads.extend(((address, 0xC1DC, old), (address, 0xC6DC, old)))
        expected_writes.append((address, ASSIGNMENT_WRITE, stored))
        expected[offset] = stored
    assert memory.reads == expected_reads, (script, memory.reads)
    assert memory.state_writes == expected_writes, (script, memory.state_writes)
    assert bytes(memory[STATE:STATE + 512]) == expected
    assert sim.registers[SP] == 0x8000 and memory.o7ffd == 0x16
    return bytes(expected), expected_writes


def main():
    _, _, banks = make_context()
    lang = payload(5)
    script_banks = [bytearray(bank) for bank in banks]
    script_banks[6][:len(lang)] = lang
    rom_path = ROOT / 'Tools/Disasm/Research/Runtime/Unreal/rom/trdos504t.rom'
    basic, dos, sysvars = model_rom_context(rom_path)
    profiles = []
    for row in range(6):
        entry = next(item for item in ENTRIES.values() if item['name'] == f'SAVE{row}')
        slot, offset = entry['slot'], entry['offset']
        block = payload(slot)
        for address in TAIL:
            for value in (0, 35, 127, 128, 255, 256, 65535):
                run_script(script_banks, block, [(address, value)])
        modified, writes = run_script(script_banks, block, list(zip(TAIL, (35, 49, 65, 81), strict=True)))

        # Писатель SAVE и последующий загрузчик получают свои обычные рамки диспетчера.
        disk = bytearray(DISK)
        written, write_ports = transfer(banks, sysvars, basic, dos, MODES[0], row, disk, modified, slot)
        restored, read_ports = transfer(banks, sysvars, basic, dos, MODES[1], row, disk, bytes(512), slot)
        sectors = [(track, sector + 1) for track, sector in
                   (divmod(offset // 256 + index, 16) for index in range(2))]
        assert written == restored == modified
        assert disk == DISK[:offset] + modified + DISK[offset + 512:]
        assert write_ports.written_sectors == read_ports.attempts[-2:] == sectors
        profiles.append(dict(file=entry['name'], directory_slot=slot, writes=writes,
                             sectors=sectors, bytes_reloaded=len(restored)))
    report = dict(passed=True, single_assignment_cases=6 * len(TAIL) * 7,
                  assignments_in_reloaded_profiles=6 * len(TAIL), profiles=profiles,
                  substituted_lang_text=True, original_lang_interpreter=True,
                  original_trdos_rom=True, physical_disk_written=False,
                  native_execution=False, assembly_executed=False)
    result = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/SecondaryContextWritesVerification.json').write_text(result, encoding='utf-8')
    print('Проверены 168 одиночных присваиваний и запись с чтением всех шести SAVE.')


if __name__ == '__main__':
    main()
