"""Потребление девяти порогов DE10 исходным выбором класса, без сборки."""
from collections import Counter
import hashlib
import json

from CheckActionParameterActivation import flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step


def main():
    original = flat_action()
    controls = base_memory()
    targets = [0x7B97 + 6 * index for index in range(9)]
    # Проверка машинных потребителей каждого байта с сохранением исходных порогов.
    assert [original[address - 1] for address in targets] == [0xFE] * 9
    assert [original[address] for address in targets] == [10, 67, 80, 80, 90, 94, 99, 107, 112]
    seeds = {}
    # Поиск зерна настоящего потока 2 для каждого выходного старшего байта.
    for seed in range(65536):
        high = step(seed, 0)['word'] >> 8
        seeds.setdefault(high, seed)
        if len(seeds) == 256:
            break
    assert len(seeds) == 256
    memory = original.copy()
    sim = Simulator(memory)
    outcomes, profiles, cases = Counter(), [], 0
    for group in range(5):
        # Чтение девяти исходных шаблонных байтов с настоящим шагом группы 16.
        template = controls[0xDEDC + 16 * group:0xDEE5 + 16 * group]
        for middle in range(16):
            # Расчёт именно выходов DE10, первая запись не получает средний индекс.
            thresholds = [value + (middle if index else 0) for index, value in enumerate(template)]
            thresholds = [value & 255 for value in thresholds]
            for address, value in zip(targets, thresholds):
                memory[address] = value
            profile_outcomes = Counter()
            for maximum in (0, 63, 127):
                adjustment = (original[0x9900 + maximum // 4] >> 4) & 7
                for high in range(256):
                    for inhibit in (0, 255):
                        seed = seeds[high]
                        memory[0xEBEA:0xEBED] = [seed & 255, seed >> 8, 0]
                        memory[0x9B71], memory[0x9B74], memory[0x9B77], memory[0x9B82] = maximum, 0, 255, inhibit
                        memory[0xBFFC:0xC000] = [0x34, 0x12, 255, 63]
                        # Выбор первого выполненного сравнения, пороги не сортируются.
                        chosen = 0 if max(0, high - adjustment) < thresholds[0] else next(
                            (index for index in range(1, 9) if high < thresholds[index]), None)
                        accepted = chosen is not None and not (chosen == 8 and inhibit)
                        sim.registers[:] = get_registers({'PC': 0x7B78, 'SP': 0xBFFC}, None, False)
                        for _ in range(180):
                            if sim.registers[PC] in (0x7BDB, 0x3FFF):
                                break
                            sim.run()
                        else:
                            raise AssertionError('Выбор класса не завершился')
                        registers = sim.registers
                        context = group, middle, maximum, high, inhibit, chosen
                        assert registers[PC] == (0x7BDB if accepted else 0x3FFF), context
                        assert registers[SP] == (0xBFFC if accepted else 0xC000), context
                        if accepted:
                            assert registers[3] == chosen, context
                        else:
                            assert registers[4:6] == [0x12, 0x34], context
                        outcome = str(chosen) if accepted else 'rejected'
                        profile_outcomes[outcome] += 1
                        outcomes[outcome] += 1
                        cases += 1
            profiles.append(dict(group=group, middle=middle, thresholds=thresholds,
                                 outcomes=dict(profile_outcomes)))
    assert '3' in outcomes
    report = dict(passed=True, cases=cases, profiles=profiles, outcomes=dict(outcomes),
        operand_addresses=targets, cp_opcode_at_every_target=True,
        original_thresholds=[original[address] for address in targets],
        source_row_templates_sha256=hashlib.sha256(bytes(controls[0xDEDC:0xDF25])).hexdigest(),
        all_80_generated_group_middle_pairs=True, all_random_high_values=True,
        sampled_folded_maxima=[0, 63, 127], both_class8_inhibit_states=True,
        generated_class_three_reachable=True, producer_executed_in_this_model=False,
        producer_proof='ControlsParameterTablesVerification.json',
        stopped_before_model_selection=True, exact_all_registers_flags_or_ram_checked=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionGeneratedClassThresholdsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'profiles'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
