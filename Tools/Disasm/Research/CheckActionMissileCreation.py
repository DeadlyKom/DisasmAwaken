"""60AE, пути существующей цели, настоящая геометрия, поиск и запись полей, без подмен."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceActionPatchedVector import evaluate
from CheckActionPatchedVector import INPUTS,COEFFICIENTS,OUTPUTS
from CheckActionPatchSwap import PAIRS
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set()
    def cost(start,end):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(start,end,'h'))
    before_choice=cost(0x60C8,0x60E4);before_result=cost(0x60E6,0x60F1);initialize=cost(0x60F1,0x6145)
    def check(target,free,preferred,fallback,matrix,skip=False,state=0):
        nonlocal touched
        assert free is None or free!=target
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=baseline[address]
        # Создание 25 исходных записей и отдельного маркера, без предположения о динамическом пределе игры.
        for i in range(26):
            base=0xA100+i*64
            memory[base:base+64]=[(serial+i*67+j*13)&255 for j in range(64)]
            memory[base],memory[base+1],memory[base+24]=0x23,0,73
            if skip and i!=target and (free is None or i<free):memory[base],memory[base+1],memory[base+24]=0,128,255
        memory[0xA740:0xA742]=[128,128]
        target_base=0xA100+64*target;memory[target_base+1]=state
        if free is not None:
            free_base=0xA100+64*free;memory[free_base],memory[free_base+1],memory[free_base+24]=0,128,0
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        memory[0x9C12:0x9C14]=[fallback,preferred];old_outputs=[0x5342,0x6453,0x7564]
        for address,value in zip(OUTPUTS,old_outputs):memory[address:address+2]=[value&255,value>>8]
        memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x3600|target,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x60AE},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[];stack=0xBFFE
        def byte(address,value):writes.append((address,value));expected[address]=value
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        word(stack-2,0x60B2);word(stack-2,0x3600|target);word(stack-4,0x60D5)
        # Расчёт настоящей рамки TransformVectorTransposed при входном SP, уменьшенном на четыре.
        word(stack-6,0xABCD);word(stack-8,0x5C3A)
        for address,value in zip(INPUTS,(0,0,400)):word(address,value)
        word(stack-10,0xACFC)
        for left,right in PAIRS:
            a=expected[left]+256*expected[left+1];b=expected[right]+256*expected[right+1];word(right,a);word(left,b)
        word(0xAD08,stack-8);word(0xAFF1,0xABCD)
        vector=evaluate((0,0,400),list(map(list,zip(*matrix))),old_outputs)
        for row in vector['performed']:word(OUTPUTS[row],vector['outputs'][row])
        word(stack-10,0xAD0D)
        for left,right in PAIRS:
            a=expected[left]+256*expected[left+1];b=expected[right]+256*expected[right+1];word(right,a);word(left,b)
        for position,value in zip((22,20,18),vector['outputs']):wanted[position:position+2]=[value>>8,value&255]
        # Расчёт выбора поля запаса и исходного параметра 0A либо 32, без списания запасов.
        word(stack-2,0x60DD);selected=0x9C13 if preferred else 0x9C12;parameter=50 if preferred else 10
        byte(0x612E,parameter);word(stack-2,0x1A00|target);word(stack-4,0x60EF)
        finder=3
        for i in range(26):
            base=0xA100+64*i;header,record_state,tag=expected[base],expected[base+1],expected[base+24]
            if record_state!=128:finder+=6;continue
            if header==128:finder+=10;found=None;break
            byte(base+24,0)
            if tag==255:finder+=16;continue
            finder+=17;found=i;break
        assert found==free,(target,free,skip,found)
        m1=18+before_choice+int(bool(preferred))+vector['refresh_m1']+65+(4 if preferred else 7)+before_result+finder
        wanted[2:4]=[0x1A,target]
        if free is None:
            wanted[6:8]=[selected>>8,selected&255];wanted[4:6]=[0,64];wanted[0:2]=[128,0x42]
            wanted[16:18]=[1,vector['af'][1]];wanted[10:12]=[0xA7,0x40];path='no_record'
        else:
            base=0xA100+64*free
            # Создание эталона 19 полей новой записи, остальные исходные байты остаются нетронутыми.
            for offset,value in zip((0,2,4),vector['outputs']):word(base+offset,value)
            for offset,value in ((6,0x90),(7,0),(8,0),(9,0),(10,8),(11,0),(12,0),(13,0x1A),
                (15,target),(17,1),(18,0x11),(19,parameter),(37,2)):byte(base+offset,value)
            word(stack-2,0x6137)
            byte(target_base+12,expected[target_base+12]|2)
            word(stack-2,0x6142);word(stack-4,64);word(stack-6,base);word(stack-6,0xE6C5)
            byte(target_base+11,free)
            wanted[0:2]=[free,0x45|(free&0x28)];wanted[6:8]=[0,64]
            wanted[4:6]=[(target_base+11)>>8,(target_base+11)&255];wanted[10:12]=[base>>8,base&255]
            wanted[16:18]=[0,0x44];m1+=initialize+12+16;path='created'
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0x60AE,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(target,free,preferred,fallback,skip,state,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(target,free,preferred,fallback,skip,state,memory.writes,writes)
        assert min(address for address,_ in memory.writes if stack-12<=address<stack)==stack-10
        touched={address for address,_ in writes};counts['cases']+=1;paths[path]+=1
    identity=((127,0,0),(0,127,0),(0,0,127))
    # Проверка каждой пары различных исходных слотов и обоих путей выбора запаса.
    for target in range(25):
        for free in range(25):
            if free==target:continue
            for pair in ((0,0),(0,1),(0,255),(1,0),(2,255),(255,255)):
                for skip in (False,True):check(target,free,*pair,identity,skip)
        for pair in ((0,0),(0,1),(1,0),(255,255)):
            for skip in (False,True):check(target,None,*pair,identity,skip)
    print('All initial slot pairs and stock profiles complete',flush=True)
    # Проверка каждого допустимого байта состояния цели, 80 относится к отдельному пути потерянной цели.
    for state in range(256):
        if state!=128:check(0,1,1,255,identity,True,state)
    # Проверка всех девяти коэффициентов на граничных значениях и исходного параметра выбранного запаса.
    for row in range(3):
        for column in range(3):
            for coefficient in range(256):
                matrix=[[0]*3 for _ in range(3)];matrix[row][column]=coefficient
                for preferred in (0,1):check(24,0,preferred,255,matrix)
    report=dict(passed=True,total_cases=counts.total(),paths=dict(paths),
        method='creation_parent_oracle_composed_with_real_geometry_stock_search_and_index_children',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_distinct_initial_record_slot_pairs=True,initial_record_slots=25,initial_marker_address='A740',
        marker_is_original_seed_not_proved_runtime_limit=True,all_non80_target_state_bytes=True,
        all_matrix_coefficient_bytes=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_multiplicity_checked=True,unwritten_object_bytes_preserved=True,
        both_stock_fields_remain_unchanged=True,selected_parameter_0a_or_32_preserved=True,
        maximum_additional_stack_bytes=10,lost_target_branch_checked_here=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileCreationVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
