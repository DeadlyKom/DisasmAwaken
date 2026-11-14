"""Обработчики ожидания, роста и спада фазы до полного RET через F0F8 и 6D06.

Документация: ../../../Docs/ActionObjectOffsetRise.md#полный-возврат-через-общий-вычислитель
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionObjectPhaseHandlers import reference as phase_reference
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from CheckStationFlightCycle import payload


def profiles():
    # Прежние полные профили роста и спада, по 8192 на вход.
    for entry in (0xEF7D, 0xEF9A):
        for phase in range(256):
            for timer in (0, 1, 2, 255):
                for saved in (2, 0x13):
                    for cls in (3, 20):
                        for marker in (False, True):
                            yield entry, {1: 128 if marker else 127, 7: phase, 8: phase * 73 & 255,
                                9: phase * 109 & 255, 10: 0x13 if phase & 1 else (0x14 if entry == 0xEF7D else 0x15),
                                15: (phase + 1) & 255, 16: phase * 31 & 255,
                                18: cls, 22: saved, 23: timer, 36: 0x80}, 0
    # Ожидание, все старшие масштабы и три профиля свёрнутых компонент.
    for gate in (0, 1, 17, 34, 68, 128, 136, 255):
        for high in range(256):
            for cls in (0, 7, 8, 20):
                for components in ((0, 0, 0), (20, 0, 0), (128, 127, 255)):
                    for saved in (2, 0x13):
                        yield 0xEFB5, {1: components[0], 3: components[1], 5: components[2],
                            7: (high * 73 + gate) & 255, 8: high * 109 & 255, 9: high ^ gate,
                            10: 0x13, 15: high ^ 255, 16: (high * 31 + gate) & 255,
                            18: cls, 22: saved, 23: 7, 36: high}, gate


def main():
    assert payload(17)[0xEFBD - 0x6000] == 0x11
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    cpu = Simulator(memory)
    paths = Counter()
    touched = set()
    cases = 0
    for entry, record, gate in profiles():
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        ix = 0xA100 + 64 * (cases % 16)
        stack = (0x9008, 0xBFFE)[cases & 1]
        for offset, value in record.items():
            memory[ix + offset] = value
        memory[stack], memory[stack + 1] = 255, 63
        memory[0xEFBD] = gate
        initial = get_registers({'PC': entry, 'SP': stack, 'AF': cases & 65535,
            'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, 'IX': ix, 'IY': 0x5C3A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = cases & 255, cases * 73 & 255, cases & 1, cases % 3
        expected = [bytearray(b) for b in memory.banks]
        expected_writes = []

        def apply(writes, update_record=False):
            for address, value in writes:
                bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
                expected[bank][address & 0x3FFF] = value
                expected_writes.append((bank, address & 0x3FFF, value))
                if update_record and ix <= address < ix + 64:
                    record[address - ix] = value

        # Числовой эталон собственного префикса обновляет запись до проверки общего хвоста.
        wanted, writes, phase_path = phase_reference(entry, initial, record, gate, ix)
        apply(writes, update_record=True)
        wanted, writes, prepare_path = prepare_reference(wanted, ix, record)
        apply(writes)
        if wanted[24] == 0x6D06:
            view = RecordedBanks(banks=expected, out7ffd=16)
            result = vector_reference(view, wanted, (record[7], (record[8] + 128) & 255, record[9]), 0x3FFF)
            wanted = result['registers']
            apply(result['writes'])
        cpu.registers[:] = initial
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.writes = []
        memory.recording = True
        cpu.run(start=entry, stop=0x3FFF)
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(cpu.registers[i] == wanted[i] for i in compared), (entry, record, gate, 'registers')
        assert memory.banks == expected and Counter(memory.writes) == Counter(expected_writes), (entry, record, gate, 'RAM')
        assert not ports.writes and memory.o7ffd == 16
        touched = {(bank, offset) for bank, offset, _ in expected_writes}
        touched.update((2, (ix + offset) & 0x3FFF) for offset in record)
        touched.update((2, (stack + i) & 0x3FFF) for i in (0, 1))
        touched.add((0, 0xEFBD & 0x3FFF))
        paths[f'{entry:04X}/{phase_path}/{prepare_path}'] += 1
        cases += 1
    assert cases == 65536
    report = dict(passed=True, original_action_sha256=sha256(payload(17)).hexdigest(),
        total_cases=cases, paths=dict(paths), full_external_return=True,
        real_F0F8_and_coefficients_and_three_multiplications=True,
        exact_registers_including_R=True, all_eight_banks_and_write_multiplicity=True,
        all_256_rise_fall_phase_bytes=True, rise_fall_timer_samples=[0, 1, 2, 255], saved_state_samples=[2, 19],
        rise_fall_class_samples=[3, 20], marker_and_active_records=True, rise_fall_original_high_scale=128,
        wait_all_256_high_scale_bytes=True, wait_phase_gate_samples=[0, 1, 17, 34, 68, 128, 136, 255],
        wait_class_samples=[0, 7, 8, 20], wait_component_profiles=[[0, 0, 0], [20, 0, 0], [128, 127, 255]],
        phase_correlated_current_state_and_low_scale=True, full_input_product_exhausted=False,
        no_OUT=True, exact_T_claimed=False, irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectPhaseHandlersCompositionVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
