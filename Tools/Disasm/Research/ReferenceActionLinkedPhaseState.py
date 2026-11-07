"""State05, иное окно R, поздний класс 8 и ранее сохранённые глобальные слова движения."""
from ReferenceActionLinkedTargetState import LinkedTargetMachine
from ReferenceActionRandomPhaseStep import RandomPhaseMachine
from CheckActionTargetTransition import ready
from CheckActionAcquireLocalState import run_model as acquire_local
from CheckActionRecordSearch import inc_flags
from CheckActionMissileConsume import dec_flags
from CheckActionVertexCodes import logic_flags
from CheckMarketAccess import add16_flags
from ReferenceControlsPointRespawn import cp_flags


class LinkedPhaseMachine(LinkedTargetMachine,RandomPhaseMachine):
    def phase_target_state(self,ratio,root,ops,flat):
        self.rendered=False;self.ports=[];self.boundary='common';ix=self.r[8]*256+self.r[9]
        linked=self.read(ix+11);self.r[0:2]=[(linked+1)&255,inc_flags(linked,self.r[1]&1)];self.m1(4)
        if linked==255:
            self.m1(2);value=self.r[15];self.r[0:2]=[value,cp_flags(value,126)];self.m1(2)
            if value>=126:
                self.call(0xEA15,0xF298,lambda:ready(self));self.m1(1)
                if not self.r[1]&64:
                    self.call(0xE9C2,0xF29D,self.nearest);self.put(ix+10,14);self.put(ix+11,self.r[0]);self.m1(5)
                    self.path.append('unlinked_nearest');return self.common()
            self.call(0x64DF,0xF2AA,self.dispatch_class)
            linked=self.read(ix+11);self.r[0:2]=[(linked+1)&255,inc_flags(linked,self.r[1]&1)];self.m1(4)
            if linked!=255:return self.common()
            saved=self.read(ix+22);self.r[0:2]=[saved,cp_flags(saved,5)];self.m1(4)
            if saved==5:self.path.append('saved_state5_stop');return self.common()
            offset=(saved*2)&255;flags=logic_flags(offset)|int(bool(saved&128));target=self.word(0xEF50+offset)
            self.pair(4,0xEF50);self.pair(6,target);self.r[0:2]=[target&255,add16_flags(offset,0xEF50,flags)]
            self.m1(11);self.r[24]=target;self.boundary='indirect';self.path.append('saved_state_indirect');return self
        parameter=self.read(ix+19);self.r[0:2]=[parameter,cp_flags(parameter,35)];self.m1(4);prepare=parameter>=35
        if not prepare:
            self.m1(2);random=self.r[15];self.r[0:2]=[random,cp_flags(random,100)];self.r[3]=random;self.m1(3)
            if random>=100:
                code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
                if code!=8:
                    self.r[1]=cp_flags(code,9);self.m1(2)
                    if code!=9:self.put(ix+10,6);self.m1(3);self.path.append('state6');return self.common()
            self.r[0:2]=[random,cp_flags(random,40)];self.m1(3);prepare=random<40
            if not prepare:
                code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,3)];self.m1(4);prepare=code==3
                if not prepare:self.r[1]=cp_flags(code,2);self.m1(2);prepare=code==2
                if not prepare:
                    self.r[1]=cp_flags(code,8);self.m1(2)
                    if code==8:
                        blocked=bool(self.read(ix+24)&4);self.r[1]=(self.r[1]&1)|0x30|(0 if blocked else 0x44);self.m1(3);prepare=blocked
                    if not prepare:
                        self.call(0x6417,0xF305,self.class19_spawn);code=self.read(ix+18)
                        self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
                        if code!=8:self.put(ix+10,15);self.m1(3)
                        self.path.append('class19_then_phase_state');return self.common()
        self.call(0xE761,0xF317,self.prepare_linked);self.m1(1)
        if self.r[1]&64:self.put(ix+11,255);self.m1(3);self.path.append('lost_link');return self.common()
        old=self.read(ix+20);value=(old-1)&255;self.r[0:2]=[value,dec_flags(old,self.r[1]&1)];self.m1(4)
        if not value&128:
            self.put(ix+20,value);self.m1(3)
            if not value:self.path.append('counter_expired_spawn');return self.spawn_continue()
        self.call(0xE863,0xF330,self.class8_spawn);code=self.read(ix+18)
        self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
        if code==8:self.path.append('tail_state12');self.boundary='outer_return';return acquire_local(self,flat)
        self.call(0x6201,0xF33B,self.random_phase)
        for pair,address in ((4,0xAF48),(2,0xAF56),(6,0xF1ED),(22,0xF1F0),(20,0xF1FE),(18,0xAF69)):
            self.pair(pair,self.word(address))
        self.m1(13);self.path.append('uses_prior_global_inputs')
        return self.motion_overlay(ratio,root,ops,'motion')
