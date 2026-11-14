"""Начальный байт #11 класса 3 и полный байтовый домен локального порога State02.

Документация: ../../../Docs/ActionPeriodicClass3State.md#начальный-порог-состояния-02
"""
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers
from CheckStationFlightCycle import payload
from CheckActionByte11ThresholdDomain import verify_local_threshold


def main(created_record_observer=None):
    original = payload(17)
    # Проверка таблицы State02 и трёх исходных инструкций локального сравнения.
    assert original[0xEF54 - 0x6000:0xEF56 - 0x6000] == bytes.fromhex('38f1')
    assert original[0xF211 - 0x6000:0xF217 - 0x6000] == bytes.fromhex('7dddbe11300b')
    flat = flat_action()
    banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    for bank, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank] = bytearray(flat[address:address + 0x4000])
    memory = RecordedBanks(banks=banks, out7ffd=16)
    # Создание одного свободного места и настоящего родителя State0B.
    for row in range(25):
        pointer = 0xA100 + 64 * row
        memory[pointer], memory[pointer + 1], memory[pointer + 24] = 0, 1, 0
    memory[0xA101] = 128
    memory[0xA740], memory[0xA741] = 128, 128
    parent = 0xA700
    for axis, value in enumerate((0x1234, 0x7FFF, 0xFF80)):
        memory[parent + axis * 2], memory[parent + axis * 2 + 1] = value & 255, value >> 8
    memory[parent + 10], memory[parent + 13], memory[parent + 22] = 11, 1, 1
    memory[0x9BC1], memory[0x9BC2] = 0x38, 0x4B
    memory[0xF3F1] = 15
    memory[0xBFFE], memory[0xBFFF] = 255, 63
    initial = get_registers({'PC': 0xF3F0, 'SP': 0xBFFE, 'AF': 0x1357,
        'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
        '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
        'IX': parent, 'IY': 0x5C3A}, None, False)
    cpu = Simulator(memory)
    cpu.registers[:] = initial
    memory.writes = []
    memory.recording = True
    cpu.run(start=0xF3F0, stop=0x3FFF)
    memory.recording = False
    child = cpu.registers[10] * 256 + cpu.registers[11]
    # Проверка значений, записанных полным создателем без подмены его детей.
    assert child == 0xA100
    assert memory[child + 18] == 3 and memory[child + 10] == 2
    threshold = memory[child + 17]
    assert threshold == 70
    creation_writes = len(memory.writes)
    if created_record_observer is not None:
        created_record_observer(memory, cpu, initial, child)
    branches = verify_local_threshold(memory, cpu, initial, child)
    result = dict(passed=True, original_action_sha256=sha256(original).hexdigest(),
        real_creator_entry=0xF3F0, real_creator_complete_return=True,
        real_creator_write_events=creation_writes, created_record=child,
        created_class=3, created_state=2, initialized_field11=threshold,
        compared_local_entry=0xF211, local_original_bytes='7dddbe11300b',
        cases=sum(branches.values()), branches=dict(branches),
        every_low_byte_and_input_F=True, threshold_unchanged=True,
        exact_all_registers_including_R_and_model_T=True,
        I_IM_IFF_varied_and_preserved=True, all_eight_banks_unchanged_by_comparison=True,
        full_State02_executed=False, random_stream_sampled=False,
        selected_children_executed=False, native_probability_claimed=False,
        irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnedClass3ThresholdVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
