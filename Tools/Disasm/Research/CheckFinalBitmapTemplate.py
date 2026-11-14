"""Исполнение 52-байтовой копии bitmap-шаблона без прерывания временного SP.

Документация: ../../../Docs/FinalCycle.md#договор-копии-bitmapline-без-irq
"""
from collections import Counter
from hashlib import sha256
import json

from CheckFinal import ROOT, Simulator, get_registers, original_memory, screen_offset
from CheckActionParameterActivation import RecordedBanks
from skoolkit.simutils import PC, SP, R


def main():
    template = bytes(original_memory()[0x6247:0x627B])
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_text(encoding='utf-8'))
    entry = next(row for row in manifest['entries'] if row['slot'] == 29)
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert template == disk[entry['offset']+0x247:entry['offset']+0x27B]
    banks = [bytearray((i*73+(i>>8)*19+bank*53)&255 for i in range(0x4000)) for bank in range(8)]
    memory = RecordedBanks(banks=banks,out7ffd=16)
    cpu = Simulator(memory)
    cases = 0

    def check(source1, source2, target_end1, target_end2):
        nonlocal cases
        memory.recording = False
        page = (0,1,7)[cases % 3]
        memory.out7ffd(16+page)
        code = bytearray(template)
        for offset,value in zip((1,14,27,40),(source1,target_end1,source2,target_end2)):
            code[offset:offset+2] = value.to_bytes(2,'little')
        memory.banks[2][4:56] = code
        data1, data2 = bytes(memory[source1:source1+16]), bytes(memory[source2:source2+16])
        expected_banks = [bank.copy() for bank in memory.banks]
        writes = []
        for end,data in ((target_end1,data1),(target_end2,data2)):
            expected_banks[5][end-16-0x4000:end-0x4000] = data
            writes.extend((5,end-16-0x4000+i,value) for i,value in enumerate(data))
        initial = get_registers(dict(PC=0x8004, SP=0x5FFE, AF=0xA55A,
            HL=0x1357, DE=0x2468, BC=0x369C, IX=0xABCD, IY=0x5C3A,
            I=cases & 255, R=cases & 255,
            **{'^AF':0xDEF0, '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC}),
            {'im':cases % 3, 'iff':cases & 1}, False)
        expected = list(initial)
        expected[:10] = [data2[15],data2[14],data2[3],data2[2],data2[5],data2[4],
                         data2[1],data2[0],data2[13],data2[12]]
        expected[18:24] = [data2[9],data2[8],data2[11],data2[10],data2[7],data2[6]]
        expected[PC],expected[SP] = 0x8038,target_end2-16
        expected[R] = (initial[R]&128)|((initial[R]+44)&127)
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        # Проверка последовательного выхода без исполнения первой команды следующего шаблона.
        cpu.run(0x8004,0x8038)
        memory.recording = False
        assert all(cpu.registers[i] == expected[i] for i in (*range(25),26,27)), cases
        assert memory.banks == expected_banks and Counter(memory.writes) == Counter(writes), cases
        assert memory.o7ffd == 16+page, cases
        cases += 1

    # Проверка всех пар физических экранных строк с независимым вычислением адресов Spectrum.
    for source_row in range(192):
        for target_row in range(192):
            source = 0xC000+screen_offset(source_row)
            target = 0x4000+screen_offset(target_row)
            check(source,source+16,target+16,target+32)
    # Проверка независимости операндов половин, включая нечётные адреса и разные строки.
    for pointers in ((0xC000,0xD7F0,0x57F0,0x4020),
                     (0xD7E0,0xC010,0x4010,0x5800),
                     (0xC010,0xC000,0x4010,0x4020),
                     (0xC001,0xC113,0x4011,0x4055)):
        check(*pointers)
    report = dict(passed=True,total_cases=cases,all_192_by_192_bitmap_row_pairs=True,
                  additional_independent_operand_cases=4,original_template_sha256=sha256(template).hexdigest(),
                  exact_all_registers_except_T=True,all_physical_banks_and_write_counts_compared=True,
                  source_banks=[0,1,7],writes_per_case=32,M1_per_case=44,
                  final_SP='second_destination_end_minus_16',external_CPU_SP_not_restored=True,
                  IY_AF_alternate_I_IM_IFF_and_paging_preserved=True,
                  IRQ_executed=False,full_generated_chain_executed=False,
                  assembly_executed=False,native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalBitmapTemplateVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
