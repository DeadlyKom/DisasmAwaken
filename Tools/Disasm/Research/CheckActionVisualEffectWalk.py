"""Проверка префикса 6D38 до входа AF43 на исходных байтах ACTION."""
import json
from random import Random

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers


def check():
    baseline = flat_action()
    assert bytes(baseline[0xA795:0xA82D]) == bytes(151) + b'\xff'
    rng = Random(0x6D38)
    counts = dict(disabled=0, marker=0, reset=0, advance=0)
    for serial in range(4096):
        memory = list(baseline)
        enable = serial & 255
        ttl = (serial >> 4) & 255
        stop_slot = (serial >> 1) % 9
        effect = 0xA795 + 18 * stop_slot
        stack = 0xBFFE
        memory[stack:stack + 2] = [0xFF, 0x3F]
        memory[0x6D39], memory[0x6D3D] = enable, ttl
        state = ((serial >> 5) & 127) + 1 if stop_slot < 8 and serial & 1 else 0xFF
        memory[effect + 7] = state
        if stop_slot < 8:
            memory[effect + 12] = (serial >> 2) & 255
            memory[effect + 13] = rng.randrange(256)

        def put(buf, addr, value):
            buf[addr:addr + 2] = [value & 255, (value >> 8) & 255]

        def get(buf, addr):
            return buf[addr] | buf[addr + 1] << 8

        for addr in (effect, effect + 2, effect + 4, effect + 8, effect + 10,
                     effect + 14, 0xE5ED, 0xE5B3, 0xE5D2):
            if addr < 0xA82D or addr > 0xC000:
                put(memory, addr, rng.randrange(65536))
        wanted = memory.copy()
        destination = 0x3FFF
        outcome = 'disabled'
        if enable:
            wanted[0x6D3D] = (ttl - 1) & 255
            if ttl == 1:
                wanted[0x6D39] = 0
            outcome = 'marker'
            if state < 128:
                destination = 0xAF43
                wanted[effect + 7] -= 1
                for offset, target, movement in ((4, 0xAF69, 0xE5ED), (0, 0xAF48, 0xE5B3), (2, 0xAF56, 0xE5D2)):
                    value = get(memory, effect + offset)
                    put(wanted, target, value)
                    put(wanted, effect + offset, value - get(memory, movement))
                phase = (memory[effect + 12] - 1) & 255
                if phase:
                    outcome = 'advance'
                    cursor = get(memory, effect + 8) + get(memory, effect + 14)
                else:
                    outcome = 'reset'
                    phase = memory[effect + 13]
                    cursor = get(memory, effect + 10)
                wanted[effect + 12] = phase
                put(wanted, effect + 8, cursor)
                put(wanted, 0x6DD2, stack)
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': 0x6D38, 'SP': stack}, None, False)
        for _ in range(150):
            if sim.registers[24] in (0xAF43, 0x3FFF):
                break
            sim.run()
        assert sim.registers[24] == destination, serial
        assert sim.registers[12] == stack + (2 if destination == 0x3FFF else 0), serial
        if destination == 0xAF43:
            assert sim.registers[8:12] == [effect >> 8, effect & 255, 0x6D, 0xD1], serial
        assert memory == wanted, serial
        counts[outcome] += 1
    assert all(counts.values()), counts
    return dict(passed=True, total_cases=sum(counts.values()), outcomes=counts,
                whole_procedure_proved=False, assembly_executed=False, native_execution=False)


if __name__ == '__main__':
    report = check()
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionVisualEffectWalkVerification.json').write_text(payload, encoding='utf-8')
    print(payload)
