"""Композиция замкнутого обхода рёбер с математическими помощниками всех табличных случаев."""
from ReferenceActionClipping import Clipping
from ReferenceControlsPointRespawn import cp_flags


class Polygon(Clipping):
    def load_second(self,index):
        address=0x8E00+index
        for offset in (0,2):self.word(0xCF1B+offset,self.word(address+offset))
        self.byte(0xCF1F,self.byte(address+4))

    def copy_first(self):
        for offset in (0,2):self.word(0xCF0B+offset,self.word(0xCF1B+offset))
        self.byte(0xCF0F,self.byte(0xCF1F))

    def polygon(self):
        pointer=self.pair(6);count=self.r[2];assert 1<=count<=15
        # Инициализация размера, запрета углов и прежних отметок соответствует настоящему входу C000.
        self.byte(0xCF03,0);self.byte(0x9BA3,0);self.byte(0xCF07,0)
        self.push(pointer);self.load_second(self.byte((pointer+count-1)&65535))
        for _ in range(count):
            self.copy_first();pointer=self.pop();index=self.byte(pointer);pointer=(pointer+1)&65535
            self.push(pointer);self.push(self.pair(2));self.load_second(index)
            code=((~self.byte(0xCF0F))&240)|(self.byte(0xCF1F)&15)
            target=self.byte(0xCF00+code)+256*self.byte(0xD000+code)
            self.r[0:2]=[code,0x90];self.pair(4,0xC071);self.pair(6,target)
            self.push(0xC071);self.r[self.pc]=target;self.run(stop=0xC071)
            if self.special:return
            self.pair(2,self.pop());self.r[2]=(self.r[2]-1)&255
            if self.r[2]==0:
                self.pair(6,self.pop());size=self.byte(0x9BA3);self.r[0:2]=[size,cp_flags(size,6)]
                self.r[self.pc]=self.pop();return
        raise AssertionError('число полигональных рёбер')
