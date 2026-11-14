"""Точный R при первом совпадении типа в четырёхбайтовой строке и при отказе.

Документация: ../../../Docs/MembershipFlags.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckMembershipFlags import ROOT, Simulator, get_registers, compare_flags
from skoolkit.simutils import A,F,D,E,H,L,SP,PC,R,T


def main():
    # Проверка исходных входов корабля и скриммера по полным секторам LANG.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(row for row in manifest['entries'] if row['slot'] == 5)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    for first,last in ((0xC558,0xC577),(0xC5B2,0xC5BB)):
        code = [row for area in flow if area['name'] == 'Text'
                for row in area['instructions'] if first <= row['address'] < last]
        raw = b''.join(bytes.fromhex(row['hex']) for row in code)
        assert len(raw) == last-first and raw == source[first-0xC000:last-0xC000]
        assert all(row['slot'] == 5 for row in code)
    memory = bytearray(65536)
    memory[0xC000:0xC000+len(source)] = source
    cpu = Simulator(memory)
    common_m1 = [10,13,16,17,19]
    counts,positions = Counter(),Counter()
    aliases = 0
    # Проверка каждого исходного R при четырёх первых совпадениях и полном несовпадении.
    for start,base,selector,prefix_m1 in ((0xC558,0x9400,0x9849,2),
            (0xC5B2,0x9484,0x984A,3),(0xC55E,0xA000,None,0),(0xC55E,0xFFFF,None,0)):
        for index in (0,1,241,255):
            for wanted in (0,128,255):
                for slot in range(5):
                    for refresh in range(256):
                        initial = get_registers(dict(PC=start,SP=0x7FFA,DE=base,
                            AF=(wanted<<8)|(refresh^wanted),R=refresh,BC=0x36C9,
                            IX=0x2468,IY=0x5C3A,
                            **{'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF}),None,False)
                        cpu.registers[:] = initial
                        memory[0x7FFA:0x7FFE] = bytes((index,0xE3,255,63))
                        if selector is not None:
                            memory[selector] = wanted
                        address = (base+4*index)&65535
                        row = [(wanted+1)&255]*4
                        if slot < 4:
                            row[slot] = wanted
                        for offset,value in enumerate(row):
                            memory[(address+offset)&65535] = value
                        actual_wanted = memory[selector] if selector is not None else wanted
                        found = row.index(actual_wanted) if actual_wanted in row else 4
                        if selector is not None and selector in [(address+i)&65535 for i in range(4)]:
                            aliases += 1
                        before = memory.copy()
                        cpu.run(start=start,stop=0x3FFF)
                        expected = initial.copy()
                        result_address = (address+(found+1 if found < 3 else 3))&65535
                        expected[A],expected[F] = actual_wanted,compare_flags(actual_wanted,row[min(found,3)])
                        expected[D],expected[E] = 0,int(found == 4)
                        expected[H],expected[L] = result_address>>8,result_address&255
                        expected[SP],expected[PC] = 0x7FFE,0x3FFF
                        m1 = prefix_m1+common_m1[found]
                        expected[R] = (refresh&128)|((refresh+m1)&127)
                        assert all(cpu.registers[i] == expected[i] for i in range(len(initial)) if i != T),(start,index,wanted,slot,refresh,found)
                        assert memory == before
                        counts[hex(start)+'_'+hex(base)] += 1
                        positions[str(found)] += 1
    assert sum(counts.values()) == 61440 and aliases == 3840
    result = dict(passed=True,method='original_four_type_match_all_initial_refresh_values',
        original_disk_sha256=manifest['sha256'],source_sha256=sha256(source).hexdigest(),
        total_cases=sum(counts.values()),cases_by_entry_and_base=dict(counts),
        cases_by_first_match_or_absence=dict(positions),selector_table_alias_cases=aliases,
        initial_R_values=256,R_bit7_preserved=True,R_low7_wrap_checked=True,
        M1_by_first_match_0_1_2_3_or_absence={'C558':[12,15,18,19,21],
            'C5B2':[13,16,19,20,22],'C55E':common_m1},
        all_registers_except_T_and_entire_RAM_checked=True,
        original_return_word_and_consumed_index_unchanged=True,
        wrapped_four_byte_read_at_FFFF_checked=True,
        all_index_value_and_flag_combinations_proved=False,arbitrary_stack_addresses_proved=False,
        irq_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/EquipmentTypeMatchRefreshVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('61440 случаев, точный R всех пяти исходов, включая 3840 наложений таблицы на селектор.')


if __name__ == '__main__':
    main()
