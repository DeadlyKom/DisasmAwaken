"""F255, компоненты текущей записи, её индекс и выбор параметра по биту 3."""
from ReferenceActionClass17Spawn import Class17Machine
from CheckActionRecordIndex import decode


class CurrentLinkMachine(Class17Machine):
    def ix_index(self):
        stack=self.r[12];pointer=self.r[8]*256+self.r[9]
        self.put_word(stack-2,self.r[6]*256+self.r[7]);self.put_word(stack-4,pointer);self.put_word(stack-4,0xE6BC)
        index,flags,_=decode(pointer);self.r[0:2]=[index,flags];return self.finish(16)

    def spawn_current_link(self):
        ix=self.r[8]*256+self.r[9];self.r[3]=self.read(ix+11)
        for pair,offset in ((22,0),(20,2),(18,4)):self.pair(pair,self.word(ix+offset))
        self.r[16:18]=[0,0x44];self.m1(19)
        self.call(0xE6B5,0xF272,self.ix_index);self.r[2]=self.r[0]
        marked=bool(self.read(ix+24)&8);self.r[0]=50 if marked else 10;self.m1(6+int(marked))
        self.path.append('parameter_32' if marked else 'parameter_0A')
        return self.class17_spawn()
