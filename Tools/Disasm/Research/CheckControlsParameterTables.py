"""Полный DE10 с настоящей цепочкой, числовая модель пятнадцати записей и девяти строк."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckControlsWordRandom import reference as random_step
from CheckControlsCircleSpan import add_flags
from CheckActionRegionType import reference as region_type
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def indices(first,second,control):
    folded = ((first>>8)^(first&255)^(second>>8)^(second&255))&7
    region,_,region_cost = region_type(first>>8,first&255)
    x,y = first,second
    for _ in range(control+1):
        x,y,output,_ = random_step(x,y)
    inverse = output^255
    return dict(hash_index=max(folded-1,0),folded=folded,region=region,
        h=4 if region==3 else inverse>>6,c=(inverse>>2)&15,x=x,y=y,
        cost=41+region_cost+34*(control+1)+int(folded==0)+2*int(region==3))


def seed_writes(first,second,control,bc):
    # Расчёт реальных рамок при SP=BFFC на входе вложенного BuildSeededIndices.
    outside = int(region_type(first>>8,first&255)[0]==3)
    writes = [(0xBFFB,bc>>8),(0xBFFA,bc&255),
        (0x9B15,first&255),(0x9B16,first>>8),(0x9B17,second&255),(0x9B18,second>>8),
        (0xBFF9,0xDE),(0xBFF8,0xB4)]
    x,y = first,second
    for iteration in range(control+1):
        x,y,_,_ = random_step(x,y)
        writes += [(0xBFF9,0xDE),(0xBFF8,0xC0),(0xBFF7,(control+1-iteration)&255),(0xBFF6,outside),
            (0x9B15,x&255),(0x9B16,x>>8),(0x9B17,y&255),(0x9B18,y>>8)]
    return writes


def main():
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original = base_memory()
    original[0x6000:0xC000] = source[:0x6000]
    original[0x6000:0x7F8F] = source[0x23D:0x21CC]
    # Проверка реальных кодов наклона и ненулевых степеней двойки исходной таблицы.
    coefficients = [original[0xDF64+3*i:0xDF67+3*i] for i in range(15)]
    assert all(code in (1,2,254) and shift in (1,2,4,8) for _,code,shift in coefficients)
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    covered_pairs = set()
    total_calls = 0

    def check(first,second,control,kind):
        nonlocal touched,total_calls
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0x9BC1:0x9BC6] = [first&255,first>>8,second&255,second>>8,control]
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        initial = get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':(first+73*second)&65535,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,
            'IY':0x5C3A,'SP':0xBFFE,'PC':0xDE10},None,False)
        initial[14],initial[15],initial[26],initial[27] = control,second&255,control&1,first%3
        result = indices(first,second,control)
        h = result['h'] if result['hash_index'] else 3
        c = result['c']
        offset = h*16
        writes = [(0xBFFD,0xDE),(0xBFFC,0x1D)]+seed_writes(first,second,control,(initial[2]<<8)|initial[3])
        writes += [(0x688B,result['hash_index']),(0xBFFD,0),(0xBFFC,offset),
                   (0xBFFB,initial[2]),(0xBFFA,c)]
        cost = (result['cost']+block_cost(0xDE10,0xDE23)+int(result['hash_index']==0)
                +block_cost(0xDE25,0xDE3F))
        # Расчёт всех пятнадцати полей через наклон, арифметический сдвиг и две аддитивные таблицы.
        for i,(base,code,shift_mask) in enumerate(coefficients):
            shift = shift_mask.bit_length()-1
            slope = 0 if code==1 else 1 if code==2 else -1
            scaled = (slope*c)//(1<<shift)
            intermediate = (scaled+base)&255
            template = original[0xDF25+offset+i]
            value = (intermediate+template)&255
            field_flags = add_flags(intermediate,template)
            writes.append((0x9BA4+i,value))
            cost += block_cost(0xDE3F,0xDE45)
            if code==254:
                cost += block_cost(0xDE45,0xDE4A)+block_cost(0xDE4A,0xDE4C)+block_cost(0xDE4C,0xDE4F)+block_cost(0xDE4F,0xDE51)
            else:
                cost += block_cost(0xDE51,0xDE54)
                if code==2:
                    cost += block_cost(0xDE54,0xDE56)+block_cost(0xDE56,0xDE59)
            cost += (block_cost(0xDE59,0xDE5B)+(shift+1)*block_cost(0xDE5B,0xDE5F)
                     +shift*block_cost(0xDE5F,0xDE63)+block_cost(0xDE63,0xDE78))
        last_field,last_field_flags = value,field_flags
        # Расчёт девяти исходных строк, первая не получает добавку C, остальные получают её.
        for i in range(9):
            base = original[0xDEDC+offset+i]
            value = (base+(c if i else 0))&255
            writes.append((0x7B97+6*i,value))
        cost += block_cost(0xDE78,0xDE8E)+8*block_cost(0xDE8E,0xDE99)+block_cost(0xDE99,0xDE9A)
        wanted = list(initial)
        wanted[0:8] = [value,(add_flags(base,c)&0xC4)|0x28,0,c,0x56,0x78,0x12,0x34]
        wanted[8:10] = [0x9B,0xB3]
        wanted[16:24] = [last_field,last_field_flags,0,6,(0xDEDC+offset+9)>>8,
                         (0xDEDC+offset+9)&255,0x7B,0xCD]
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],cost)
        expected = list(memory)
        for address,new_value in writes:
            expected[address] = new_value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(25000):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',first,second,control))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (first,second,control,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (first,second,control,
            [(i,a,b) for i,(a,b) in enumerate(zip(memory,expected)) if a!=b][:8])
        touched = {address for address,_ in writes}
        counts[kind] += 1
        covered_pairs.add((h,c))
        total_calls += control+1

    # Поиск малых независимых наборов зерна для всех реализуемых областей и индексных сочетаний.
    for first in (0x4A36,0x4734,0x4738,0):
        seen = set()
        for second in range(65536):
            result = indices(first,second,0)
            h = result['h'] if result['hash_index'] else 3
            key = (h,result['c'],result['hash_index']==0)
            if key not in seen:
                check(first,second,0,'all_table_cases')
                seen.add(key)
    print('Parameter table combinations complete',flush=True)
    # Проверка каждого числа шагов в каждой исходной координатной области.
    for first in (0x4A36,0x4734,0x4738,0):
        for control in range(256):
            check(first,(first+25173*control)&65535,control,'all_counts_by_region')
    assert len(covered_pairs)==80
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        all_table_h_c_pairs=len(covered_pairs),calls_to_original_random=total_calls,
        real_helpers_without_stubs=True,coefficient_stride=3,coefficient_records=15,
        overlapping_h4_template_preserved=True,final_exx_register_bank_checked=True,
        exact_registers_flags_r_and_sp=True,every_ram_byte_and_write_checked=True,
        all_input_combinations_exhausted=False,game_field_names_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsParameterTablesVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
