"""Чистые бинарные операторы LANG, RAM, флаги и M1 на исходных байтах.

Документация: ../../../Docs/ScriptLanguage.md#собственные-эффекты-простых-бинарных-операторов
"""
from pathlib import Path
from hashlib import sha256
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from CheckGeometryReturnEntries import Memory


def subtract_flags(left, right):
    value = (left-right) & 65535
    return (2 | ((value >> 8) & 0xA8) | (0x40 if value == 0 else 0)
            | (0x10 if (left ^ right ^ value) & 0x1000 else 0)
            | (4 if (left ^ right) & (left ^ value) & 0x8000 else 0)
            | int(left < right))


def main():
    m = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(e for e in m['entries'] if e['slot'] == 5)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    # Проверка физических байтов перед запуском исходных процедур.
    assert sha256(disk).hexdigest() == m['sha256']
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    assert sha256(source).hexdigest() == entry['sectors_sha256']
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex('320070')
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    memory[0xC000:0xC000+len(source)] = source
    memory[0x7FFE:0x8000] = bytes((255,63))
    cpu = Simulator(memory)
    initial = get_registers({'SP':0x7FFE, 'HL':0x1357, 'AF':0x47AD,
        '^HL':0x2468, '^DE':0x369C, '^BC':0x58BE, '^AF':0x69CF,
        'IX':0x789A, 'IY':0x8ABC}, None, False)
    entries = ((0xC3D5,'equal'),(0xC49C,'less'),(0xC4A6,'greater'),
        (0xC4BC,'not_less'),(0xC4B1,'not_greater'),(0xC488,'add'),
        (0xC491,'subtract'),(0xC4C6,'and'),(0xC4CD,'or'),(0xC4D4,'right'))
    counts = {}
    for address, name in entries:
        count = 0
        for profile in range(4):
            for left in range(65536):
                right = (left, (left+1)&65535, (left-1)&65535, left^65535)[profile]
                r = cpu.registers
                r[:] = initial
                r[2],r[3],r[4],r[5] = right>>8,right&255,left>>8,left&255
                r[0],r[1],r[15] = left&255,(left>>8)^right&255,(left^right)&255
                expected = list(r)
                # Расчёт результата и флагов независимо от исполнения инструкций.
                if name in ('equal','less','greater','not_less','not_greater'):
                    result = int({'equal':left==right,'less':left<right,'greater':left>right,
                        'not_less':left>=right,'not_greater':left<=right}[name])
                    hl, flags = (left-right)&65535, subtract_flags(left,right)
                    cost = (6 if left==right else 8) if name=='equal' else (
                        (6 if left<right else 8) if name in ('less','not_less') else
                        (6 if left==right else 7 if left<right else 9) if name=='greater' else
                        (6 if left<right else 7 if left==right else 9))
                elif name=='add':
                    total = left+right
                    result, hl = min(total,65535), 0x1357
                    flags = ((r[1]&0xC4) | ((total>>8)&0x28)
                        | (0x10 if (left&4095)+(right&4095)>4095 else 0) | int(total>65535))
                    cost = 5+int(total>65535)
                elif name=='subtract':
                    result, hl, flags = max(left-right,0),0x1357,subtract_flags(left,right)
                    cost = 7+int(left<right)
                elif name in ('and','or'):
                    result = left&right if name=='and' else left|right
                    low = result&255
                    hl = 0x1357
                    flags = ((low&0xA8) | (0x40 if low==0 else 0)
                        | (4 if low.bit_count()%2==0 else 0) | (0x10 if name=='and' else 0))
                    expected[0] = low
                    cost = 7
                else:
                    result,hl,flags,cost = right,0x1357,r[1],3
                expected[4],expected[5],expected[6],expected[7] = result>>8,result&255,hl>>8,hl&255
                expected[1],expected[12],expected[24] = flags,0x8000,0x3FFF
                expected[15] = (r[15]&128)|((r[15]+cost)&127)
                memory.writes.clear()
                memory.recording = True
                cpu.run(address,0x3FFF)
                memory.recording = False
                assert not memory.writes
                assert all(r[i]==expected[i] for i in range(len(expected)) if i!=25), (name,left,right,list(r),expected)
                assert memory[0x7FFE:0x8000] == bytes((255,63))
                count += 1
        counts[name] = count
    report = dict(passed=True,method='original_simple_operators_against_word_and_flag_formulas',
        cases_by_operator=counts,total_cases=sum(counts.values()),
        right_profiles=['equal','left_plus_one_wrapped','left_minus_one_wrapped','complement'],
        full_left_right_AF_R_cartesian_product_checked=False,
        exact_registers_except_T_checked=True,no_own_RAM_writes=True,
        original_return_word_preserved=True,CPU_write_watch_positive_control=True,
        physical_disk_and_sector_hashes_checked=True,
        arbitrary_stack_addresses_checked=False,multiply_checked=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SimpleOperatorsVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()

