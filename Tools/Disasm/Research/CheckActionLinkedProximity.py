"""State0E, обычный индекс связи, полный класс 13, бит 4 и реальный дальний подвод."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckActionNearestCandidate import NearestMachine
from ReferenceActionClassRefresh import RefreshMachine
from ReferenceControlsPointRespawn import cp_flags,refresh
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes
from CheckActionSelectedRecordStep import arguments


class LinkedMachine(RefreshMachine,NearestMachine):
    def mark_iy(self):
        pointer=self.r[10]*256+self.r[11]
        self.put(pointer+1,128);self.put(pointer,0);self.put(pointer+24,255)
        return self.finish(7)

    def far_step(self,ratio,root):
        ix=self.r[8]*256+self.r[9];iy=self.r[10]*256+self.r[11]
        current=tuple(self.word(ix+2*k) for k in range(3));target=tuple(self.word(iy+2*k) for k in range(3))
        child=arguments(self.r,current,target);child[12]-=2;child[24]=0xAD5A
        # Учёт M1 вызова геометрии в StepRecordTargetCodes после хвостового JP обёртки.
        child[15]=refresh(child[15],1)
        self.put_word(child[12],0x6268)
        computed=geometry(child,ratio,root,return_address=0x6268)
        stepped=apply_codes(computed['registers'],self.read(ix+8),self.read(ix+9),self.read(ix+37),return_address=0xF368)
        for address,value in computed['writes']+stepped['writes']:self.put(address,value)
        self.r=stepped['registers'];self.ports=computed['ports'];self.path.append('far_geometry')
        return self

    def linked(self,ratio,root):
        ix=self.r[8]*256+self.r[9];self.r[0]=self.read(ix+11);self.m1(2)
        self.call(0xE6A7,0xF00F,self.index_address);pointer=self.r[6]*256+self.r[7]
        self.r[7]=(self.r[7]+1)&255;high=self.read(pointer+1);self.r[0:2]=[high,cp_flags(high,128)];self.m1(4)
        if high==128:self.path.append('unavailable_class_refresh');return self.refresh_class()
        code=self.read(pointer+18);self.r[3]=code;self.pair(6,pointer);self.r[0:2]=[code,cp_flags(code,19)];self.m1(9)
        if code!=19:self.path.append('wrong_class_refresh');return self.refresh_class()
        self.put_word(self.r[12]-2,pointer);self.pair(10,pointer);self.m1(3)
        self.call(0xEAE9,0xF028,self.distance);distance=self.r[0];self.r[1]=cp_flags(distance,1);self.m1(2)
        if distance>=1:
            self.call(0xF36B,0xF368,lambda:self.far_step(ratio,root));self.m1(1)
            self.r[24]=0xF0F8;return self
        marked=bool(self.read(pointer+24)&16)
        self.r[1]=((pointer>>8)&0x28)|17|(0 if marked else 0x44);self.m1(2)
        self.call(0xF03D,0xF034,self.mark_iy);self.m1(1)
        if not marked:self.path.append('near_class_refresh');return self.refresh_class()
        self.m1(1);self.r[12]-=2;self.put_word(self.r[12],0xF03A);self.r[24]=0xEA29
        self.path.append('large_effect_boundary');return self


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();depth=0;r_proved=0
    for index in range(256):
        for mode in range(4):
            for code in (*range(26),*range(128,154)):
                for bit4 in (0,16):
                    memory.recording=False
                    for page in range(8):memory.banks[page][:]=baseline[page]
                    memory.out7ffd(16)
                    for row,kind in enumerate((0,5,6,7,14,18)):
                        pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+18]=row,1,kind
                    memory[0xA740],memory[0xA741]=128,128
                    ix=0xA100;selected=0xA100+64*index
                    for axis,value in enumerate((0x1234,0x2345,0x3456)):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
                    memory[ix+18],memory[ix+11],memory[ix+21],memory[ix+22]=code,index,0 if cases&1 else 255,13 if cases&2 else 12
                    memory[ix+8],memory[ix+9],memory[ix+37]=cases*73&255,cases*109&255,(0,1,2,3,127,128,255)[cases%7]
                    if index<25:
                        for axis,delta in enumerate((0,255,65535) if mode!=3 else (256,1024,0xF000)):
                            value=(memory[ix+2*axis]+256*memory[ix+2*axis+1]+delta)&65535
                            memory[selected+2*axis],memory[selected+2*axis+1]=value&255,value>>8
                        memory[selected+18]=18 if mode==1 else 19
                        memory[selected+24]=(cases*37&0xEF)|bit4
                        if mode==0:memory[selected+1]=128
                    stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'PC':0xF009,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                    initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
                    model=LinkedMachine(memory.banks,initial);model.ports=[];model.linked(ratio,root)
                    simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
                    for _ in range(5000):
                        if simulator.registers[24] in (0xF0F8,0xEA29):break
                        simulator.run()
                    else:raise AssertionError(('нет границы',index,mode,code,bit4))
                    memory.recording=False
                    compared=[*range(25),26,27]
                    assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,index,mode,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
                    assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
                    assert trace.writes==model.ports and memory.o7ffd==16
                    for bank,offset,_ in memory.writes:
                        if bank==2 and stack-20<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                    r_proved+=1;paths.update(model.path);cases+=1
                    if cases%32768==0:print(str(cases)+' linked proximity cases passed',flush=True)
    assert cases==106496 and paths['large_effect_boundary'] and paths['far_geometry'] and paths['near_class_refresh']
    result=dict(passed=True,total_cases=cases,paths=dict(paths),all_256_indices_with_modes_and_class_aliases=True,
        exact_registers_flags_sp_and_all_ram=True,exact_R_cases=r_proved,far_geometry_R_proved=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports_compared=True,
        maximum_additional_stack_bytes=depth,large_effect_body_executed=False,common_tail_executed=False,
        boundaries=[0xF0F8,0xEA29],all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedProximityVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
