"""ACAB..ACD5, шесть реальных межбанковых вызовов без подмены производителя очереди."""
from collections import Counter
from itertools import product
import json

from CheckActionTextQueueCalls import Memory, Ports, payload
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsTextQueue import QUEUE, PRODUCER, insert


def main():
    memory = Memory(banks=[[0xA5] * 16384 for _ in range(8)], out7ffd=16)
    action = payload(17)
    for index, value in enumerate(action):
        memory[0x6000 + index] = value
    for index, value in enumerate(action[0x23D:0x21CC]):
        memory[0x6000 + index] = value
    for slot, offset in ((22, 0), (23, 0x1ADE)):
        raw = payload(slot)
        memory.banks[1][offset:offset + len(raw)] = raw
    assert bytes(memory[0xACD6:0xACEA]) == b'Status: \n\rDeads: \n\r\n'
    baseline = [list(bank) for bank in memory.banks]
    simulator = Simulator(memory)
    ports = Ports(memory)
    simulator.set_tracer(ports)
    counts = Counter()
    triples = ((0, 0, 0), (1, 2, 3), (255, 255, 255), (127, 128, 129),
               (10, 100, 250), (255, 0, 1), (3, 2, 1), (0, 255, 0))
    for head, mode, values, flags in product(range(17), range(4), triples, (0, 255)):
        memory.recording = False
        for bank, original in zip(memory.banks, baseline):
            bank[:] = original
        serial = counts.total()
        memory.out7ffd(serial % 32)
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        memory[0x9BCD], memory[0x9BCF], memory[0x9BCE] = values
        for index in range(16):
            kind = (1, 0x80, 1 if index & 1 else 0x80, 0)[mode]
            memory.banks[1][0x2C80 + 2 * index] = kind
            memory.banks[1][0x2C81 + 2 * index] = (serial + index) & 255
        cursor = QUEUE + 2 * head
        memory.banks[1][0x2C5D:0x2C5F] = [cursor & 255, cursor >> 8]
        expected = [list(bank) for bank in memory.banks]
        virtual = {address: memory.banks[1][address - 0xC000] for address in range(QUEUE, QUEUE + 34)}
        virtual[PRODUCER], virtual[PRODUCER + 1] = cursor & 255, cursor >> 8
        queue_writes = []
        for value in (0xACD6, 0x0200 | values[0], 0xACDF, 0x0200 | values[1], 0x0200 | values[2], 0xACE8):
            result = insert(virtual, value)
            counts['accepted_items' if result['accepted'] else 'dropped_items'] += 1
            for address, byte in result['writes']:
                virtual[address] = byte
                expected[1][address - 0xC000] = byte
                queue_writes.append((1, address - 0xC000, byte))
        initial = get_registers({'PC': 0xACAB, 'SP': 0xBFFE, 'AF': 0x5600 | flags,
                                 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                                 '^AF': 0x6900 | (flags ^ 0xA5), '^HL': 0x1234,
                                 '^DE': 0x5678, '^BC': 0x9ABC, 'IX': 0xABCD, 'IY': 0x5C3A}, None, False)
        initial[14], initial[26], initial[27] = serial & 255, serial & 1, serial % 3
        wanted = list(initial)
        wanted[0], wanted[4], wanted[5], wanted[16] = 16, 2, values[2], 17
        wanted[PC], wanted[SP] = 0x3FFF, 0xC000
        simulator.registers[:] = initial
        memory.writes, memory.recording, ports.events = [], True, []
        for _ in range(1600):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('нет возврата', head, mode, values))
        memory.recording = False
        compared = (*range(13), 14, *range(16, 24), PC, 26, 27)
        assert all(wanted[index] == simulator.registers[index] for index in compared)
        # Проверка всей RAM вне восемнадцатибайтовой временной рамки, её значения отдельно не объявляются доказанными.
        expected[2][0x3FEC:0x3FFE] = memory.banks[2][0x3FEC:0x3FFE]
        assert memory.banks == expected
        writes = [write for write in memory.writes if write[0] != 2 or not 0x3FEC <= write[1] < 0x3FFE]
        assert writes == queue_writes
        assert min(offset for bank, offset, _ in memory.writes if bank == 2) == 0x3FEC
        assert ports.events == [(0x7FFD, page) for _ in range(6) for page in (17, 16)]
        assert memory.o7ffd == 16
        counts['cases'] += 1
    result = dict(passed=True, total_cases=counts['cases'], outcomes=dict(counts),
                  actual_queue_and_banked_wrappers_executed=True, all_ram_outside_stack_checked=True,
                  exact_registers_except_R_and_T=True, maximum_stack_bytes=18,
                  temporary_stack_values_independently_checked=False, runtime_caller_found=False,
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionDiagnosticQueueVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
