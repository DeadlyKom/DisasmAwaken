"""Полный исходный проход D5C9 с настоящими банковым копированием, произведениями и перспективой."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from CheckActionObjectCopy import packet
from CheckActionRenderMatrix import OUTPUT
from CheckActionVertexProducts import TARGETS
from PreviewVertexProductsOracle import general
from ReferenceActionVertexGroup import group,WORD_TARGETS,BYTE_TARGETS


def main():
    flat=flat_action()
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[4][:len(objects)]=objects
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    touched=set()
    counts,reasons=Counter(),Counter()
    maximum_native_points=0
    rng=random.Random(0xD5C9)

    def check(index,coefficients,base,payload=None):
        nonlocal touched,maximum_native_points
        memory.recording=False
        for bank,offset in touched:
            memory.banks[bank][offset]=baseline[bank][offset]
        if payload is not None:
            memory[0x9E00+index],memory[0x9E00+((index+1)&255)]=0,0xC0
            memory.banks[4][:len(payload)]=payload
        pointer=memory[0x9E00+index]+256*memory[0x9E00+((index+1)&255)]
        raw,fixed,lengths=packet(memory.banks[4],pointer-0xC000)
        exponent=raw[1]
        assert 1<=exponent<=6
        memory[0x9B8E]=index
        for row in range(3):
            for column in range(3):memory[OUTPUT[row][column]]=coefficients[row][column]
        for address,value in zip((0xD7A2,0xD7C4,0xD9B6),base):
            memory[address],memory[address+1]=value&255,value>>8
        memory[0xBFFE],memory[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'BC':(serial*73)&65535,'DE':0x2468,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD5C9},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        expected=[bytearray(b) for b in memory.banks]
        writes=[]
        def byte(address,value):
            bank=2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value
            writes.append((bank,address&0x3FFF,value))
        def word(address,value):
            byte(address,value&255);byte(address+1,value>>8)
        bc=initial[2]*256+initial[3]
        final_bc=65535 if lengths else (bc-len(raw))&65535
        # Сохранение реальных CPU-возвратов и счётчиков настоящего банкового копировщика.
        word(0xBFFC,0xD5D0)
        for ret,saved in ((0xAAED,bc),(0xAB1A,final_bc)):
            word(0xBFFA,ret);word(0xBFF8,saved)
        for i,value in enumerate(raw):byte(0x9F1C+i,value)
        byte(0xD699,4)
        for address in (0xD7AC,0xD7C7,0xD9B9):byte(address,6-exponent)
        wanted=list(initial)
        wanted[0:2]=[0,0x54]
        for position,value in ((2,final_bc),(4,0x9F1C+len(raw))):wanted[position:position+2]=[value>>8,value&255]
        offset=4
        alternates=(tuple(initial[16:18]),0x9ABC,0x5678,0x1234)
        point_count=0
        # Преобразование всех фиксированных записей без чтения переменной части после маркера.
        for record in range(fixed):
            position=2+record*4
            tag,b,c,d=raw[position:position+4]
            next_pointer=0x9F1C+position+4
            word(0xBFFC,next_pointer);word(0xBFFA,0xD5F5)
            words,thirds=general(coefficients,(b,c,d))
            values=tuple(w>>8 for w in words)+tuple(w&255 for w in words)+thirds
            for address,value in zip(TARGETS,values):byte(address,value)
            result=group(words,thirds,tag,base,exponent,offset,alternates)
            word(0xD79D,0xBFFA)
            for corner in (0,1,3,2,5,4,6,7):word(WORD_TARGETS[corner],result['words'][corner])
            for corner in (5,4,6,7):byte(BYTE_TARGETS[corner],result['depths'][corner])
            for stack,point in result['points']:
                if point['save_depth']:word(0xD9C3,point['depth'])
                word(stack-2,point['first']);word(stack-4,point['second'])
                reasons[point['reason']]+=1
            point_count+=len(result['vertices'])
            offset=result['stack']&255
            byte(0xD699,offset)
            for position,key in ((2,'bc'),(4,'de'),(8,'ix'),(10,'iy'),(18,'alt_bc'),(20,'alt_de'),(22,'alt_hl')):
                value=result[key];wanted[position:position+2]=[value>>8,value&255]
            wanted[16:18]=result['alt_af']
            alternates=(result['alt_af'],result['alt_bc'],result['alt_de'],result['alt_hl'])
        value=0x9F1F+4*fixed
        wanted[6:8]=[value>>8,value&255]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial
        trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True
        for _ in range(60000):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат объекта',index))
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(index,payload is not None,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes),('RAM',index)
        assert trace.writes==[(0x7FFD,20),(0x7FFD,16)] and memory.o7ffd==16
        touched={(bank,address) for bank,address,value in memory.writes}
        if payload is not None:
            touched.update((4,i) for i in range(len(payload)))
            touched.update((2,(0x9E00+i)&0x3FFF) for i in (index,(index+1)&255))
        else:maximum_native_points=max(maximum_native_points,point_count)
        counts['synthetic' if payload is not None else 'native']+=1
    # Проверка всех исходных чётных указателей, отказов глубины и осей с двумя различными матрицами.
    for index in range(0,256,2):
        for base in ((1500,0,0),(0,0,0),(32768,0,0),(1,32768,32768)):
            for coefficients in (((127,0,0),(0,127,0),(0,0,127)),tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3))):
                check(index,coefficients,base)
    # Проверка всех ненулевых кодов групп и шести масштабов на конечном синтетическом потоке.
    for exponent in range(1,7):
        for tag in range(1,256):
            raw=bytes((0xA5,exponent,tag,0x13,0x57,0x9B,0,0xF1,0xAB,0xE0))
            check(0,tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3)),(1000,0,0),raw)
        check(0,((127,0,0),(0,127,0),(0,0,127)),(1000,0,0),bytes((0xA5,exponent,0,0)))
    assert maximum_native_points==40
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),projection_paths=dict(reasons),
        original_even_pointers=128,maximum_original_points=maximum_native_points,maximum_original_next_offset=4+5*maximum_native_points,
        children_executed_without_stubs=True,real_eight_physical_banks_and_out_sequence=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True,exact_registers_and_flags_except_R=True,
        refresh_and_timing_independently_checked=False,maximum_extra_cpu_stack_bytes=6,
        all_nonzero_tag_bytes_and_six_scales=True,empty_fixed_part_checked=True,
        variable_records_copied_but_not_interpreted=True,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectVerticesVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
