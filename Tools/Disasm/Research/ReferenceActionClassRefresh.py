"""F003, композиция исходного диспетчера со всеми одиннадцатью различными целями."""
from ReferenceActionClassHandlers import ClassMachine,ENTRIES
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import cp_flags


class RefreshMachine(ClassMachine):
    def class9(self):
        ix=self.r[8]*256+self.r[9];saved=self.read(ix+22)
        if saved==13:
            self.r[0:2]=[13,cp_flags(13,13)];self.put(ix+10,13);return self.finish(7)
        self.m1(6);value=self.r[15];self.r[0:2]=[value,cp_flags(value,112)]
        self.put(ix+10,1);self.put(ix+11,255);return self.finish(6)

    def dispatch_class(self):
        ix=self.r[8]*256+self.r[9];raw=self.read(ix+18);kind=raw&127
        assert kind<26,'граница исходной таблицы не проверяется кодом, но обязательна для этого договора'
        target=self.word(0x64F0+2*kind);self.pair(6,target);self.pair(2,0x64F0)
        self.r[0:2]=[target&255,0x20|(logical_flags((raw*2)&255)&0xC4)];self.m1(13)
        self.path.append('class_'+str(kind))
        if kind==0:return self.class0()
        if kind in ENTRIES:return self.handle(kind)
        if kind==9:return self.class9()
        return self.finish(1)

    def refresh_class(self):
        self.call(0x64DF,0xF006,self.dispatch_class);self.m1(1);self.r[24]=0xF0F8
        return self
