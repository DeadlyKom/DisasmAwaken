"""Точное изменение R у двух читателей предела количества и общего входа.

Документация: ../../../Docs/MembershipFlags.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckMembershipFlags import ROOT, Simulator, get_registers
from skoolkit.simutils import A,F,B,C,D,E,H,L,SP,PC,R,T


def main():
    # Проверка обоих исходных фрагментов LANG по физическим секторам оригинального диска.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(row for row in manifest['entries'] if row['slot'] == 5)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    assert source[0x577:0x58A] == bytes.fromhex('118E98E12600193E7FCB7E28023E015F1600C9')
    assert source[0x5BB:0x5C1] == bytes.fromhex('11F698C37AC5')
    memory = bytearray(65536)
    memory[0xC000:0xC000+len(source)] = source
    cpu = Simulator(memory)
    counts = Counter()
    # Проверка каждого начального R на обеих ветвях бита, с индексными и адресными границами.
    for start,base,clear_m1 in ((0xC577,0x988E,11),(0xC5BB,0x98F6,12),
                               (0xC57A,0xA200,10),(0xC57A,0xFFFF,10)):
        for index in (0,1,255):
            for value in (0,1,127,128,255):
                for refresh in range(256):
                    initial = get_registers(dict(PC=start,SP=0x7FFA,HL=0x1357,DE=base,
                        BC=0x36C9,AF=0x5A00|(refresh^value),R=refresh,IX=0x2468,IY=0x5C3A,
                        **{'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF}),None,False)
                    cpu.registers[:] = initial
                    memory[0x7FFA:0x7FFE] = bytes((index,0xE3,255,63))
                    address = (base+index)&65535
                    memory[address] = value
                    before = memory.copy()
                    cpu.run(start=start,stop=0x3FFF)
                    expected = initial.copy()
                    result = 1 if value&128 else 127
                    flags = 0x10|(value&0xA8)|(0 if value&128 else 0x44)|int(base+index>65535)
                    expected[A],expected[F],expected[D],expected[E] = result,flags,0,result
                    expected[H],expected[L] = address>>8,address&255
                    expected[SP],expected[PC] = 0x7FFE,0x3FFF
                    m1 = clear_m1+int(bool(value&128))
                    expected[R] = (refresh&128)|((refresh+m1)&127)
                    assert all(cpu.registers[i] == expected[i] for i in range(len(initial)) if i != T),(start,base,index,value,refresh)
                    assert memory == before
                    counts[hex(start)+'_'+hex(base)] += 1
    assert sum(counts.values()) == 15360
    report = dict(passed=True,method='original_equipment_limit_all_initial_refresh_values',
        original_disk_sha256=manifest['sha256'],source_sha256=sha256(source).hexdigest(),
        cases_by_entry_and_base=dict(counts),total_cases=sum(counts.values()),
        initial_R_values=256,R_bit7_preserved=True,R_low7_wrap_checked=True,
        input_indices=[0,1,255],input_bytes=[0,1,127,128,255],
        M1_for_bit7_clear={'C577':11,'C5BB':12,'C57A':10},
        M1_for_bit7_set={'C577':12,'C5BB':13,'C57A':11},
        all_registers_except_T_and_entire_RAM_checked=True,
        original_return_word_and_consumed_index_unchanged=True,
        arbitrary_base_word_wrap_checked_at_FFFF=True,
        full_input_cartesian_product_proved=False,arbitrary_stack_addresses_proved=False,
        irq_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/EquipmentLimitRefreshVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('15360 случаев, точные R и все регистры кроме T, вся RAM без изменений.')


if __name__ == '__main__':
    main()
