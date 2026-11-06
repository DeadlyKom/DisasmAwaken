"""Прямой преобразователь 6C19 и копировщик 6BFF, настоящие арифметический SP и кодирование компонент."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionThirdGlyphVector import profiles,INPUTS,OUTPUTS,COEFFICIENTS
from ReferenceActionPatchedVector import evaluate
from CheckActionComponentEncoding import evaluate_encoding
from ReferenceControlsPointRespawn import refresh


def cases():
    for gate,flags,vector,matrix,kind in profiles():
        if gate:continue
        if kind=='gate_and_flags':kind='initial_flags'
        for entry in (0x6C19,0x6BFF):yield entry,flags,vector,matrix,kind,0x9000
    # Проверка последовательного копирования при перекрытии источника, рабочих полей и рамки CPU-стека.
    matrix=((127,0,0),(0,127,0),(0,0,127))
    for pointer in (0x9B1C,0x9B1D,0x9B1E,0x9B1F,0x9B20,0x9B21,0x8000,0xBFFC,0xFFF8):
        for flags in range(8):yield 0x6BFF,flags,(1,0x8001,0x7FFF),matrix,'source_aliases',pointer


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();paths=Counter();sites=Counter();total=0
    for entry,flags,vector,matrix,kind,pointer in cases():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        def fixture_byte(address,value):
            address&=65535
            if address>=0x4000:memory[address]=value
        def fixture_word(address,value):fixture_byte(address,value&255);fixture_byte(address+1,value>>8)
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        for index,value in enumerate(vector):
            memory[0x9B1E+3*index]=(total+index*73)&255;fixture_word(0x9B1F+3*index,value)
            if entry==0x6BFF:
                for offset,byte in enumerate(((total+index*109)&255,value&255,value>>8,0xA5)):
                    fixture_byte(pointer+4*index+offset,byte)
        old_outputs=(0x5342,0x6453,0x7564)
        for address,value in zip(OUTPUTS,old_outputs):fixture_word(address,value)
        stack=0x8002 if total&1 else 0xBFFE;fixture_word(stack,0x3FFF)
        initial_bc=(0,1,8,9,255,256,264,65535)[flags&7]
        initial=get_registers({'AF':((total*73)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':initial_bc,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':pointer,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=total&255,total&255,total&1,total%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]

        def read(address):
            address&=65535
            if address<0x4000:return memory.roms[1][address]
            return expected[5 if address<0x8000 else 2 if address<0xC000 else 0][address&0x3FFF]

        def put(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

        def word(address,value):put(address,value&255);put(address+1,value>>8)

        overhead=15
        if entry==0x6BFF:
            word(stack-2,pointer);source=pointer
            for component in range(3):
                for offset in range(3):put(0x9B1E+3*component+offset,read(source));source=(source+1)&65535
                if component<2:source=(source+1)&65535
            wanted[2]=((initial_bc-9)&65535)>>8;overhead+=24
        actual_vector=tuple(read(address)+256*read(address+1) for address in (0x9B1F,0x9B22,0x9B25))
        for address,value in zip(INPUTS,actual_vector):word(address,value)
        word(0x6C41,stack)
        for address in (0x9B1E,0x9B21,0x9B24):put(address,0)
        word(0xAFF1,0xABCD)
        result=evaluate(actual_vector,matrix,old_outputs)
        for row in result['performed']:word(OUTPUTS[row],result['outputs'][row])
        wanted[0:2]=result['af'];wanted[3]=0;wanted[4:6]=[result['de']>>8,result['de']&255]
        wanted[6:8]=[result['hl']>>8,result['hl']&255];wanted[16:18]=result['alternate_af'];wanted[10:12]=[0x6C,0x40]
        if result['overflow']:
            post_m1=1;paths['overflow']+=1;sites[str(result['stop_position'])]+=1
        else:
            encoded=evaluate_encoding(result['outputs'],result['af'][0],result['af'][1]&1)
            for address,value in zip((0x9B1F,0x9B22,0x9B25),encoded['words']):word(address,value)
            wanted[0:2]=encoded['af'];wanted[6:8]=[encoded['hl']>>8,encoded['hl']&255]
            post_m1=encoded['refresh_m1'];paths['encoded']+=1
        m1=overhead+result['refresh_m1']+1+post_m1
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(total,hex(entry),kind,pointer,vector,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(total,hex(entry),kind,'RAM')
        assert Counter(memory.writes)==Counter(writes),(total,hex(entry),kind,'writes')
        counts[format(entry,'04X')+'_'+kind]+=1;total+=1
    assert len(sites)==6
    report=dict(passed=True,total_cases=total,cases_by_kind=dict(counts),paths=dict(paths),overflow_sites=dict(sites),
        actual_compute_stack_restore_and_encoder_executed=True,all_six_overflow_sites=True,
        copy_has_three_byte_components_and_four_byte_stride=True,sequential_source_aliases_checked=True,
        prefix_BC_decrements_by_nine=True,lower_component_bytes_cleared_even_on_overflow=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        direct_entry_CPU_stack_written=False,copy_entry_CPU_stack_bytes=2,
        compositional_numeric_oracle=True,independent_new_vector_oracle=False,full_vector_matrix_product_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionComponentTransformVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
