"""Числовая композиция кадрового чередования, реальная последовательность источников и назначений."""
from ReferenceIntroIRQ import apply as irq


class Frame:
    def __init__(self,read,put,registers):
        self.read,self.put,self.r=read,put,list(registers)
    def word(self,address,value=None):
        if value is None:return self.read(address)+256*self.read(address+1)
        self.put(address,value&255);self.put(address+1,value>>8)
    def set_pair(self,index,value):self.r[index],self.r[index+1]=value>>8,value&255
    def scatter(self,table,stack,shift):
        self.word(0x6831,table);self.word(0x68A1,stack)
        bc=self.r[2]*256+self.r[3]
        for row in range(38):
            source=self.word(table+4*row);destination=self.word(table+4*row+2)
            if shift:destination=(((destination>>8)+1)&255)*256+(destination&255)
            self.word(0x6831,table+4*row+4)
            for col in range(32):
                pointer=self.word(source+2*col)
                self.put(destination,self.read(pointer))
                hl=(pointer+1)&65535;destination=(destination+1)&65535;bc=(bc-1)&65535
        self.r[0:2]=[0,0x42|(self.r[1]&1)]
        self.set_pair(2,bc);self.set_pair(4,destination);self.set_pair(6,hl)
        self.r[12]=stack+2
    def attributes(self,source,stack,origin):
        self.word(0x692A,stack)
        for row in range(8):
            for col in range(8):self.put((origin+row)*256+origin+col,self.read(source+8*row+col))
        self.set_pair(6,self.word(source+62));self.r[12]=stack+2
    def present(self,phase,origin):
        stack=self.r[12];new_phase=(phase+128)&255
        ports=[];initial_iff=self.r[26];initial_time=self.r[25]
        self.r[0]=phase
        # При активном окне IRQ уже разрешённый IFF допускает прерывание после первого LD A.
        if initial_iff and initial_time==0:ports+=irq(self.read,self.put,self.r,0x67F3)
        flags=(new_phase&0xA8)|(0x40 if new_phase==0 else 0)|(5 if phase>=128 else 0)
        self.r[0:2]=[new_phase,flags]
        # В проверенном конце кадра следующий ADD попадает в активное окно до записи фазы.
        if initial_iff and initial_time==69880:ports+=irq(self.read,self.put,self.r,0x67F5)
        # Обновление кодового операнда и двух байтов вставки, затем настоящий кадр вызова ожидания.
        self.put(0x67F2,new_phase)
        shift=new_phase==0;patch=0x1400 if shift else 0
        self.word(0x6839,patch)
        self.set_pair(6,patch)
        self.word(stack-2,0x6805)
        self.r[12]=stack-2
        ports+=irq(self.read,self.put,self.r,0x6A15)
        self.r[12]=stack;self.r[26]=0
        # Первая половина, матрица атрибутов, затем хвостовая вторая половина без дополнительного CALL.
        self.word(stack-2,0x680D if shift else 0x681E)
        self.scatter(0x6100 if shift else 0x6000,stack-2,shift)
        self.word(stack-2,0x6813 if shift else 0x6824)
        self.attributes(0x60C0 if shift else 0x61C0,stack-2,origin)
        self.scatter(0x6000 if shift else 0x6100,stack,shift)
        self.r[24]=0x3FFF
        return ports
