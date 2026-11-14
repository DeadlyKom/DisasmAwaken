"""Четыре писателя пересечений, полный M1 и R всех ветвей ограничения.

Документация: ../../../Docs/ActionClipIntersections.md#точный-r-писателей-пересечений
"""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckSignedDivision import expected as divide
from ReferenceActionClipRefresh import intersection_cost
from ReferenceControlsPointRespawn import refresh

DETAILS=((0xC4F6,0xCF37,False,0),(0xC540,0xCF33,False,95),(0xC58B,0xCF2F,True,0),(0xC5E7,0xCF2B,True,255))


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=banks,out7ffd=16);s=Simulator(m);counts,paths=Counter(),Counter()
    def check(entry,product,vertical,bound,number,coordinates,offset):
        m.recording=False
        for address,value in zip((0xCF0B,0xCF1B,0xCF0D,0xCF1D),coordinates):m[address],m[address+1]=value&255,value>>8
        raw=number&0xFFFFFFFF
        for i in range(4):m[product+i]=(raw>>(8*i))&255
        m[0x9BA3]=offset;m[0xBFFE],m[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*73&255,serial&1,serial%3
        x1,x2,y1,y2=coordinates;first,second=(x1,x2) if vertical else (y1,y2)
        denominator=(second-first)&65535;signed=denominator-65536 if denominator&32768 else denominator
        q,_,alt_flags,bc,_,ix=divide(number,signed,int(second<first),initial[1]&1,0x369C)
        base=y1 if vertical else x1;translated=(q+base)&65535
        de=base
        if translated&32768:
            output=(bound,0) if vertical else (0,bound);path='negative_word'
        elif vertical:
            if translated&128:output=(bound,95);path='low_byte_negative'
            else:
                output=(bound,translated&255);de=(translated&255)*256+(base&255);path='vertical_low_byte'
        else:
            value=255 if translated>>8 else translated&255
            output=(value,bound);de=(base&0xFF00)|value;path='horizontal_high' if translated>>8 else 'horizontal_inside'
        next_offset=(offset+2)&255;previous=(next_offset-1)&255
        flags=(next_offset&0xA8)|(64 if next_offset==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)
        # XOR A на отрицательной ветви Top меняет нулевую вторую координату, DE всё равно сохраняет базу.
        wanted=list(initial);wanted[0:2]=[next_offset,flags];wanted[16:18]=[q&255,alt_flags]
        for position,value in ((2,bc),(4,de),(6,0x9000|next_offset),(8,0xAB00|(ix&255))):wanted[position:position+2]=[value>>8,value&255]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        expected_m1=intersection_cost(entry,number,signed,translated);wanted[15]=refresh(initial[15],expected_m1)
        expected=[bytearray(b) for b in m.banks];writes=[]
        def byte(address,value):expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
        byte(0xBFFC,(entry+24)&255);byte(0xBFFD,(entry+24)>>8)
        byte(0x9000+offset,output[0]);byte(0x9000+((offset+1)&255),output[1]);byte(0x9BA3,next_offset)
        s.registers[:]=initial;m.writes=[];m.recording=True
        measured_m1=0
        for _ in range(200):
            if s.registers[PC]==0x3FFF:break
            before=s.registers[15];s.run();increment=(s.registers[15]-before)&127
            assert increment in (1,2);measured_m1+=increment
        else:raise AssertionError('возврат пересечения')
        assert measured_m1==expected_m1,(entry,number,coordinates,measured_m1,expected_m1)
        m.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==s.registers[i] for i in compared),(hex(entry),number,coordinates,offset,[(i,wanted[i],s.registers[i]) for i in compared if wanted[i]!=s.registers[i]])
        assert all(a==b for a,b in zip(expected,m.banks)) and Counter(writes)==Counter(m.writes)
        counts[format(entry,'04X')]+=1;paths[path]+=1
    rng=random.Random(0xC4F6)
    for entry,product,vertical,bound in DETAILS:
        # Проверка всех промежуточных слов, в том числе положительных со старшим ненулевым байтом и младшим 00..7F.
        coordinates=(0,1,0,0) if vertical else (0,0,0,1)
        for value in range(65536):check(entry,product,vertical,bound,value,coordinates,(2*value)&255)
        # Проверка всех выходных смещений с переносом внутри страницы, оба байта пишутся через INC L.
        for offset in range(256):check(entry,product,vertical,bound,127,coordinates,offset)
        for _ in range(4096):
            coordinates=[rng.randrange(65536) for _ in range(4)];a,b=(coordinates[0],coordinates[1]) if vertical else (coordinates[2],coordinates[3])
            d=(b-a)&65535
            if d==0:coordinates[1 if vertical else 3]=(b+1)&65535;d=1
            signed=d-65536 if d&32768 else d
            magnitude=rng.randrange(abs(signed)*65536)
            number=magnitude if rng.randrange(2) else -magnitude-1
            check(entry,product,vertical,bound,number,coordinates,rng.randrange(256))
    report=dict(passed=True,total_cases=counts.total(),entries=dict(counts),paths=dict(paths),
        actual_division_executed=True,all_intermediate_words_per_entry=True,all_output_offsets=True,
        original_vertical_low_byte_sign_rule_preserved=True,exact_registers_flags_except_R=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True,extra_cpu_stack_bytes=2,
        exact_refresh_R_checked=True,full_M1_count_compared=True,exact_T_claimed=False,all_joint_inputs_exhausted=False,refresh_and_timing_independently_checked=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipIntersectionsRefreshVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
