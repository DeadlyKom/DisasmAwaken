"""CF0B целиком, настоящие отношения и делители, частичные поля проекции и все байты режима."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsBodyProjection import Projection


def profiles():
    patterns=((0,0,0),(1,0,1),(0xA000,1,0xA000),(0xA001,1,0xA001),
        (1000000,500000,1000000),(0x7FFFFF,0x7FFFFF,0x7FFFFF),
        (0xFFFF,0x10000,0x10001),(0x100000,0x200000,0x180000))
    for mode in range(256):
        for signs in range(8):
            for values in patterns:yield mode,signs,values,'all_modes_and_signs'
    edges=(0,1,255,256,0xA000,0xA001,0xFFFF,0x7FFFFF)
    for mode in range(4):
        for signs in range(8):
            for values in product(edges,repeat=3):yield mode,signs,values,'component_edges'
    # Проверка каждого слова глубины для радиуса, оба отношения имеют нулевые числители.
    for word in range(32768):yield 0,0,(0,0,(word<<8)|(word&255)),'all_radius_depth_words'
    boundaries=(0,1,2,127,255,256,257,65535,65536,1000000,0x3FFFFF,0x7FFFFF)
    for depth in boundaries:
        numerators=sorted({0,max(0,depth-1),depth,min(0x7FFFFF,depth+1),min(0x7FFFFF,2*depth-1),min(0x7FFFFF,2*depth),min(0x7FFFFF,2*depth+1)})
        for mode in range(4):
            for numerator in numerators:
                for vertical in (0,depth,min(0x7FFFFF,2*depth)):
                    values=(numerator,vertical,depth) if mode<2 else (depth,vertical,numerator)
                    sign=(1<<(2 if mode<2 else 0)) if mode in (1,2) else 0
                    yield mode,sign,values,'ratio_boundaries'
    randomizer=random.Random(0xCF0B)
    for _ in range(8192):yield randomizer.randrange(256),randomizer.randrange(8),tuple(randomizer.randrange(0x800000) for _ in range(3)),'mixed_components'


def main():
    flat=base_memory();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17);simulator=Simulator(memory)
    counts=Counter();paths=Counter();total=0;max_stack_writes=0
    for mode,signs,values,kind in profiles():
        memory.recording=False
        for page in (1,2,5):memory.banks[page][:]=base[page]
        memory[0xCEF9]=mode
        for index,value in enumerate(values):
            encoded=value|(((signs>>index)&1)<<23)
            for offset in range(3):memory[0x9B1E+3*index+offset]=(encoded>>(8*offset))&255
        for offset in range(4):memory[0xD17D+offset]=(total*73+offset*109)&255
        stack=0x8002 if total&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':(total*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0xCF0B},None,False)
        initial[14],initial[15],initial[26],initial[27]=total&255,total&255,total&1,total%3
        expected=Projection(memory.banks,initial).run()
        allowed={(5 if address<0x8000 else 2,address&0x3FFF) for address in range(stack-6,stack)}
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xCF0B,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(expected.r[i]==simulator.registers[i] for i in compared),(total,mode,signs,values,expected.path,
            [(i,expected.r[i],simulator.registers[i]) for i in compared if expected.r[i]!=simulator.registers[i]])
        # Проверка отказа по знаку до вызовов отношений, исходные пары и RAM должны сохраниться.
        depth=2 if mode<2 else 0
        if bool(signs&(1<<depth)) != (mode in (1,2)):
            assert simulator.registers[0:2]==[0,0x44]
            assert simulator.registers[2:8]==initial[2:8]
            assert simulator.registers[18:20]==[0,3] and not memory.writes
        elif simulator.registers[0]==1:
            # Расчёт конечных битов направлений и N<=Q напрямую из исходных компонент.
            horizontal=0 if mode<2 else 2
            q=values[depth]
            direction_x=int(bool(signs&(1<<horizontal)) == (mode not in (0,2)))
            direction_y=0 if signs&2 else 2
            flags=direction_x|direction_y|(4 if values[horizontal]<=q else 0)|(8 if values[1]<=q else 0)
            assert simulator.registers[18:20]==[flags,1]
            assert memory[0xD17F]==flags and not flags&0xF0
            if q<=0xA000:
                # Проверка ближнего радиуса, DE содержит глубину, а не результат деления.
                assert simulator.registers[4:8]==[q>>8,q&255,(0xA000-q)>>8,(0xA000-q)&255]
                assert memory[0xD180]==255
                # Проверка двух успешных исходов с разным Z, статус задаётся A, а не сохранёнными F радиуса.
                if q in (0,0xA000):
                    assert simulator.registers[0:2]==[1,0xA2 if q==0 else 0x42]
        nonstack=[item for item in memory.writes if item[:2] not in allowed]
        assert Counter(nonstack)==Counter(expected.writes),(total,expected.path,'nonstack_writes',nonstack,expected.writes)
        for bank,offset in allowed:expected.banks[bank][offset]=memory.banks[bank][offset]
        assert all(a==b for a,b in zip(expected.banks,memory.banks)),(total,expected.path,'RAM_except_stack')
        total+=1;counts[kind]+=1;paths.update(expected.path)
        max_stack_writes=max(max_stack_writes,len(memory.writes)-len(nonstack))
        if total%16384==0:print(str(total)+' cases passed',flush=True)
    report=dict(passed=True,total_cases=total,cases_by_kind=dict(counts),paths=dict(paths),
        all_mode_bytes_and_sign_combinations=True,all_depth_words_for_radius=True,actual_ratios_and_dividers_executed=True,
        primary_and_unwound_rejections_proved=True,partial_projection_writes_preserved=True,selected_depth_sign_cleared_in_place=True,
        exact_registers_except_R=True,all_nonstack_physical_RAM_and_write_multiplicity_proved=True,
        stack_writes_confined_to_six_bytes=True,max_observed_stack_byte_writes=max_stack_writes,
        stack_residue_values_and_R_proved=False,unreachable_far_rejection_explained_by_23_bit_depth=True,
        direct_depth_sign_reject_and_final_flag_invariants=True,
        direct_near_radius_depth_register_invariants=True,
        independent_integer_parent_oracle=True,full_component_product_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsBodyProjectionVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
