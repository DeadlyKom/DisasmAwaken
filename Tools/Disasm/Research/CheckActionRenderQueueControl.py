"""Два коротких управляющих входа очереди, исполнение её потребителя не подменяется доказательством."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import cp_flags, refresh


def main():
    memory = Memory(flat_action())
    simulator = Simulator(memory)
    counts = Counter()
    for entry in (0xE4A6, 0xE4FF):
        # Проверка всех слов сохранённого SP либо всех сочетаний входных A и F, на этих границах RAM не записывается.
        for value in range(65536):
            memory.recording = False
            memory[0xBFFE:0xC000] = [0xFF, 0x3F]
            memory[0xE4A7:0xE4A9] = [value & 255, value >> 8]
            memory[0x9BA1] = value & 255
            af = value if entry == 0xE4FF else 0xA500 | (value >> 8)
            initial_hl = (value * 71) & 65535 if entry == 0xE4A6 else 0x8F73
            initial = get_registers({'AF': af, 'HL': initial_hl, 'DE': 0x2468, 'BC': 0x369C,
                '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
                'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': entry}, None, False)
            initial[14], initial[15], initial[26], initial[27] = value & 255, value & 255, value & 1, value % 3
            wanted = list(initial)
            if entry == 0xE4A6:
                wanted[0], wanted[6], wanted[SP], wanted[PC] = value & 255, 0x8F, value, 0xE4FF
                m1, path = 4, 'start'
            else:
                a = value >> 8
                wanted[1] = cp_flags(a, 1)
                if a == 1:
                    wanted[SP], wanted[PC] = 0xC000, 0x3FFF
                    m1, path = 2, 'end_return'
                else:
                    wanted[7], wanted[PC] = a, 0xE4B1
                    m1, path = 4, 'select_node'
            wanted[15] = refresh(initial[15], m1)
            simulator.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(5):
                if simulator.registers[PC] == wanted[PC]:
                    break
                simulator.run()
            else:
                raise AssertionError('граница управляющего входа')
            memory.recording = False
            compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
            assert all(wanted[i] == simulator.registers[i] for i in compared), (entry, value,
                [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
            assert not memory.writes
            counts[path] += 1
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), all_saved_sp_words=True,
        all_selector_af_words=True, exact_registers_flags_refresh_sp=True, no_ram_writes=True,
        start_boundary='E4A6..E4FF, selector not executed', selector_boundary='E4FF..E4B1 or external return',
        selector_h_provided_by_caller=True, saved_sp_not_validated_as_native_stack=True,
        full_consumer_executed=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderQueueControlVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
