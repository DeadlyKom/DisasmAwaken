"""Пороги общего роста OffsetScaleLow на настоящих результатах двух создателей.

Документация: ../../../Docs/ActionObjectOffsetTransfer.md#пределы-созданных-дочерних-записей
"""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator
from CheckStationFlightCycle import payload
from CheckActionObjectOffsetTransfer import reference
from CheckActionSpawnedClass3Threshold import main as class3
from CheckActionChildInitialByte11 import main as class9


def main():
    original = payload(17)
    results = []

    def observe_created(source, source_cpu, initial, child):
        # Создатель уже исполнился полностью, проверка работает с отдельной копией его результата.
        cls, state, limit = source[child + 18], source[child + 10], source[child + 15]
        assert (cls, state, limit) in ((3, 2, 150), (9, 2, 90), (9, 14, 90))
        baseline = [bytearray(bank) for bank in source.banks]
        memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline], out7ffd=16)
        cpu = Simulator(memory)
        # Сверка всех 64 байтов общего хвоста с неизменённым ACTION.
        assert bytes(memory[a] for a in range(0xF0F8, 0xF138)) == original[0x90F8:0x9138]
        outcomes = Counter()
        for current in range(256):
            memory.recording = False
            for bank in range(8):
                memory.banks[bank][:] = baseline[bank]
            memory[child + 16] = current
            registers = list(initial)
            registers[1] = current
            registers[8:10] = [child >> 8, child & 255]
            registers[14], registers[15] = current, current * 73 & 255
            registers[26], registers[27] = current & 1, current % 3
            registers[24] = 0xF0F8
            record = {offset: memory[child + offset] for offset in (1, 7, 8, 9, 10, 15, 16, 18, 36)}
            wanted, writes, path = reference(registers, child, record)
            assert path != 'marker_return'
            expected = [bytearray(bank) for bank in memory.banks]
            expected_writes = []
            for address, value in writes:
                bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
                expected[bank][address & 0x3FFF] = value
                expected_writes.append((bank, address & 0x3FFF, value))
            cpu.registers[:] = registers
            memory.writes = []
            memory.recording = True
            cpu.run(start=0xF0F8, stop=0x6D06)
            memory.recording = False
            compared = (*range(25), 26, 27)
            assert all(cpu.registers[i] == wanted[i] for i in compared), (cls, state, current, 'registers')
            assert memory.banks == expected and memory.writes == expected_writes, (cls, state, current, 'RAM')
            # Проверка исключающего порога и сохранения прежнего масштаба в E.
            candidate = (current + 1) & 255
            assert memory[child + 16] == (candidate if candidate < limit else current)
            assert cpu.registers[5] == current
            assert memory[child + 15] == limit
            outcomes[path] += 1
        results.append(dict(class_code=cls, state=state, limit=limit,
            initialized_scale=source[child + 16], cases=sum(outcomes.values()), paths=dict(outcomes),
            exact_registers_including_R=True, all_banks_and_ordered_writes=True,
            stop=0x6D06, no_lifetime_or_destruction_claim=True))

    # Наблюдатель относится к исследовательскому коду, инструкции создателей не подменяются.
    with redirect_stdout(StringIO()):
        class3(created_record_observer=observe_created)
        class9(created_record_observer=observe_created)
    assert len(results) == 3 and sum(r['cases'] for r in results) == 768
    report = dict(passed=True, original_action_sha256=sha256(original).hexdigest(),
        creator_results=results, all_256_scale_bytes_per_created_profile=True,
        previous_local_byte11_validations_also_executed=True,
        candidate_255_wraps_to_zero_below_positive_limit=True,
        full_child_lifecycle_executed=False, downstream_6D06_executed=False,
        exact_model_T_claimed=False, irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnedScaleLimitsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
