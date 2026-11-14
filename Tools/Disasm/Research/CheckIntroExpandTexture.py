"""Полное расширение 64 строк, все добавки IXL, физические банки и точный R.

Документация: ../../../Docs/IntroGeneratedEffects.md#разворачивание-строк-и-добавка-ixl
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
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_text(encoding='utf-8'))
    entry = next(row for row in manifest['entries'] if row['slot'] == 3)
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    code = bytes(flat[0x6729:0x6757])
    assert code == disk[entry['offset']+0x429:entry['offset']+0x457]
    texture = bytes((i*73+(i>>6)*19)&255 for i in range(4096))
    assert set(texture) == set(range(256))
    cases = 0
    flags = Counter()
    profiles = [(bias,texture) for bias in range(256)]
    profiles += [(bias,bytes([value])*4096) for bias,value in ((0,0),(0,255),(1,255),(255,0),(255,1),(128,128))]
    for bias,source in profiles:
        banks = [bytearray([0xA0+i]*0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[4][:4096] = source
        memory = RecordedBanks(banks=banks,out7ffd=17)
        memory[0x5FFE],memory[0x5FFF] = 255,63
        expected = [bank.copy() for bank in memory.banks]
        # Расчёт независимых 64-байтовых строк, каждая повторяется четыре раза.
        expanded = bytes(value for row in range(64) for repeat in range(4)
                         for value in ((x+bias)&255 for x in source[row*64:row*64+64]))
        expected[2][:] = expanded
        expected[5][0x1FFC:0x1FFE] = bytes.fromhex('2e67')
        initial = get_registers(dict(PC=0x6729,SP=0x5FFE,AF=0xA55A,HL=0x1357,DE=0x2468,BC=0x369C,
            IX=0xAB00|bias,IY=0x5C3A,I=cases&255,R=cases&255,
            **{'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),
            {'im':cases%3,'iff':cases&1},False)
        wanted = list(initial)
        final_flags = 0x10 | int(source[-1]+bias >= 256)
        wanted[:8] = [0x11,final_flags,0x7F,0xFD,0xC0,0,0xC0,0xC0]
        wanted[PC],wanted[SP] = 0x3FFF,0x6000
        wanted[R] = (initial[R]&128)|((initial[R]+54096)&127)
        cpu = Simulator(memory)
        cpu.registers[:] = initial
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.writes = []
        memory.recording = True
        cpu.run(0x6729,0x3FFF)
        memory.recording = False
        # Проверка всех регистров кроме времени и точного физического набора записей.
        assert all(cpu.registers[i] == wanted[i] for i in (*range(25),26,27)),(bias,source[-1])
        assert memory.banks == expected,(bias,'RAM')
        writes = Counter((2,i,value) for i,value in enumerate(expanded))
        writes.update(((5,0x1FFC,0x2E),(5,0x1FFD,0x67)))
        assert Counter(memory.writes) == writes,(bias,'writes')
        assert ports.writes == [(0x7FFD,0x14),(0x7FFD,0x11)] and memory.o7ffd == 0x11
        flags[final_flags] += 1
        cases += 1
    report = dict(passed=True,total_cases=cases,all_256_IXL_values=True,all_source_byte_values_in_each_of_256_pattern_profiles=True,
                  additional_constant_boundary_cases=6,original_code_sha256=sha256(code).hexdigest(),
                  output_bytes=16384,each_output_byte_written_once=True,CPU_stack_writes=2,
                  exact_registers_including_R_except_T=True,all_physical_banks_and_write_counts_compared=True,
                  final_HL=0xC0C0,final_DE=0xC000,final_BC=0x7FFD,final_A=0x11,
                  F_counts=dict(flags),M1_per_case=54096,
                  all_joint_4096_byte_source_inputs_exhausted=False,IRQ_executed=False,
                  assembly_executed=False,native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroExpandTextureVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
