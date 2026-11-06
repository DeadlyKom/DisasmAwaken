"""Полный 6E6C без нажатых клавиш, с настоящим сканером и затуханием."""
from itertools import product
import json

from CheckActionKeyDispatchPrefix import Inputs
from CheckActionObjectOffsetVector import multiply
from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers


def main():
    baseline = flat_action()
    cases = 0
    for value, enabled, coefficient in product((0, 1, 2, 0x7FFF, 0x8000, 0xFFFE, 0xFFFF), (0, 1, 255), range(256)):
        memory = baseline.copy()
        memory[0xBFFE:0xC000] = [255, 63]
        memory[0x6EAD] = enabled
        memory[0x6F56] = memory[0x6F59] = 0
        memory[0xA78F:0xA791] = list(value.to_bytes(2, 'little'))
        coefficients = (coefficient, coefficient ^ 255, (coefficient * 73) & 255)
        for address, parameter in zip((0xCBD8, 0xCBEE, 0xCC09), coefficients):
            memory[address] = parameter
        wanted = {0: 0xFFFE, 1: 0xFFFF, 65535: 1}.get(value, value) if enabled else value
        sim = Simulator(memory)
        trace = Inputs(-1, 255)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x6E6C, 'SP': 0xBFFE}, None, False)
        sim.run(0x6E6C, 0x3FFF)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000
        assert len(trace.reads) == 27 and all(value == 255 for _, value in trace.reads)
        assert bytes(memory[0xA78F:0xA791]) == wanted.to_bytes(2, 'little')
        for address, parameter in zip((0xE5B3, 0xE5D2, 0xE5ED), coefficients):
            product_word, _ = multiply([0] * 28, parameter, wanted)
            assert bytes(memory[address:address + 2]) == product_word.to_bytes(2, 'little')
        cases += 1
    report = dict(passed=True, total_cases=cases, all_coefficient_bytes=True,
                  key_handlers_skipped_by_input=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionMotionWithoutKeysVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
