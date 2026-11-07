"""State01, независимая композиция выбора строки, геометрии и переходов состояния."""
from CheckActionNearestCandidate import NearestMachine
from CheckActionTargetTransition import run_model as target_transition
from ReferenceActionWideTargetStep import evaluate as wide_step
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import cp_flags


class WideVectorMachine(NearestMachine):
    def wide_state(self,ratio,root):
        ix=self.r[8]*256+self.r[9];index=self.read(ix+38);pointer=0x9B27+12*index
        self.r[2]=0;self.pair(4,12);self.pair(10,pointer);self.m1(6+3*(index+1))
        values=tuple(self.word(pointer+4*k)+65536*self.word(pointer+4*k+2) for k in range(3))
        words=tuple(self.word(ix+2*k) for k in range(3))
        self.m1(1);self.r[12]-=2;self.put_word(self.r[12],0xF0D0)
        child=wide_step(self.r,values,words,(self.read(ix+8),self.read(ix+9)),self.read(ix+37),ratio,root)
        for address,value in child['writes']:self.put(address,value)
        self.r=child['registers'];self.r[24]=0xF0D0;self.ports=child['ports']
        self.call(0xE91E,0xF0D3,lambda:target_transition(self));self.m1(1)
        if self.r[1]&1:self.path.append('transition_carry');self.r[24]=0xF0F8;return self
        mode=self.read(0x9B83);self.r[0:2]=[mode,logical_flags(mode)|16];self.m1(3)
        if not mode:self.path.append('zero_mode');self.r[24]=0xF0F8;return self
        code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,0)];self.m1(4)
        if not code:self.path.append('zero_class');self.r[24]=0xF0F8;return self
        self.r[1]=cp_flags(code,5);self.m1(2)
        if code>=5:self.path.append('class_ge_5');self.r[24]=0xF0F8;return self
        self.call(0xEBB8,0xF0EA,lambda:self.stream(2));high=self.r[6]
        self.r[0:2]=[high,cp_flags(high,65)];self.m1(3)
        if high!=65:self.path.append('random_high_reject');self.r[24]=0xF0F8;return self
        low=self.r[7];self.r[0:2]=[low,cp_flags(low,90)];self.m1(3)
        if low<90:self.path.append('random_low_reject')
        else:self.put(ix+10,12);self.m1(2);self.path.append('state_0C')
        self.r[24]=0xF0F8;return self
