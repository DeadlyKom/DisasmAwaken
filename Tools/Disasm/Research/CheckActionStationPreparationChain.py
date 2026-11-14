"""6CE4 -> DCE3 банка 1 -> 4200, реальные инструкции до исполнения копии загрузчика."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def main():
    flat = flat_action()
    controls = base_memory()
    base = [bytearray([0xA0 + i] * 16384) for i in range(8)]
    base[5] = bytearray(flat[0x4000:0x8000])
    base[2] = bytearray(flat[0x8000:0xC000])
    base[0] = bytearray(flat[0xC000:])
    base[1] = bytearray(controls[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in base], out7ffd=16)
    sim = Simulator(memory)
    counts = Counter()
    sums = set()
    payload = bytes(controls[0xDD23:0xDE23])
    for old in range(64):
        # Проверка достижимости Controls, блокировка допустима только при уже выбранном банке 1.
        if old & 32 and old & 7 != 1:
            continue
        for flags in range(256):
            serial = counts.total()
            memory.recording = False
            for bank, original in zip(memory.banks, base):
                bank[:] = original
            memory.out7ffd(old)
            blob = bytes((serial + i * 109) & 255 for i in range(512))
            memory.banks[2][0x1BBD:0x1DBD] = blob
            memory.banks[2][0x3FFA:0x4000] = bytes((0xA5, 0x5A, 0xC3, 0x3C, 255, 63))
            initial = get_registers({
                'AF': 0xA500 | flags, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0,
                'IX': 0xABCD, 'IY': 0xABCD, 'SP': 0xBFFE, 'PC': 0x6CE4,
            }, None, False)
            initial[14], initial[15] = serial & 255, serial & 255
            initial[26], initial[27] = serial & 1, serial % 3
            # Расчёт независимого результата перестановки, трёх переносов и последнего LDIR.
            low, high = blob[2:4]
            saved = bytearray(blob)
            saved[2:4] = bytes((high, low))
            addition = (low + payload[-1]) & 255
            sums.add(addition)
            wanted = list(initial)
            wanted[0:8] = [0x3F, (flags & 0xC1) | (addition & 8) | ((addition & 2) << 4),
                           0, 0, 0x43, 0, 0xDE, 0x23]
            wanted[10:13] = [0x5C, 0x3A, 0x5FFF]
            wanted[14], wanted[15] = 0x3F, refresh(initial[15], 3107)
            wanted[24], wanted[26], wanted[27] = 0x4200, 0, 1
            writes = [(2, 0x3FFC, 0xEC), (2, 0x3FFD, 0x6C),
                      (2, 0x3FFA, 0x9C), (2, 0x3FFB, 0x36)]
            writes += [(5, 0x1800 + i, 0) for i in range(768)]
            writes += [(2, 0x1BBF, high), (2, 0x1BC0, low)]
            writes += [(5, i, value) for i, value in enumerate(saved)]
            writes += [(5, 0x1FFD, 0), (5, 0x1FFE, 0x42)]
            writes += [(5, 0x200 + i, value) for i, value in enumerate(payload)]
            expected = [bytearray(b) for b in memory.banks]
            for bank, offset, value in writes:
                expected[bank][offset] = value
            sim.registers[:] = initial
            trace = PortTrace(sim)
            sim.set_tracer(trace)
            memory.writes = []
            memory.recording = True
            sim.run(start=0x6CE4, stop=0x4200)
            memory.recording = False
            # Проверка регистров, всех физических банков, кратности записей и настоящего OUT.
            compared = (*range(25), 26, 27)
            assert all(wanted[i] == sim.registers[i] for i in compared), (old, flags)
            assert memory.banks == expected, (old, flags, 'RAM')
            assert Counter(memory.writes) == Counter(writes), (old, flags, 'writes')
            assert trace.writes == [(0x7FFD, 17)]
            assert memory.o7ffd == (old if old & 32 else 17)
            counts['locked_bank1' if old & 32 else 'unlocked'] += 1
    assert len(sums) == 256
    report = dict(
        passed=True, total_cases=counts.total(), cases_by_paging=dict(counts),
        execution_boundary='6CE4 through real DCE3 bank1, stop before 4200 payload',
        all_32_unlocked_and_4_locked_bank1_configurations=True, all_input_F=True,
        all_256_final_LDIR_flag_sums=True, exact_registers_including_R=True,
        all_physical_ram_and_write_multiplicity_checked=True, real_OUT_checked=True,
        refresh_m1=3107, final_SP=0x5FFF, old_return_not_consumed=True,
        complete_saved_data_product_exhausted=False, IRQ_executed=False,
        payload_4200_executed=False, station_disk_load_executed=False,
        assembly_executed=False, native_execution=False, timing_proved=False,
    )
    (ROOT / 'Tools/Disasm/Reports/ActionStationPreparationChainVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
