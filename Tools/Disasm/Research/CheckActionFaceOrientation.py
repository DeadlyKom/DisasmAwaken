"""DFB6..E008, настоящие POP из точек и оба умножителя, точные RAM и стековые слова."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionFaceOrientation import face


def main():
    flat=flat_action()
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    counts,paths=Counter(),Counter()
    defects=0

    def check(points,count,profile):
        nonlocal defects
        memory.recording=False
        for i,(second,first) in enumerate(points):
            for j,value in enumerate((second&255,second>>8,first&255,first>>8,0xA5)):memory[0x8E00+5*i+j]=value
        for i,value in enumerate((0xA5,0,5,10,15,20)):memory[0x9000+i]=value
        memory[0xBFFE],memory[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':count*256+(serial&255),'HL':0x9000,'DE':0x2468,'BC':(serial*73)&65535,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDFB6},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        result=face(points,count,0xABCD)
        wanted=list(initial);wanted[0:2]=result['af']
        for position,value in ((4,result['low']),(8,result['ix']),(18,result['first']['bc']),(20,result['first']['low']),(22,result['first']['high'])):
            wanted[position:position+2]=[value>>8,value&255]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        expected=[bytearray(b) for b in memory.banks];writes=[]
        def byte(address,value):
            bank=2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        # Запись всех служебных слов по фактическим уровням CPU-стека, рабочие POP точек RAM не меняют.
        word(0xBFFC,initial[2]*256+initial[3]);word(0xBFFA,0x9000)
        word(0xDFE4,0xBFFA)
        word(0xBFF8,result['v_first']);word(0xBFF8,result['v_second'])
        word(0xBFF8,0xDFF8);word(0xBFF6,result['first']['stack_af'][0]*256+result['first']['stack_af'][1])
        word(0xBFF8,result['first']['high']);word(0xBFF6,result['first']['low'])
        word(0xBFF4,0xDFFE);word(0xBFF2,result['second']['stack_af'][0]*256+result['second']['stack_af'][1])
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(650):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат ориентации')
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(count,points,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes),'RAM'
        counts[profile]+=1;paths['first_three' if count<5 else 'alternating_three']+=1
        paths['negative' if result['af'][1]&128 else 'nonnegative']+=1
        defects+=int(result['first']['defect'])+int(result['second']['defect'])
    # Проверка отдельных координат против границ signed16 и экранных пределов при обоих способах выбора тройки.
    for count in (3,4,5,6):
        for component in range(6):
            for value in (0,1,95,96,127,255,256,32767,32768,65535):
                coords=[0x1357,0x2468,0x369C,0x47AD,0x58BE,0x69CF];coords[component]=value
                chosen=[tuple(coords[i:i+2]) for i in (0,2,4)]
                points=chosen+[(0xA5A5,0x5A5A)]*2 if count<5 else [chosen[0],(0xA5A5,0x5A5A),chosen[1],(0x5A5A,0xA5A5),chosen[2]]
                check(points,count,'coordinate_boundaries')
        for selected in (((0,0),(32768,32768),(256,256)),((0,0),(256,32768),(32768,256)),
                         ((32768,32768),(0,0),(65535,65535)),((65535,65535),(0,0),(1,1))):
            points=list(selected)+[(0,0)]*2 if count<5 else [selected[0],(0,0),selected[1],(0,0),selected[2]]
            check(points,count,'multiply_exception_boundaries')
    # Проверка всех полных входных байтов A, Carry от CP 5 намеренно становится первым заёмом.
    for count in range(256):check([(0,0),(1,95),(255,96),(256,32768),(65535,65535)],count,'all_count_bytes')
    rng=random.Random(0xDFB6)
    for _ in range(4096):check([tuple(rng.randrange(65536) for _ in range(2)) for _ in range(5)],rng.randrange(16),'mixed')
    assert defects>0
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),multiply_exception_hits=defects,
        children_executed_without_stubs=True,all_full_count_bytes=True,carry_from_count_comparison_preserved=True,
        borrow_chain_across_coordinates_preserved=True,multiply_return_carry_used_by_final_subtract=True,
        final_EXX_bank_change_checked=True,exact_registers_and_flags_except_R=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True,maximum_extra_cpu_stack_bytes=12,
        refresh_and_timing_independently_checked=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionFaceOrientationVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
