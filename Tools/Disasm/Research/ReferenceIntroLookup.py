"""Числовая композиция 13 и 25 строк, двух обновлений масштаба и полного чередующегося кадра."""
from ReferenceIntroFrame import Frame
from ReferenceIntroIRQ import apply as irq


class Lookup(Frame):
    def sample(self,rows,table,destination,stack):
        self.word(0x6BF3,stack)
        for row in range(rows):
            for col in range(64):
                pointer=self.word(table+128*row+2*col)
                low=pointer&255;high=pointer>>8;mapped=self.read(0x9300+low)
                value=self.read(high*256+mapped)
                self.put(destination,value)
                if col!=63:destination=(destination&0xFF00)|((destination+1)&255)
            destination=(destination+1)&65535
        self.r[0:2]=[value,0x42|(self.r[1]&1)]
        self.set_pair(2,destination);self.set_pair(4,high*256+mapped);self.set_pair(6,0x9300+low)
        self.r[9]=0;self.r[12]=stack+2
    def scale(self,stack):
        warmup=max(1,self.read(0x6C22)-1);self.put(0x6C22,warmup)
        if warmup>1:
            ramp=min(63,self.read(0x6C2E)+1);self.put(0x6C2E,ramp);selected=39+ramp//2
        else:
            index=(self.read(0x6C3F)+1)%40;self.put(0x6C3F,index);selected=56+self.read(0x6C62+index)
        pointer=0xF000+16*selected;self.word(0x6BB2,pointer)
        self.r[0:2]=[selected,0x20];self.set_pair(4,0xF000);self.set_pair(6,pointer)
        self.r[12]=stack+2
    def present_lookup(self,phase,origin):
        # Восстановление CPU SP, первоначальный входной SP ещё указывает на перенесённые данные A800.
        stack=self.word(0x6BBD);self.r[12]=stack
        self.r[9]=13;self.set_pair(6,0xAD00);self.set_pair(2,0x8000)
        self.word(stack-2,0x6BCB);self.sample(13,0xAD00,0x8000,stack-2)
        # Настоящий CALL ожидания после первых 13 строк, числовые эффекты ROM рассчитаны отдельно.
        self.word(stack-2,0x6BCE);self.r[12]=stack-2
        ports=irq(self.read,self.put,self.r,0x6A15)
        self.r[12]=stack;self.r[26]=0
        self.word(stack-2,0x6BD1);self.scale(stack-2)
        self.r[9]=25;self.set_pair(6,0xB380);self.set_pair(2,0x8340)
        self.word(stack-2,0x6BDD);self.sample(25,0xB380,0x8340,stack-2)
        self.word(stack-2,0x6BE0);self.scale(stack-2)
        ports+=self.present(phase,origin)
        return ports
