"""State08, движение к записи, связь, текстовая очередь и полный большой эффект."""
from ReferenceActionLargeClassEffect import LargeClassMachine
from ReferenceActionSpawnCurrentLink import CurrentLinkMachine
from ReferenceActionLinkedMotionGate import MotionGateMachine
from ReferenceControlsTextQueue import insert,QUEUE,PRODUCER
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags
from CheckActionRecordIndex import add_flags
from CheckActionRecordSearch import inc_flags


class ArrivalMachine(LargeClassMachine,CurrentLinkMachine,MotionGateMachine):
    def approach(self):
        old=self.r[6]*256+self.r[7];target=self.r[2]*256+self.r[3];delta=(old-target)&65535
        negative=bool(delta&32768);magnitude=(-delta)&65535 if negative else delta
        step=magnitude//8 if magnitude<256 else 180;signed=step if negative else (-step)&65535
        residual=(delta+signed)&65535;high=residual>>8;folded=high^255 if high&128 else high
        aggregate=folded|self.r[19];self.pair(6,(old+signed)&65535);self.pair(4,signed)
        self.r[0:2]=[aggregate,logic_flags(aggregate)];self.r[19]=aggregate
        return self.finish(32+9*int(magnitude<256)+int(bool(high&128)))

    def queue_bank1(self,return_address):
        saved=list(self.r);stack=self.r[12];value=self.r[4]*256+self.r[5]
        af=self.r[0]*256+self.r[1];bc=self.r[2]*256+self.r[3];hl=self.r[6]*256+self.r[7]
        for address,word in ((stack-2,af),(stack-4,bc),(stack-6,hl),(stack-8,0x6048),(stack-10,bc),
                             (stack-8,0x604B),(stack-10,hl),(stack-12,bc),(stack-14,0x1100|self.r[1])):
            self.put_word(address,word)
        virtual={a:self.banks[1][a&0x3FFF] for a in range(QUEUE,QUEUE+34)}
        virtual[PRODUCER],virtual[PRODUCER+1]=self.banks[1][PRODUCER&0x3FFF],self.banks[1][(PRODUCER+1)&0x3FFF]
        result=insert(virtual,value)
        for address,byte in result['writes']:self.put_bank(1,address,byte)
        self.put_word(stack-8,0x6050);self.put_word(stack-10,bc)
        cost=9
        for address in result['probes']:
            kind=virtual[address];cost+=3 if kind==1 else 7 if kind==0 else 8
        cost+=6*int(result['accepted'])+int(not result['accepted'] and virtual[result['probes'][-1]]==0)
        self.r=saved;self.m1(24+cost);self.r[12]+=2;self.r[24]=return_address
        self.ports.extend(((0x7FFD,17),(0x7FFD,16)));self.path.append('text_accepted' if result['accepted'] else 'text_dropped')
        return self

    def notify(self,text,return_address):
        stack=self.r[12];de=self.r[4]*256+self.r[5];self.put_word(stack-2,de);self.r[12]-=2
        self.pair(4,text);self.m1(2);self.call(0x6040,return_address,lambda:self.queue_bank1(return_address))
        self.r[12]+=2;self.pair(4,de);self.m1(1)

    def effect_tail(self,rom):
        old_ix=self.r[8]*256+self.r[9];target=self.r[4]*256+self.r[5]
        self.put_word(self.r[12]-2,old_ix);self.r[12]-=2;self.pair(8,target);self.m1(6)
        self.call(0xEA29,0xF667,lambda:self.large_class_effect(rom));self.r[12]+=2;self.pair(8,old_ix);self.m1(2)
        return self.finish(1)

    def arrival(self,rom):
        self.ports=[];ix=self.r[8]*256+self.r[9];self.r[0]=self.read(ix+15);self.m1(2)
        self.call(0xE69E,0xF585,self.select_iy);iy=self.r[10]*256+self.r[11]
        self.put(iy+12,self.read(iy+12)|2);self.r[0]=self.read(ix+13);self.put(iy+21,self.r[0]);self.m1(6)
        self.call(0xE6B5,0xF592,self.ix_index);self.put(iy+11,self.r[0]);self.m1(2)
        self.r[3]=self.read(iy);high=self.read(iy+1);self.r[0:2]=[high,cp_flags(high,128)];self.m1(6)
        if high==128:
            value=self.read(ix+17);self.r[0:2]=[value,logic_flags(value)|16];self.m1(4)
            if value:self.notify(0xF248,0xF5AC)
            self.pair(4,ix);self.m1(5);self.path.append('target_missing_effect_current');return self.effect_tail(rom)
        self.r[2]=high;self.r[19]=0;self.m1(4)
        for axis,ret in ((0,0xF5C2),(1,0xF5D7),(2,0xF5EC)):
            if axis:
                self.pair(2,self.word(iy+2*axis));self.m1(4)
            self.pair(6,self.word(ix+2*axis));self.m1(4)
            self.call(0x6311,ret,self.approach)
            if axis<2:self.put_word(ix+2*axis,self.r[6]*256+self.r[7]);self.m1(4)
        self.pair(4,iy);aggregate=self.r[19];self.r[0:2]=[aggregate,logic_flags(aggregate)|16];self.m1(9)
        if aggregate:
            self.put_word(ix+4,self.r[6]*256+self.r[7]);self.m1(4)
            for offset,amount in ((7,1),(8,2),(9,3)):
                for _ in range(amount):
                    old=self.read(ix+offset);self.put(ix+offset,(old+1)&255);self.r[1]=inc_flags(old,0);self.m1(2)
            self.pair(6,0)
            for address in (0xE5B0,0xE5CF,0xE5EA):self.put_word(address,0)
            self.path.append('approach_far');return self.finish(5)
        self.r[0]=self.read(ix+15);self.m1(2);self.call(0xE6A7,0xF621,self.index_address)
        pointer=self.r[6]*256+self.r[7];state=self.read(pointer+10);self.pair(6,pointer+10)
        self.r[0:2]=[(state+1)&255,inc_flags(state,0)];self.m1(6)
        if state!=255:
            self.call(0xF394,0xF62C,lambda:self.mark_current());self.path.append('current_released_at_arrival')
        self.put(iy+12,self.read(iy+12)|4);value=self.read(ix+17)
        self.r[0:2]=[value,logic_flags(value)|16];self.m1(6)
        if value:
            self.notify(0xF293,0xF63D);code=self.read(iy+18)
            for compared,cost in ((0,4),(5,2),(6,2),(7,2)):
                self.r[0:2]=[code,cp_flags(code,compared)];self.m1(cost)
                if code==compared:
                    self.put_word(self.r[12]-2,self.r[6]*256+self.r[7]);self.put_word(0x9BCE,(self.word(0x9BCE)+1)&65535)
                    self.m1(5);self.path.append('arrival_counter_incremented');break
        self.path.append('approach_near_effect_target');return self.effect_tail(rom)

    def mark_current(self):
        ix=self.r[8]*256+self.r[9];self.put(ix+1,128);self.put(ix,0);self.put(ix+24,255)
        return self.finish(7)
