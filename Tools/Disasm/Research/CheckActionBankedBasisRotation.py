"""Сверка обёртки ADB7 с прямым вызовом VOXAL E500 в странице 3."""
import json
from random import Random

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[3][:] = bytes(memory_image()[0xC000:])
    rng = Random(0xADB7)
    changes = 0
    for index in range(1024):
        actual = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        for address in range(0x9B00, 0x9B15):
            actual[address] = 0 if index == 0 else rng.randrange(256)
        stack = 0xBFFE
        actual[stack], actual[stack + 1] = 255, 63
        direct = RecordedBanks(banks=[bank.copy() for bank in actual.banks], out7ffd=19)
        bc = (index * 71) & 65535
        initial = get_registers({'PC': 0xADB7, 'SP': stack, 'AF': index & 255, 'BC': bc,
                                 'IX': 0xABCD, 'IY': (index * 89) & 65535}, None, False)
        expected_sim = Simulator(direct)
        expected_sim.registers[:] = initial
        expected_sim.registers[0] = 19
        expected_sim.registers[SP] = stack - 2
        expected_sim.registers[15] = refresh(initial[15], 9)
        for address, value in zip(range(stack - 4, stack), (bc & 255, bc >> 8, 0xBF, 0xAD)):
            direct[address] = value
        expected_sim.run(0xE500, 0xADBF)
        wanted = list(expected_sim.registers)
        assert wanted[SP] == stack
        wanted[0], wanted[SP], wanted[PC] = 16, stack + 2, 0x3FFF
        wanted[15] = refresh(wanted[15], 9)
        for address, value in zip(range(stack - 4, stack), (wanted[3], wanted[2], 0xC4, 0xAD)):
            direct[address] = value
        sim = Simulator(actual)
        sim.registers[:] = initial
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        before = bytes(actual[0x9B00:0x9B12])
        sim.run(0xADB7, 0x3FFF)
        compared = (*range(13), *range(14, 25), 26, 27)
        assert all(sim.registers[i] == wanted[i] for i in compared), (
            index, [(i, sim.registers[i], wanted[i]) for i in compared if sim.registers[i] != wanted[i]])
        assert actual.banks == direct.banks and trace.writes == [(0x7FFD, 19), (0x7FFD, 16)]
        assert actual.o7ffd == 16
        changes += bytes(actual[0x9B00:0x9B12]) != before
    assert changes
    report = dict(passed=True, total_cases=1024, basis_changed=changes,
                  exact_registers_and_physical_ram=True, direct_child_comparison=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionBankedBasisRotationVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
