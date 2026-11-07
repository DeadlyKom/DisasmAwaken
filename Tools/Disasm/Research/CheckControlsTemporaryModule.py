"""Первые три копирования DADE и достижимый предел при исходном нулевом BC."""
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from PackedResourceCodec import decode


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    sentinel = bytes((index * 37 + 33) & 255 for index in range(0x3400))
    baseline[2][0x0C00:] = sentinel
    panel = decode((ROOT / 'Tools/Disasm/Extracted/Active/25_PANEL.C.bin').read_bytes())['data']
    baseline[6][:len(panel)] = panel
    direct = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=17)
    direct_sim = Simulator(direct)
    direct_trace = PortTrace(direct_sim)
    direct_sim.set_tracer(direct_trace)
    direct_sim.registers[:] = get_registers({'PC': 0xDADE, 'SP': 0x5FF0}, None, False)
    direct_sim.run(0xDADE, 0xDAEB)
    assert direct_trace.writes == [(0x7FFD, 22)]
    assert direct.banks[1][0x1AEB] == 0xD9 and direct[0xDAEB] == 0x04
    template = baseline[1][0x1ADE:0x1B5D]
    fixture = 0x5000

    def relocated(original_pc):
        return fixture + original_pc - 0xDADE

    cases = []
    for length in (0, 1, 12, 0x600, 0x1C00, 0x2000):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=17)
        put(memory, fixture, template)
        if length:
            put(memory, relocated(0xDB01), length.to_bytes(2, 'little'))
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': fixture, 'SP': 0x5FF0, 'IX': 0x1234}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        limit = 0x4001 if not length else 40000
        steps = 0
        for _ in range(50000):
            pc = sim.registers[PC]
            if pc == relocated(0xDB20):
                break
            if pc == relocated(0xDB08):
                steps += 1
            sim.run()
            if steps == limit:
                break
        assert trace.writes == [(0x7FFD, 22), (0x7FFD, 17)], (length, trace.writes, sim.registers[PC], steps)
        assert bytes(memory.banks[6][:0x3400]) == sentinel
        assert bytes(memory[0x5E33:0x5E35]) == bytes((0xEE, 0x5F))
        assert bytes(memory[0x5FEE:0x5FF0]) == bytes((0x34, 0x12))
        if length:
            assert sim.registers[PC] == relocated(0xDB20) and sim.registers[SP] == 0x5FEE, length
            assert steps == length
            assert bytes(memory[0xE000:0x10000]) == bytes(baseline[5][0x2000:])
            assert bytes(memory[0x6400:0x6400 + length]) == bytes(baseline[1][0x600:0x600 + length])
            assert sim.registers[4:8] == [0x64, 0, 0x64, 0]
        else:
            assert sim.registers[PC] == relocated(0xDB08) and sim.registers[SP] == 0x5FEA
            assert steps == 0x4001 and memory[0xC000] == memory[0x0600]
        cases.append(dict(length=length, ldir_iterations=steps, stop_address=sim.registers[PC]))
    report = dict(passed=True, total_cases=len(cases), cases=cases,
                  direct_switch_changes_next_opcode=True, stored_opcode=0xD9, bank6_panel_opcode=0x04,
                  zero_count_reaches_destination_bank1=True, relocated_cases_are_hypothetical=True,
                  unpack_and_temporary_code_executed=False, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ControlsTemporaryModuleVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
