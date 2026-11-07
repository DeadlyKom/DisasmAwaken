"""State10, таймер, подготовленный контекст и два полных общих продолжения."""
from ReferenceActionSpawnWindow import SpawnWindowMachine
from ReferenceControlsPointRespawn import cp_flags
from CheckActionMissileConsume import dec_flags


class TimedLinkedMachine(SpawnWindowMachine):
    def prepare_linked(self):
        ix=self.r[8]*256+self.r[9];index=self.read(ix+11);pointer=0xA780 if index==255 else 0xA100+64*index
        self.put_word(0xE796,pointer);cost=11 if index==255 else 23
        if index!=255:self.put_word(self.r[12]-2,0xE770)
        high=self.read(pointer+1);self.r[0:2]=[high,cp_flags(high,128)];self.pair(6,pointer+1)
        if high!=128:
            for address,offset in ((0xF1ED,0),(0xF1F0,2),(0xF1FE,4)):self.put_word(address,self.word(ix+offset))
            self.pair(6,self.word(ix+4));cost+=16
        else:self.path.append('prepare_unavailable')
        return self.finish(cost)

    def timed_linked(self,ops):
        self.rendered=False;ix=self.r[8]*256+self.r[9];old=self.read(ix+23);timer=(old-1)&255
        self.r[0:2]=[timer,dec_flags(old,self.r[1]&1)];self.put(ix+23,timer);self.m1(6)
        if not timer:
            self.r[0]=self.read(ix+25);self.put(ix+10,self.r[0]);self.m1(5)
            self.path.append('timer_expired');self.r[24]=0xF0F8;return self
        self.call(0xE761,0xF3DD,self.prepare_linked);self.m1(1)
        if self.r[1]&64:self.r[24]=0xF0F8;return self
        self.call(0xEB72,0xF3E3,lambda:self.stream(0));low=self.r[7]
        self.r[0:2]=[low,cp_flags(low,self.read(ix+17))];self.m1(4)
        if low>=self.read(ix+17):return self.spawn_window()
        self.call(0xE804,0xF3ED,lambda:self.linked_overlay(ops));self.m1(1)
        self.path.append('timed_overlay_return');self.r[24]=0xF0F8;return self
