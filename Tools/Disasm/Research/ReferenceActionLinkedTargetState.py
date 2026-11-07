"""State02 и общая цепочка F1EC, исходные ветви, реальные числовые дети и косвенный хвост."""
from ReferenceActionTimedLinkedState import TimedLinkedMachine
from ReferenceActionClassRefresh import RefreshMachine
from ReferenceActionClass19Spawn import Class19Machine
from ReferenceActionLinkedMotionGate import MotionGateMachine
from CheckActionTargetTransition import ready
from CheckActionAcquireLocalState import run_model as acquire_local
from CheckActionRecordSearch import inc_flags
from CheckActionMissileConsume import dec_flags
from CheckActionVertexCodes import logic_flags
from CheckMarketAccess import add16_flags
from ReferenceControlsPointRespawn import cp_flags


class LinkedTargetMachine(TimedLinkedMachine,RefreshMachine,Class19Machine,MotionGateMachine):
    def common(self):self.r[24]=0xF0F8;return self

    def class8_spawn(self):
        ix=self.r[8]*256+self.r[9];code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,8)]
        if code!=8:return self.finish(4)
        self.r[0]=2;self.m1(5);return self.spawn()

    def spawn_continue(self):
        self.call(0xF255,0xF252,self.spawn_current_link);self.m1(1);return self.common()

    def motion_overlay(self,ratio,root,ops,entry='prepared'):
        ix=self.r[8]*256+self.r[9]
        if entry=='prepared':
            for pair,address in ((4,0xF1ED),(2,0xF1F0),(6,0xAF48),(22,0xAF56),(20,0xAF69),(18,0xF1FE)):
                self.pair(pair,self.word(address))
            self.m1(9)
        if entry!='refresh':
            self.call(0x624B,0xF204,lambda:self.motion_gate(ratio,root,0xF204))
            high,low=self.r[6:8];value=max(high,low);self.r[0:2]=[value,cp_flags(value,6)];self.m1(5+int(high<low))
            if value>=6:self.path.append('motion_delta_reject');return self.common()
            self.call(0xEB72,0xF211,lambda:self.stream(0));value=self.r[7]
            self.r[0:2]=[value,cp_flags(value,self.read(ix+17))];self.m1(4)
            if value>=self.read(ix+17):return self.spawn_window()
            self.call(0xE804,0xF21A,lambda:self.linked_overlay(ops));self.m1(1)
            if not self.r[1]&1:self.m1(1);return self.common()
        self.call(0x64DF,0xF21F,self.dispatch_class);self.m1(1);self.path.append('common_class_refresh');return self.common()

    def target_state(self,ratio,root,ops,flat,entry=0xF138):
        self.rendered=False;self.ports=[];self.boundary='common';ix=self.r[8]*256+self.r[9]
        linked=self.read(ix+11)
        if entry==0xF138:
            self.r[0:2]=[(linked+1)&255,inc_flags(linked,self.r[1]&1)];self.m1(4)
        if linked==255 or entry==0xF142:
            if entry==0xF142:
                gate=not bool(self.r[1]&1);self.m1(1)
            else:
                self.m1(2);value=self.r[15];self.r[0:2]=[value,cp_flags(value,120)];self.m1(2);gate=value>=120
            if gate:
                self.call(0xEA15,0xF147,lambda:ready(self));self.m1(1)
                if not self.r[1]&64:
                    self.call(0xE9C2,0xF14C,self.nearest);self.put(ix+10,14);self.put(ix+11,self.r[0]);self.m1(5)
                    self.path.append('unlinked_nearest');return self.common()
            self.call(0x64DF,0xF159,self.dispatch_class)
            linked=self.read(ix+11);self.r[0:2]=[(linked+1)&255,inc_flags(linked,self.r[1]&1)];self.m1(4)
            if linked!=255:return self.common()
            saved=self.read(ix+22);self.r[0:2]=[saved,cp_flags(saved,2)];self.m1(4)
            if saved==2:self.path.append('saved_state2_stop');return self.common()
            offset=(saved*2)&255;flags=logic_flags(offset)|int(bool(saved&128));pointer=0xEF50+offset
            target=self.word(pointer);self.pair(4,0xEF50);self.pair(6,target);self.r[0:2]=[target&255,add16_flags(offset,0xEF50,flags)]
            self.m1(11);self.r[24]=target;self.boundary='indirect';self.path.append('saved_state_indirect');return self
        self.call(0xE863,0xF179,self.class8_spawn);code=self.read(ix+18)
        self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
        if code==8:self.path.append('tail_state12');self.boundary='outer_return';return acquire_local(self,flat)
        parameter=self.read(ix+19);self.r[0:2]=[parameter,cp_flags(parameter,35)];self.m1(4)
        prepare=parameter>=35
        if not prepare:
            self.m1(2);random=self.r[15];self.r[0:2]=[random,cp_flags(random,100)];self.r[3]=random;self.m1(3)
            if random>=100:
                code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
                if code!=8:
                    self.r[1]=cp_flags(code,9);self.m1(2)
                    if code!=9:self.put(ix+10,6);self.m1(3);self.path.append('state6');return self.common()
            self.r[0:2]=[random,cp_flags(random,50)];self.m1(3);prepare=random>=50
            if not prepare:
                code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,3)];self.m1(4);prepare=code==3
                if not prepare:
                    self.r[1]=cp_flags(code,2);self.m1(2);prepare=code==2
                if not prepare:
                    self.r[1]=cp_flags(code,8);self.m1(2)
                    self.call(0x6417,0xF1BE,self.class19_spawn);code=self.read(ix+18)
                    self.r[0:2]=[code,cp_flags(code,8)];self.m1(4)
                    if code!=8:self.put(ix+10,15);self.m1(3)
                    self.path.append('class19_then_state0F');return self.common()
        self.call(0xE761,0xF1D0,self.prepare_linked);self.m1(1)
        if self.r[1]&64:self.put(ix+11,255);self.m1(3);self.path.append('lost_link');return self.common()
        self.call(0xE794,0xF1DC,self.linked_vectors);self.m1(1)
        if self.r[1]&1:return self.motion_overlay(ratio,root,ops,'refresh')
        old=self.read(ix+20);value=(old-1)&255;self.r[0:2]=[value,dec_flags(old,self.r[1]&1)];self.m1(4)
        if not value&128:
            self.put(ix+20,value);self.m1(3)
            if not value:self.path.append('counter_expired_spawn');return self.spawn_continue()
        return self.motion_overlay(ratio,root,ops)
