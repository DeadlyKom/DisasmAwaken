"""Рабочая рамка InitializeFinal и повреждение исходного bitmap при перекрытии стеком.

Документация: ../../../Docs/FinalCycle.md#стек-до-копирования-bitmap
"""
from hashlib import sha256
import json

from CheckFinal import original_memory
from CheckFinalCycle import FinalMemory, InputPorts
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, I, IM, IFF, IYh, IYl, get_registers


def main():
    flat = original_memory()
    payload = bytes(flat[0x6000:0xAAAA])
    assert payload == DISK[ENTRIES[29]['offset']:ENTRIES[29]['offset'] + len(payload)]
    bitmaps = [bytes(flat[0x62A9 + index * 6144:0x62A9 + (index + 1) * 6144]) for index in range(3)]
    profiles = []
    for stack in (0x5FFE, 0x5FFF, 0x7FFE):
        banks = [bytearray([0xA0 + index] * 16384) for index in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][:] = bytes(flat[0x8000:0xC000])
        memory = FinalMemory(banks=banks, out7ffd=16)
        cpu = Simulator(memory)
        ports = InputPorts(cpu, None, False)
        cpu.set_tracer(ports)
        cpu.registers[:] = get_registers(dict(PC=0x6000, SP=stack, IY=0xABCD), {'im':1, 'iff':0}, False)
        min_sp = stack
        before_builder = None
        for _ in range(100000):
            pc = cpu.registers[PC]
            if pc == 0x6196:
                assert before_builder is None
                differences = []
                for bank, expected in zip((7, 0, 1), bitmaps):
                    changes = [dict(source_address=0x62A9 + (0 if bank == 7 else 1 if bank == 0 else 2) * 6144 + offset,
                                    bank=bank, offset=offset, expected=value, actual=memory.banks[bank][offset])
                               for offset, value in enumerate(expected) if memory.banks[bank][offset] != value]
                    differences.extend(changes)
                before_builder = dict(input_SP=cpu.registers[SP], copied_bitmap_differences=differences)
                assert bytes(memory.banks[7][0x1800:0x1B00]) == bytes([0x88] * 768)
                assert bytes(memory[0xBE00:0xBF01]) == bytes([0xBF] * 257)
                assert bytes(memory[0xBFBF:0xBFC2]) == bytes.fromhex('c36c61')
            if pc == 0x607A:
                break
            cpu.run()
            min_sp = min(min_sp, cpu.registers[SP])
        else:
            raise AssertionError(('final_first_frame_pair_not_reached', stack))
        r = cpu.registers
        assert before_builder is not None and before_builder['input_SP'] == stack - 2
        assert min_sp == stack - 14 and r[SP] == stack
        assert (r[I], r[IM], r[IFF], memory.o7ffd) == (0xBE, 2, 0, 1)
        assert r[:8] == [1, 0x9B, 0, 0, 0x80, 3, 0xA9, 0x37]
        assert r[IYh] * 256 + r[IYl] == 0xABCD
        assert ports.writes == [(0x7FFD, 0x1F), (0x7FFD, 7), (0x7FFD, 0), (0x7FFD, 1)]
        changes = before_builder['copied_bitmap_differences']
        if stack == 0x7FFE:
            assert changes and all(row['bank'] == 0 and 0x7FF8 <= row['source_address'] < 0x7FFE for row in changes)
        else:
            assert not changes
        profiles.append(dict(entry_SP=stack, minimum_SP=min_sp, SP_before_frame_pair=r[SP],
                             temporary_stack_bytes=stack - min_sp, **before_builder,
                             first_pair_HL=0xA937, first_pair_DE=0x8003, first_pair_BC=0, first_pair_AF=0x019B,
                             first_pair_I=r[I], first_pair_IM=r[IM], first_pair_IFF=r[IFF], paging=memory.o7ffd))
    report = dict(passed=True, original_final_payload_sha256=sha256(payload).hexdigest(), profiles=profiles,
                  actual_prepare_frame_and_builder_executed=True, stopped_before_first_EI_and_HALT=True,
                  initial_IFF=0, maximum_temporary_stack_bytes=14,
                  stack_outside_generated_code_alone_is_insufficient=True,
                  natural_game_stack_at_7FFE_proved=False, all_stack_locations_proved=False,
                  IRQ_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/FinalStartupStackVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены рамка 14 байтов, два рабочих стека и перекрытие bitmap стеком 7FFE.')


if __name__ == '__main__':
    main()
