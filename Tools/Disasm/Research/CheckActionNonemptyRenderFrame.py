"""E020: формирование очереди, загрузка узлов, вывод и конечный возврат."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import OUTPUTS
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import EXP, LOG
from ReferenceActionPatchedVector import evaluate


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline[4][:len(objects)] = objects
    baseline[2][0x1100:0x1200] = bytes(value & 255 for value in LOG)
    baseline[2][0x1200:0x1300] = bytes(value >> 8 for value in LOG)
    baseline[2][0x1300:0x1400] = bytes(EXP)
    matrix = ((127, 0, 0), (0, 127, 0), (0, 0, 127))
    paths = Counter()
    cases = 0
    for model, depths, lateral, phases in product(
            (0, 12, 32, 64), ((0x1000,), (0x2000, 0x3000, 0x1000), (0x2200, 0x2200, 0x2200)),
            (0, 0x180, 0x600, -1), ((0, 0, 0), (1, 7, 11))):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)

        def put(address, value):
            memory[address], memory[address + 1] = value & 255, value >> 8

        def word(address):
            return memory[address] | memory[address + 1] << 8

        memory[0x9B81], memory[0x688B] = 1, 0
        for index in range(9):
            put(0x9B00 + 2 * index, 0x7F00 if index % 4 == 0 else 0)
        for address in range(0x9B95, 0x9B98):
            memory[address] = 0
        put(0xBFFE, 0x3FFF)
        order, payloads = [], []
        old_outputs = [word(address) for address in OUTPUTS]
        for index, depth in enumerate(depths):
            pointer = 0xA100 + 64 * index
            vector = (depth // 2 - 64 if lateral == -1 else lateral, 0, depth)
            for offset, value in enumerate(vector):
                put(pointer + 2 * offset, value)
            for offset, value in enumerate((model, *phases)):
                memory[pointer + 6 + offset] = value
            outputs = evaluate(vector, matrix, old_outputs)['outputs']
            old_outputs = outputs
            selected = model + 2 * (outputs[2] >> 8 < 31)
            payload = bytes((int(not (phases[0] | phases[2])), selected, *phases))
            payload += b''.join(value.to_bytes(2, 'little') for value in outputs)
            payloads.append(payload)
            position = next((pos for pos, prev in enumerate(order)
                             if (word_from_payload(payloads[prev]) - outputs[2] - int(prev == 0)) & 32768),
                            len(order))
            order.insert(position, index)
        put(0xA100 + 64 * len(depths), 0x80FF)

        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xE020, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
        loaded, rendered = [], []
        context = (model, depths, lateral, phases)
        for _ in range(500000):
            r = sim.registers
            pc = r[PC]
            if pc == 0x3FFF:
                break
            if pc == 0xE4A6:
                assert memory[0x9BA1] == 14 * order[0] and memory[0x9BA2] == 14 * len(order), context
                for position, index in enumerate(order):
                    pointer = 0x8F00 + 14 * index
                    link = 14 * order[position + 1] if position + 1 < len(order) else 1
                    assert memory[pointer] == link, context
                    assert bytes(memory[pointer + 3:pointer + 14]) == payloads[index], context
            if pc == 0xE4B1:
                assert r[SP] == 0xBFFE and r[6] == 0x8F
                loaded.append(r[7] // 14)
            if pc == 0xE4DB:
                index = loaded[-1]
                assert r[SP] == 0xBFFC and word(0xBFFC) == 0x8F00 + 14 * index
                assert bytes(memory[0x9B8D:0x9B8F]) + bytes(memory[0x9B12:0x9B15]) == payloads[index][:5]
                assert b''.join(word(address).to_bytes(2, 'little') for address in OUTPUTS) == payloads[index][5:]
                rendered.append(index)
            if pc in (0xE4F4, 0xE4FA):
                paths['inside' if pc == 0xE4F4 else 'clipped'] += 1
            sim.run()
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert loaded == rendered == order, (context, order, loaded, rendered)
        paging = [(port, value) for port, value in trace.writes if port == 0x7FFD]
        assert paging == [(0x7FFD, 19), (0x7FFD, 16)] + [(0x7FFD, 20), (0x7FFD, 16)] * (2 * len(order)), context
        assert memory.o7ffd == 16
        paths['nodes'] += len(order)
        cases += 1
    assert paths['inside'] or paths['clipped'], paths
    report = dict(passed=True, total_cases=cases, outcomes=dict(paths),
                  actual_frame_entry_executed=True, original_object_bank_used=True,
                  checked_order_payload_stack_and_paging=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionNonemptyRenderFrameVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


def word_from_payload(payload):
    return int.from_bytes(payload[-2:], 'little')


if __name__ == '__main__':
    main()
