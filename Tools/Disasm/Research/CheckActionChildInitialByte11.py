"""Создание класса 9 с состояниями 02/0E и локальный порог только для State02.

Документация: ../../../Docs/ActionChildSpawn.md#начальный-байт-11-и-состояние-ребёнка
"""
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers
from CheckStationFlightCycle import payload
from ReferenceActionFoldedRandom import step
from CheckActionByte11ThresholdDomain import verify_local_threshold


def main(created_record_observer=None):
    original = payload(17)
    # Проверка машинных инструкций специализированного входа и передачи состояния 0E.
    assert original[0xE863 - 0x6000:0xE86B - 0x6000] == bytes.fromhex('dd7e12fe08c03e02')
    assert original[0xF6C8 - 0x6000:0xF6CD - 0x6000] == bytes.fromhex('3e0ecd6be8')
    assert original[0xF211 - 0x6000:0xF217 - 0x6000] == bytes.fromhex('7dddbe11300b')
    flat = flat_action()
    banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    for bank, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank] = bytearray(flat[address:address + 0x4000])
    memory = RecordedBanks(banks=banks, out7ffd=16)
    baseline = [bytearray(bank) for bank in memory.banks]
    cpu = Simulator(memory)
    # Подбор исходного слова с допущенным первым новым младшим байтом потока 11.
    seed = next(value for value in range(65536) if step(value, 0)['word'] & 255 == 0)
    outcomes = []
    for entry, state in ((0xE863, 2), (0xE86B, 14)):
        memory.recording = False
        for bank in range(8):
            memory.banks[bank][:] = baseline[bank]
        # Один свободный слот, остальные заняты, родитель имеет полный класс 8.
        for row in range(25):
            pointer = 0xA100 + 64 * row
            memory[pointer], memory[pointer + 1], memory[pointer + 24] = 0, 1, 0
        memory[0xA101] = 128
        memory[0xA740], memory[0xA741] = 128, 128
        parent = 0xA700
        for axis, value in enumerate((0x1234, 0x2345, 0x3456)):
            memory[parent + axis * 2], memory[parent + axis * 2 + 1] = value & 255, value >> 8
        memory[parent + 18], memory[parent + 11] = 8, 1
        memory[0xEBED], memory[0xEBEE], memory[0xEBEF] = seed & 255, seed >> 8, 0
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        initial = get_registers({'PC': entry, 'SP': 0xBFFE, 'AF': state * 256 + 0x57,
            'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': parent, 'IY': 0x5C3A}, None, False)
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        cpu.run(start=entry, stop=0x3FFF)
        memory.recording = False
        # Проверка настоящего результата с сохранением начального байта при обоих состояниях.
        child = 0xA100
        assert memory[child + 18] == 9 and memory[child + 10] == state
        assert memory[child + 17] == 40
        item = dict(entry=entry, state=state, class_code=9, child=child,
            initialized_byte11=40, real_creator_write_events=len(memory.writes),
            real_creator_complete_return=True)
        if created_record_observer is not None:
            created_record_observer(memory, cpu, initial, child)
        if state == 2:
            branches = verify_local_threshold(memory, cpu, initial, child)
            item.update(local_cases=sum(branches.values()), local_branches=dict(branches),
                exact_local_registers_R_model_T_and_all_RAM=True)
        else:
            item.update(State0E_executed=False, threshold_role_for_State0E_claimed=False)
        outcomes.append(item)
    result = dict(passed=True, original_action_sha256=sha256(original).hexdigest(),
        seed=seed, outcomes=outcomes, local_compare_entry=0xF211,
        all_low_bytes_and_input_F_for_created_State02=True,
        other_constructor_inputs_exhausted=False, full_State02_executed=False,
        original_State0E_caller_executed=False, random_stream_sampled_in_local_comparison=False,
        irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionChildInitialByte11Verification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
