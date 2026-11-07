"""F222, исходные случайные пороги и неограниченное чтение таблицы по полному классу."""
from ReferenceActionSpawnCurrentLink import CurrentLinkMachine
from ReferenceActionLinkedOverlay import LinkedOverlayMachine
from ReferenceControlsPointRespawn import cp_flags
from CheckMarketAccess import add16_flags


class SpawnWindowMachine(CurrentLinkMachine,LinkedOverlayMachine):
    def spawn_window(self):
        ix=self.r[8]*256+self.r[9];a=self.r[0];self.r[1]=cp_flags(a,240);self.m1(2)
        if a!=240:self.path.append('window_low_reject');self.r[24]=0xF0F8;return self
        a=self.r[6];self.r[0:2]=[a,cp_flags(a,95)];self.m1(3)
        if a<95:self.path.append('window_high_reject');self.r[24]=0xF0F8;return self
        code=self.read(ix+18);self.r[0:2]=[code,cp_flags(code,9)];self.m1(4)
        if code==9:self.path.append('window_class9_reject');self.r[24]=0xF0F8;return self
        value=self.read(ix+20);self.r[0:2]=[value,(value&0xA8)|(64 if not value else 0)|(4 if value.bit_count()%2==0 else 0)|16];self.m1(4)
        if value:self.path.append('window_counter_reject');self.r[24]=0xF0F8;return self
        self.call(0xF255,0xF23F,self.spawn_current_link)
        code=self.read(ix+18);self.pair(2,code);pointer=0xF280+code
        self.r[1]=add16_flags(0xF280,code,self.r[1]);self.pair(6,pointer);self.r[0]=self.read(pointer)
        self.put(ix+20,self.r[0]);self.m1(9);self.r[24]=0xF0F8;self.path.append('window_spawn_attempted')
        return self
