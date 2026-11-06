"""D95F, проекция и короткая цепь сравнений с неизменным опорным Component2."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsBodyProjection import profiles
from CheckControlsComponentCompare import logical_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceControlsBodyProjection import Projection


def evaluate(banks,registers):
    result=Projection(banks,registers).run()
    # Проверка результата проекции до замены IX и IY указателями физических записей.
    a=result.r[0];result.r[1]=logical_flags(a)|0x10
    if not a:return result,0,'projection_reject'
    reference=result.read(0x9B26)&127;middle=result.read(0x9B25)
    count=0;path='all_three_accept'
    # Поиск первого компонента с большим усечённым ключом, опора всегда Component2.
    for index in range(3):
        high=result.read(0x9B20+3*index)&127;other=result.read(0x9B1F+3*index)
        result.pair(4,(high<<8)|3);count+=1
        if reference<10:
            a=reference|1;f=logical_flags(a)
        elif reference>high:
            a=reference;f=cp_flags(reference,high)
        elif reference<high or middle<other:
            a=0;f=0x44
        else:
            a=middle|1;f=logical_flags(a)
        result.r[0:2]=[a,f]
        if f&0x40:path='component_'+str(index)+'_reject';break
    return result,count,path


def main():
    flat=base_memory();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17);simulator=Simulator(memory)
    counts=Counter();paths=Counter();comparisons=Counter();total=0
    for mode,signs,values,kind in profiles():
        if kind not in ('all_modes_and_signs','component_edges','mixed_components'):continue
        memory.recording=False
        for page in (1,2,5):memory.banks[page][:]=base[page]
        memory[0xCEF9]=mode
        for index,value in enumerate(values):
            encoded=value|(((signs>>index)&1)<<23)
            for offset in range(3):memory[0x9B1E+3*index+offset]=(encoded>>(8*offset))&255
        for offset in range(4):memory[0xD17D+offset]=(total*73+offset*109)&255
        stack=0x8002 if total&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':(total*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,
            'IX':(total*73)&65535,'IY':(total*109)&65535,'SP':stack,'PC':0xD95F},None,False)
        initial[14],initial[15],initial[26],initial[27]=total&255,total&255,total&1,total%3
        expected,count,path=evaluate(memory.banks,initial)
        allowed={(5 if address<0x8000 else 2,address&0x3FFF) for address in range(stack-8,stack)}
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xD95F,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(expected.r[i]==simulator.registers[i] for i in compared),(total,mode,signs,values,path,
            [(i,expected.r[i],simulator.registers[i]) for i in compared if expected.r[i]!=simulator.registers[i]])
        nonstack=[item for item in memory.writes if item[:2] not in allowed]
        assert Counter(nonstack)==Counter(expected.writes),(total,path,'nonstack_writes')
        for bank,offset in allowed:expected.banks[bank][offset]=memory.banks[bank][offset]
        assert all(a==b for a,b in zip(expected.banks,memory.banks)),(total,path,'RAM_except_stack')
        total+=1;counts[kind]+=1;paths[path]+=1;comparisons[count]+=1
        if total%16384==0:print(str(total)+' cases passed',flush=True)
    report=dict(passed=True,total_cases=total,cases_by_kind=dict(counts),paths=dict(paths),comparisons=dict(comparisons),
        actual_projection_ratios_dividers_and_comparisons_executed=True,independent_numeric_parent_oracle=True,
        fixed_reference_component_2_proved=True,short_circuit_and_index_restoration_proved=True,
        exact_registers_except_R=True,all_nonstack_physical_ram_and_write_multiplicity_proved=True,
        maximum_additional_stack_bytes=8,stack_residue_values_and_R_proved=False,
        full_component_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsProjectionGateVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
