"""Создание альтернативной записи с настоящим эффектом страницы 3."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionSpawnTemplateLoop import signed, word
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    streams = (0xEBFC, 0xEBFF, 0xEBE4, 0xEBE7, 0xEBF0, 0xEBEA, 0xEBF3, 0xEBDB)
    cases = 0
    for fixture, mode, free, ttl in product(range(32), (0, 1), range(9), (0, 26, 255)):
        memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=16)
        record = bytearray((offset * 37 + fixture) & 255 for offset in range(64))
        record[:2] = bytes((0, 128))
        record[24] = 0
        put(memory, 0xA100, record)
        put(memory, 0xA140, (128, 128))
        memory[0x79DE], memory[0x7A6A] = mode * 32, mode * 6
        for slot in range(8):
            memory[0xA795 + slot * 18 + 7] = int(slot != free)
        memory[0x6D39], memory[0x6D3D] = 0, ttl
        states = {}
        for stream in streams:
            seed = (fixture * 719 + mode * 2953 + stream * 173) & 65535
            fold = (fixture + ttl + stream) & 255
            put(memory, stream, seed.to_bytes(2, 'little') + bytes((fold,)))
            states[stream] = (seed, fold)

        def advance(stream):
            result = step(*states[stream])
            states[stream] = result['word'], result['fold']
            return result['word']

        random = advance(0xEBFC)
        model = ((random ^ (random >> 8)) & 28) + 64 + mode * 32
        coords = [signed(advance(0xEBFF)) // 2 for _ in range(3)][::-1]
        record[:6] = b''.join((coord & 65535).to_bytes(2, 'little') for coord in coords)
        record[6:8] = bytes((model, 0))
        delta = advance(0xEBE4)
        record[8] = ((delta >> 8) + (-1 if delta & 128 else 1) * (delta & 3)) & 255
        record[9] = advance(0xEBE7) & 31
        record[11:13] = bytes((255, 0))
        record[13:15] = states[0xEBDB][0].to_bytes(2, 'little')
        record[15:19] = bytes((100, 32, flat[0x7DE4], mode * 6))
        advance(0xEBF0)
        advance(0xEBEA)
        record[19:24] = bytes((min((advance(0xEBF3) & 255) | flat[0x7E07], flat[0x7E09] - 1),
                               0, 255, record[10], 0))
        states[0xEBDB] = states[0xEBDB][0], 0
        advance(0xEBDB)
        record[32:34] = b'\xff\xff'
        record[36] = 0
        effect = bytearray(memory[0xA795:0xA82D])
        pointer = word(flat, 0x9E00 + model)
        if free < 8:
            effect[free * 18:(free + 1) * 18] = record[:6] + bytes(
                (objects[pointer - 0xC000 + 1], 26, 0, 216, 0, 216, 1, 13, 192, 0, 12, 12))

        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x79CC, 'SP': 0xBFFE}, None, False)
        sim.registers[15] = fixture * 7
        sample = None
        for _ in range(1800):
            pc = sim.registers[PC]
            if pc == 0x7E89:
                break
            if 0x7A96 <= pc < 0x7E89 and memory[pc:pc + 2] == [0xED, 0x5F]:
                sample = refresh(sim.registers[15], 2)
            sim.run()
        context = (fixture, mode, free, ttl)
        assert sim.registers[PC] == 0x7E89 and sim.registers[SP] == 0xBFFE, context
        record[24] = (sample + 1) & 15
        actual = bytes(memory[0xA100:0xA140])
        assert actual == record, (context, [(n, a, b) for n, (a, b) in enumerate(zip(actual, record)) if a != b])
        assert bytes(memory[0xA795:0xA82D]) == effect, context
        for address, (value, fold) in states.items():
            assert bytes(memory[address:address + 3]) == value.to_bytes(2, 'little') + bytes((fold,)), context
        assert (memory[0x6D39], memory[0x6D3D]) == (1, max(26, ttl)), context
        assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16)] and memory.o7ffd == 16, context
        cases += 1

    report = dict(passed=True, total_cases=cases, whole_object_and_effect_pool_compared=True,
                  all_eight_stream_states_compared=True, stops_before_final_header=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateRecordVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
