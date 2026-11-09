"""Условная цепочка CONTROL до CALL 6500 с исходным распаковщиком ACTION."""
import json

from CheckControlsTemporaryModule import ROOT, RecordedBanks, flat_action, base_memory, decode
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())['entries']
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    screens = json.loads((reports / 'Screens.json').read_bytes())
    base = 0x5DA0

    def relocated(address):
        return base + address - 0xDADE

    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    template = baseline[1][0x1ADE:0x1B5D]
    assert template[0xDB20 - 0xDADE:0xDB23 - 0xDADE] == bytes.fromhex('CD 23 AB')
    cases = []
    for screen in screens:
        slot = screen['slot']
        entry = next(entry for entry in manifest if entry['slot'] == slot)
        start = entry['offset'] + screen['offset']
        size = screen['packed_size']
        packed = disk[start:start + size]
        expected = decode(packed, disk[start + size:start + size + 2])['data']
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=0x11)
        put(memory, base, template)
        put(memory, 0xC600, packed)
        put(memory, relocated(0xDB01), size.to_bytes(2, 'little'))
        simulator = Simulator(memory, config={'fast_ldir': False, 'fast_djnz': False})
        r = simulator.registers
        r[:] = get_registers({'PC': base, 'SP': 0x5FF0, 'IX': 0x1234}, None, False)
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        saw_unpack = False
        for steps in range(600000):
            if r[PC] == 0x6500:
                break
            if r[PC] == 0xAB23:
                assert not saw_unpack and r[4:8] == [0x64, 0, 0x64, 0]
                assert bytes(memory[0x6400:0x6400 + size]) == packed
                saw_unpack = True
            simulator.run()
        else:
            raise AssertionError(('предел временного распаковщика', slot, screen['index'], hex(r[PC])))
        assert saw_unpack and trace.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
        assert r[SP] == 0x5FFE and bytes(memory[0x5FFE:0x6000]) == relocated(0xDB29).to_bytes(2, 'little')
        assert bytes(memory[0x6400:0x6400 + len(expected)]) == expected
        assert bytes(memory.banks[6][:0x3400]) == bytes(baseline[2][0x0C00:])
        assert bytes(memory.banks[1][0x2000:]) == bytes(baseline[5][0x2000:])
        assert bytes(memory[0x5E33:0x5E35]) == bytes.fromhex('EE 5F')
        cases.append(dict(slot=slot, index=screen['index'], packed_bytes=size,
                          unpacked_bytes=len(expected), instructions=steps))
    assert len(cases) == 20
    report = dict(passed=True, total_cases=len(cases), cases=cases,
                  original_ldir_and_action_unpacker_executed=True, call_frame_at_6500_checked=True,
                  source_and_length_supplied_in_model=True, hypothetical_template_relocation=True,
                  payload_instructions_executed=False, actual_game_caller_proved=False,
                  assembly_executed=False, native_execution=False)
    (reports / 'ControlsTemporaryUnpackBoundaryVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
