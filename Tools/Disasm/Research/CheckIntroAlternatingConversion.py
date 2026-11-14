"""Преобразование после BuildTextureLookup, без исполнения самого построителя.

Документация: ../../../Docs/IntroGeneratedEffects.md#чередующееся-преобразование-текстуры
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT, original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckScreenUpdate import PortTrace
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def main():
    flat = original_memory()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text(encoding='utf-8'))
    entry = next(row for row in manifest['entries'] if row['slot'] == 3)
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    code = bytes(flat[0x6640:0x6663])
    assert code == disk[entry['offset']+0x340:entry['offset']+0x363]
    for start, end in ((0x6A0D,0x6A13),(0x6757,0x6763)):
        assert bytes(flat[start:end]) == disk[entry['offset']+start-0x6300:entry['offset']+end-0x6300]
    profiles = [bytes((i*73+(i>>8)*19+bias)&255 for i in range(16384)) for bias in range(256)]
    assert all(set(source[parity::2]) == set(range(256)) for source in profiles for parity in (0,1))
    flags = Counter()
    for case, source in enumerate(profiles):
        banks = [bytearray([0xA0+i]*0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][0x2000:] = source[:0x2000]
        banks[1][:0x2000] = source[0x2000:]
        memory = RecordedBanks(banks=banks, out7ffd=0x11)
        memory[0x5FFE], memory[0x5FFF] = 255, 63
        expected = [bank.copy() for bank in memory.banks]
        # Расчёт результата из снимка источника до начала перекрывающихся записей.
        output = bytes(value >> 2 if i % 2 == 0 else value for i, value in enumerate(source))
        expected[2][:] = output
        expected[6][:] = output
        expected[5][0x1FFC:0x1FFE] = bytes.fromhex('6066')
        initial = get_registers(dict(PC=0x6640, SP=0x5FFE, AF=0xA55A, HL=0x1357,
            DE=0x2468, BC=0x369C, IX=0x6400, IY=0x5C29, I=case, R=case,
            **{'^AF':0xDEF0, '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC}),
            {'im':case%3, 'iff':case&1}, False)
        wanted = list(initial)
        last_sum = (0x16+output[-1])&255
        final_flags = ((source[-2]>>1)&1) | (last_sum&8) | ((last_sum&2)<<4)
        wanted[:8] = [0x16, final_flags, 0, 0, 0, 0, 0xC0, 0]
        wanted[PC], wanted[SP] = 0x3FFF, 0x6000
        wanted[R] = (initial[R]&128)|((initial[R]+139661)&127)
        cpu = Simulator(memory)
        cpu.registers[:] = initial
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.writes = []
        memory.recording = True
        cpu.run(0x6640, 0x3FFF)
        memory.recording = False
        # Проверка регистров, всех банков и каждой физической записи.
        assert all(cpu.registers[i] == wanted[i] for i in (*range(25),26,27)), (case, [(i,wanted[i],cpu.registers[i]) for i in range(25) if wanted[i]!=cpu.registers[i]])
        assert memory.banks == expected, (case, 'RAM')
        writes = Counter((bank,i,value) for bank in (2,6) for i,value in enumerate(output))
        writes.update(((5,0x1FFC,0x60),(5,0x1FFD,0x66)))
        assert Counter(memory.writes) == writes, (case,'writes')
        assert ports.writes == [(0x7FFD,0x16)] and memory.o7ffd == 0x16
        flags[final_flags] += 1
    report = dict(passed=True, total_cases=len(profiles), entry=0x6640,
        original_code_sha256=sha256(code).hexdigest(), all_byte_values_in_even_and_odd_positions=True,
        all_physical_banks_and_write_counts_compared=True, exact_registers_except_T=True,
        M1=139661, F_counts=dict(flags), CPU_stack_writes=2,
        BuildTextureLookup_executed=False, IRQ_executed=False,
        all_joint_source_inputs_exhausted=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/IntroAlternatingConversionVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
