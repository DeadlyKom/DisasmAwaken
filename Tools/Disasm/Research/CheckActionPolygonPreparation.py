"""Точные регистры и вся RAM подготовителя D511 до D229 либо плоского RET."""
from collections import Counter
import json, random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from CheckPreviewPolygon import hull
from PreviewEdgeRasterOracle import arithmetic
from ReferenceControlsPointRespawn import cp_flags


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    sim=Simulator(memory);counts=Counter()

    def check(vertices,mode,carry=None):
        memory.recording=False
        for bank in (0,2):memory.banks[bank][:]=base[bank]
        serial=counts.total()
        for i,(y,x) in enumerate(vertices):memory[0x9000+2*i],memory[0x9001+2*i]=x,y
        size=2*len(vertices);memory[0x9BA3]=size;memory[0xD560]=mode
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            'IX':0xABCD,'IY':0x5C3A,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'SP':0xBFFE,'PC':0xD511},None,False)
        initial[14],initial[26],initial[27]=serial&255,serial&1,serial%3
        if carry is not None:initial[1]=(initial[1]&254)|carry
        expected=[bytearray(b) for b in memory.banks];writes=[]
        def byte(a,v):
            bank=2 if a<0xC000 else 0;expected[bank][a&0x3FFF]=v;writes.append((bank,a&0x3FFF,v))
        def word(a,v):byte(a,v&255);byte(a+1,v>>8)
        # Сохранение входного HL и последнего нечётного индекса списка.
        word(0xBFFC,0x1357);byte(0xD3B7,size-1)
        low=min(y for y,x in vertices);high=max(y for y,x in vertices)
        top=next(i for i,(y,x) in enumerate(vertices) if y==low)
        wanted=list(initial)
        if low==high:
            wanted[0:2]=[high,cp_flags(high,high)];wanted[2:6]=[0,1,high,high]
            value,flags=arithmetic(size,1,True)
            wanted[16:18]=[value,(flags&254)|(initial[1]&1)]
            wanted[SP],wanted[PC]=0xC000,0x3FFF
            # Проверка полного F сравнения равных строк и альтернативного DEC размера с исходным Carry.
            closed_alt=2|((size-1)&0x28)|(16 if size&15==0 else 0)|(initial[1]&1)
            assert wanted[1]==0x42|(high&0x28)
            assert wanted[17]==closed_alt
        else:
            # Поиск крайних верхних вершин двух направленных цепочек.
            left=right=top
            while vertices[(left-1)%len(vertices)][0]==low:left=(left-1)%len(vertices)
            while vertices[(right+1)%len(vertices)][0]==low:right=(right+1)%len(vertices)
            byte(0xD4C2,high);byte(0xD4C4,low);byte(0xD387,low)
            word(0xD275,0x9001+2*left);word(0xD3B0,0x9001+2*right)
            pattern,delta=flat[0xD100+2*mode:0xD102+2*mode]
            byte(0xD1FF,delta);byte(0xD258,delta);word(0xD264,0xBFFC)
            byte(0xD22A,low);byte(0xD22C,0x45)
            ix=(((low&7)<<13)+vertices[left][1]*32+mode*2)&65535
            iy=(((low&7)<<13)+vertices[right][1]*32+mode*2+16)&65535
            wanted[0:8]=[low,cp_flags(low,high),0x80+low//8,mode*2,low,high,0x8C,2*right]
            wanted[8:12]=[ix>>8,ix&255,iy>>8,iy&255]
            wanted[16:18]=[pattern,arithmetic(mode,mode)[1]]
            wanted[SP],wanted[PC]=0xFFE0,0xD229
            # Проверка сравнения min<max и флагов удвоенного режима без переноса или переполнения.
            assert wanted[1]==(0x83|(high&0x28)|(16 if low&15<high&15 else 0))
            assert wanted[17]==(0x40 if mode==0 else 8 if mode==4 else 0)
        sim.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(3000):
            if sim.registers[PC]==wanted[PC]:break
            sim.run()
        else:raise AssertionError(('граница подготовителя',vertices,mode))
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==sim.registers[i] for i in compared),(vertices,mode,[(i,wanted[i],sim.registers[i]) for i in compared if wanted[i]!=sim.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(vertices,mode,'RAM')
        assert Counter(writes)==Counter(memory.writes),(vertices,mode,'кратность записей',writes,memory.writes)
        counts['flat' if low==high else 'prepared']+=1

    # Проверка крайних строк, фаз пикселя, размеров списка и обоих обходов верхней горизонтали.
    for row in range(96):
        for mode in range(5):check(((row,3),(row,19),(row,37)),mode)
    for size in range(3,61):
        points=[(2,3),(93,245),(93,3)] if size==3 else [(2,3)]*(size-3)+[(2,245),(93,245),(93,3)]
        for mode in range(5):
            for shift in (0,1,len(points)-1):check(points[shift:]+points[:shift],mode)
    # Проверка прежнего пробела, горизонтальные контуры всех допустимых длин и обоих входных Carry.
    for size in range(3,61):
        row=(size*7)%96
        points=tuple((row,(i*29)&255) for i in range(size))
        for carry in (0,1):
            for mode in range(5):check(points,mode,carry)
    rng=random.Random(0xD511)
    for _ in range(2048):
        points=hull([(rng.randrange(96),rng.randrange(256)) for i in range(rng.randrange(4,20))])
        if len(points)<3:continue
        shift=rng.randrange(len(points));check(points[shift:]+points[:shift],rng.randrange(5))
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),boundary=0xD229,
        exact_registers_flags_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        original_instructions_without_stubs=True,counts_3_to_60=True,modes_0_to_4=True,
        convex_positive_winding_profile=True,whole_polygon_fill_proved=False,
        flat_counts_3_to_60_both_initial_Carry=True,closed_AF_and_alternate_AF_formulas_checked=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonPreparationVerification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
