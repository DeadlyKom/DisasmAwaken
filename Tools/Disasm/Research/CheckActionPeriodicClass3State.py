"""State0B, общий четырёхбитный период, поиск и заполнение ребёнка класса 3 до RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionChildSpawn import SpawnMachine
from CheckActionNearestCandidate import NearestMachine
from CheckActionRegionType import reference as region
from ReferenceActionClampVectorWords import logical_flags
from CheckActionMissileConsume import dec_flags
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags


class PeriodicMachine(SpawnMachine,NearestMachine):
    def reset(self):
        self.pair(6,0)
        for address in (0xE5B0,0xE5CF,0xE5EA):self.put_word(address,0)
        return self.finish(5)

    def classify(self):
        code,flags,m1=region(self.r[6],self.r[7]);self.r[0:2]=[code,flags];return self.finish(m1)

    def periodic(self):
        ix=self.r[8]*256+self.r[9];phase=(self.read(0xF3F1)+1)&15
        self.put(0xF3F1,phase);self.r[0:2]=[phase,logical_flags(phase)|16];self.m1(5)
        if phase:self.path.append('phase_skip');return self.reset()
        self.call(0xE9A1,0xF3FE,self.reusable);self.m1(1)
        if self.r[1]&64:self.path.append('no_child_slot');return self.reset()
        iy=self.r[10]*256+self.r[11];self.r[0]=self.read(ix+13);self.m1(2)
        self.call(0xE6A7,0xF407,self.index_address);pointer=self.r[6]*256+self.r[7]
        self.r[7]=(self.r[7]+1)&255;high=self.read(pointer+1);self.r[0:2]=[high,cp_flags(high,128)];self.m1(4)
        if high==128:
            self.put(ix+10,9);self.m1(3);self.path.append('linked_unavailable');return self.reset()
        self.put_word(iy,self.word(ix));self.m1(8)
        self.m1(2);b=(self.r[15]&1)+1;self.pair(2,b*256+128);self.m1(4)
        y=(self.word(ix+2)+b*256+128)&65535;self.put_word(iy+2,y);self.m1(9)
        self.put_word(iy+4,self.word(ix+4));self.m1(8)
        self.pair(6,self.word(0x9BC1));self.m1(1);self.call(0x6E2B,0xF447,self.classify)
        model=16+4*self.r[0];self.r[0:2]=[model,add_flags(model-16,16)];self.put(iy+6,model);self.m1(5)
        for field,value in ((15,150),(7,64),(8,0),(9,0),(17,70),(10,2),(22,12),(12,0),(18,3),(20,0)):
            self.put(iy+field,value);self.m1(2)
        linked=self.read(ix+13);self.r[0]=linked;self.m1(2)
        for field,value in ((21,255),(11,linked),(19,100),(16,30),(37,2)):
            self.put(iy+field,value);self.m1(2)
        old=self.read(ix+22);value=(old-1)&255;self.r[0:2]=[value,dec_flags(old,0)]
        self.put(ix+22,value);self.m1(6)
        if value==0:self.put(ix+10,9);self.m1(2);self.path.append('parent_state_09')
        self.m1(1);self.path.append('class3_child_written');return self.reset()


def profiles():
    for phase in range(256):
        for timer in range(256):yield phase,timer,phase,(phase+timer)%4,24,((phase<<8)|timer),'all_phase_and_parent_counter_bytes'
    for coordinate in range(65536):yield 15,2,coordinate&255,2,24,coordinate,'all_region_coordinates'
    for r in range(256):
        for style in range(4):
            for index in (0,24,254,255):yield 15,r,r,style,index,(0x4B38,0x4835,0x4839,0)[style],'all_R_and_index_edges'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter()
    for phase,timer,r,style,index,coordinate,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for row in range(25):
            pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,1,0
        for row in range((0,1,2,2)[style]):memory[0xA101+64*row]=128
        if style==3:memory[0xA118]=255
        memory[0xA740],memory[0xA741]=128,128
        ix=0xA700
        for axis,value in enumerate((0x1234,0x7FFF,0xFF80)):memory[ix+axis*2],memory[ix+axis*2+1]=value&255,value>>8
        memory[ix+10],memory[ix+13],memory[ix+22]=11,index,timer
        memory[0x9BC1],memory[0x9BC2]=coordinate&255,coordinate>>8;memory[0xF3F1]=phase
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF3F0,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=PeriodicMachine(memory.banks,initial);model.periodic()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(1500):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',phase,timer,index))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
        counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%65536==0:print(str(cases)+' periodic class3 cases passed',flush=True)
    assert cases==135168 and paths['parent_state_09'] and paths['linked_unavailable'] and paths['skip_once']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),all_phase_parent_counter_products=True,
        all_65536_region_coordinates=True,all_256_R_values_with_four_list_styles_and_index_edges=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_allocator_index_region_and_reset_children_executed=True,maximum_additional_stack_bytes=2,
        complete_external_return=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPeriodicClass3StateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
