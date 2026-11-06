"""Классификатор экранных точек DEF3 и общий хвост отказа DEF0, точный исходный формат кодов."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import cp_flags


def logic_flags(value):
    return (value&0xA8)|(64 if value==0 else 0)|(4 if value.bit_count()%2==0 else 0)


def code(second,first):
    if second>>8==128:return None
    sides=2 if second&32768 else 1 if second>=256 else 0
    sides|=8 if first&32768 else 4 if first>=96 else 0
    return sides,((sides^15)<<4)|sides


def main():
    flat=flat_action()
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    counts,code_counts=Counter(),Counter()
    touched=set()

    def check(points,profile):
        nonlocal touched
        memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        for i,(second,first) in enumerate(points):
            address=0x8E00+5*i
            for j,value in enumerate((second&255,second>>8,first&255,first>>8,0xA5)):memory[address+j]=value
        memory[0xD699]=4+5*len(points)
        memory[0xBFFE],memory[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':(serial*73)&65535,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDEF3},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial)
        expected=[bytearray(b) for b in memory.banks]
        writes=[]
        def byte(address,value):
            expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
        byte(0xBFFC,initial[7]);byte(0xBFFD,initial[6])
        aggregate=0
        aborted=False
        for i,(second,first) in enumerate(points):
            classified=code(second,first)
            if classified is None:
                aborted=True;break
            sides,value=classified
            byte(0x8E04+5*i,value)
            aggregate|=value
            code_counts[format(value,'02X')]+=1
        wanted[2]=5*len(points)
        wanted[3]=0 if aborted else sides
        if aborted:
            wanted[0:2]=[0,0x44]
            wanted[16:18]=[aggregate,logic_flags(aggregate)]
        else:
            wanted[0:2]=[aggregate,logic_flags(aggregate)]
            wanted[16:18]=[5*len(points),cp_flags(5*len(points),5*len(points))]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(1800):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат классификатора')
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(points,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes),'RAM'
        touched={(bank,offset) for bank,offset,value in memory.writes}
        counts[profile]+=1
        counts['aborted' if aborted else 'completed']+=1
    # Проверка всех слов второй координаты с независимыми вертикальными областями и маркером 80xx.
    for second in range(65536):
        for first in (0,95,96,32768,65535):check(((second,first),),'second_word_slices')
    # Проверка всех слов первой координаты при трёх горизонтальных областях.
    for first in range(65536):
        for second in (0,256,65535):check(((second,first),),'first_word_slices')
    # Проверка всех длин штатной страницы и частично обработанных списков с поздним отказом.
    rng=random.Random(0xDEF3)
    for length in range(1,51):
        for _ in range(10):
            points=[(rng.choice((0,255,256,32767,32768,65535)),rng.choice((0,95,96,32767,32768,65535))) for _ in range(length)]
            check(points,'mixed_lists')
            points[rng.randrange(length)]=(0x8000|rng.randrange(256),rng.randrange(65536))
            check(points,'late_abort_lists')
    total=counts['second_word_slices']+counts['first_word_slices']+counts['mixed_lists']+counts['late_abort_lists']
    report=dict(passed=True,total_cases=total,profiles=dict(counts),written_codes=dict(code_counts),
        exact_registers_and_flags_except_R=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        both_coordinate_words_exhausted_by_separate_slices=True,all_record_counts_1_to_50=True,
        marker_80xx_aborts_without_rollback=True,shared_abort_tail_executed=True,
        empty_and_misaligned_count_outside_contract=True,refresh_and_timing_independently_checked=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    for tag in ('ActionVertexCodes','ActionVertexAbort'):
        (ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
