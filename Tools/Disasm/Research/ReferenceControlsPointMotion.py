"""Модель координат CB00, R считается по M1, вычисления точек не исполняют Z80."""
from pathlib import Path
import json
from functools import lru_cache
from ReferenceControlsBufferPoints import random_step
from ReferenceControlsPointRespawn import respawn,refresh

ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def opcode_costs():
    flow=json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    region=next(item for item in flow if item['name']=='Controls')
    return {i['address']:2 if i['hex'][:2] in ('cb','ed','dd','fd') else 1 for i in region['instructions']}


@lru_cache(maxsize=None)
def block_cost(start,end):
    return sum(cost for address,cost in opcode_costs().items() if start<=address<end)


class NoProgress(Exception):
    def __init__(self,entry,loop):
        self.entry,self.loop = entry,loop


class Motion:
    def __init__(self,memory,r,stack=0xBFFE):
        self.memory,self.r,self.stack = memory,r,stack
        self.writes,self.samples = [],[]
        self.b,self.c=0x36,0x9C
        self.last_respawn=None
        self.last_random=None
        self.alt_af=None
        self.work_hl,self.work_de,self.work_bc=None,None,None

    def tick(self,count):
        self.r = refresh(self.r,count)

    def path(self,start,end):
        self.tick(block_cost(start,end))

    def write(self,address,value):
        self.memory[address]=value
        self.writes.append((address,value))

    def word(self,address,value):
        self.write(address,value&255)
        self.write(address+1,value>>8)

    def sample(self,address):
        self.tick(2)
        self.samples.append((address,self.r))
        return self.r

    def call_frame(self,return_address):
        self.tick(1)
        self.word(self.stack-2,return_address)

    def rng(self,return_address):
        self.call_frame(return_address)
        seed = self.memory[0xCA8F]+256*self.memory[0xCA90]
        following,mixed,difference,_ = random_step(seed)
        self.last_random=(following,mixed,difference)
        self.word(0xCA8F,following)
        self.path(0xCA8D,0xCAB3)
        return following&255

    def replace_point(self,entry,return_address):
        self.call_frame(return_address)
        phase_address,step_address,offset_address = (0xCE17,0xCE1E,0xCE31) if entry==0xCE16 else (0xCE5E,0xCE65,0xCE78)
        phase,step,offset = self.memory[phase_address],self.memory[step_address],self.memory[offset_address]
        if not step:
            self.write(phase_address,phase^1)
            self.tick(7)
            first = (0xCE21 if phase==1 else 0xCE3F) if entry==0xCE16 else (0xCE68 if phase==1 else 0xCE84)
            self.samples.append((first,self.r))
            raise NoProgress(entry,first+2)
        result = respawn(entry,phase,step,offset,self.r)
        self.write(phase_address,result['phase'])
        first_branch = result['phase']==0
        if entry==0xCE16:
            positions = (0xCE21,0xCE33) if first_branch else (0xCE3F,0xCE53)
        else:
            positions = (0xCE68,0xCE7A) if first_branch else (0xCE84,0xCE98)
        self.samples.extend(zip(positions,(result['first_r'],result['second_r'])))
        self.r=result['r']
        self.c=step
        self.last_respawn=(result['y'],result['x'])
        return result['y'],result['x']

    def modulo(self,value,step):
        quotient,remainder = divmod(value,step)
        self.tick(4*quotient+2)
        return remainder

    def limit(self,value,maximum):
        self.tick(2)
        if value>=maximum:
            self.tick(1)
        return min(value,maximum)

    def random_x_for_y(self,return_address,positive,index):
        x=self.rng(return_address)
        # После вызова следуют INC L и сравнение нулевого X с единицей.
        self.tick(3)
        if not x:
            self.tick(1)
            x=1
        self.tick(2)
        if x>=254:
            self.tick(1)
            x-=1
        self.write(0xC501+2*index,x)
        self.tick(5)
        if index==34:
            self.tick(1)

    def translate_y(self):
        control=self.memory[0x9B95]
        self.path(0xCB00,0xCB0A)
        if not control:
            return
        self.path(0xCB0A,0xCB0D)
        positive=control<128
        magnitude=control if positive else (-control)&255
        step=((magnitude<<2)+2+(0 if positive else magnitude>>7))&255
        self.c=step
        self.path(0xCB0D,0xCB12) if positive else self.path(0xCB54,0xCB59)
        for index in range(35):
            address=0xC500+2*index
            old=self.memory[address]
            value=old+step if positive else old-step
            self.tick(3)
            if (value<256 if positive else value>=0):
                self.tick(2)
            valid=(value<95) if positive else value>=1
            if valid:
                self.write(address,value)
                self.tick(6)
                if index==34 and positive:
                    self.tick(1)
                continue
            sampled=self.sample(0xCB1A if positive else 0xCB61)&127
            self.tick(1)
            remainder=self.modulo(sampled,step)
            limited=self.limit(remainder,94)
            if positive:
                self.tick(2)
                y=(limited+self.memory[0xCB2B])&255
            else:
                self.tick(4)
                self.b=limited
                y=95-limited
            self.write(address,y)
            self.random_x_for_y(0xCB30 if positive else 0xCB79,positive,index)

    def random_y_for_x(self,right,index):
        value=self.sample(0xCBC6 if right else 0xCC11)&127
        self.tick(4)
        if not value:
            self.tick(1)
            value=1
        self.tick(2)
        if value>=95:
            self.tick(1)
            value-=64
        self.write(0xC500+2*index,value)
        self.tick(7)
        if index==34:
            self.tick(1)

    def translate_x(self):
        control=self.memory[0x9B96]
        self.path(0xCB9A,0xCBA4)
        if not control:
            return
        self.path(0xCBA4,0xCBA7)
        right=control>=128
        magnitude=(-control)&255 if right else control
        step=((magnitude<<2)+2+(magnitude>>7 if right else 0))&255
        self.c=step
        self.path(0xCBA7,0xCBAC) if right else self.path(0xCBF0,0xCBF5)
        for index in range(35):
            address=0xC501+2*index
            old=self.memory[address]
            value=old+step if right else old-step
            self.tick(3)
            if (value<256 if right else value>=0):
                self.tick(2)
            valid=value<254 if right else value>=1
            if valid:
                self.write(address,value)
                self.tick(6)
                if index==34 and right:
                    self.tick(1)
                continue
            generated=self.rng(0xCBB7 if right else 0xCC00)
            remainder=self.modulo(generated,step)
            limited=self.limit(remainder,253)
            if right:
                self.tick(2)
                x=(limited+self.memory[0xCBC4])&255
            else:
                self.tick(4)
                x=255-limited
            self.write(address,x)
            self.random_y_for_x(right,index)

    def product(self,coordinate,coefficient,exchange):
        coordinate&=255
        coefficient&=255
        a=coordinate if coordinate<128 else coordinate-256
        k=coefficient if coefficient<128 else coefficient-256
        magnitude=abs(a)*(abs(k)&127)//128+1
        raw=abs(a)*(abs(k)&127)
        flags=(magnitude&0xA8) | (0x10 if (raw//128)&15==15 else 0) | (4 if raw//128==127 else 0) | ((raw>>6)&1)
        self.alt_af=(magnitude,flags)
        negative=bool((coordinate^coefficient)&128)
        # M1 семи пар RR E/RRA, условных сложений и знаковой подготовки.
        self.tick(43+3*int(coefficient>=128)+3*int(coordinate>=128)+
            (abs(k)&127).bit_count()+5*int(negative)+int(exchange))
        return -magnitude if negative else magnitude

    def rotate(self):
        control=self.memory[0x9B97]
        self.path(0xCC38,0xCC3F)
        if not control:
            return False
        index=(-control)&255
        negative=bool(index&128)
        magnitude=(-index)&255 if negative else index
        self.path(0xCC3F,0xCC43)
        if negative:
            self.path(0xCC43,0xCC45)
        step=((magnitude<<2)+(2+(magnitude>>7) if negative else 0))&255
        self.path(0xCC45,0xCC6C)
        self.write(0xCE1E,step)
        self.write(0xCE65,step)
        first=self.memory[0x9900+index]
        second=self.memory[0x9900+((index+64)&255)]
        self.write(0xCCD2,first)
        self.write(0xCD9D,(-first)&255)
        self.write(0xCC7E,second)
        self.write(0xCD49,second)
        entry=0xCE5D if negative else 0xCE16
        if negative:
            self.path(0xCC6C,0xCC6F)
        self.word(0xCD31,entry)
        self.word(0xCDFC,entry)
        self.path(0xCC6F,0xCC78)
        for point in range(35):
            address=0xC500+2*point
            y,x=self.memory[address:address+2]
            self.tick(4)
            vertical=self.product(y-48,second,True)
            self.tick(6)
            second_product=self.product(x-128,first,False)
            vertical+=second_product
            vertical+=48
            self.work_hl,self.work_de,self.work_bc=vertical&65535,second_product&65535,0x30
            self.tick(6)
            if 0<=vertical<=255:
                self.tick(3)
                if vertical>=1:
                    self.tick(2)
            if not 1<=vertical<95:
                self.tick(1)
                ry,rx=self.replace_point(entry,0xCD33)
                self.write(address+1,rx)
                self.write(address,ry)
                self.tick(8)
                if point==34:
                    self.tick(1)
                continue
            self.write(0xCE0B,vertical)
            self.tick(6)
            horizontal=self.product(x-128,second,True)
            self.tick(6)
            fourth_product=self.product(y-48,(-first)&255,False)
            horizontal+=fourth_product
            horizontal+=128
            self.work_hl,self.work_de,self.work_bc=horizontal&65535,fourth_product&65535,0x80
            self.tick(6)
            if 0<=horizontal<=255:
                self.tick(3)
                if horizontal>=1:
                    self.tick(2)
            if not 1<=horizontal<254:
                self.tick(1)
                ry,rx=self.replace_point(entry,0xCDFE)
                self.write(address,ry)
                self.write(address+1,rx)
                self.tick(7)
            else:
                self.write(address,vertical)
                self.write(address+1,horizontal)
                self.tick(8)
            if point==34:
                self.tick(1)
        return True

    def run(self):
        self.translate_y()
        self.translate_x()
        return self.rotate()

    def registers(self,initial,rotated):
        expected=list(initial)
        a,f=(0x46,0x42) if rotated else (0,0x54)
        pointer=0xC546 if rotated else 0xC547 if self.memory[0x9B96] else 0xC501
        expected[0:4]=[a,f,self.b,self.c]
        expected[6:8]=[pointer>>8,pointer&255]
        if self.last_respawn is not None:
            y,x=self.last_respawn
            expected[4:6]=[x,y]
        if rotated:
            expected[16:24]=[*self.alt_af,self.work_bc>>8,self.work_bc&255,
                self.work_de>>8,self.work_de&255,self.work_hl>>8,self.work_hl&255]
        elif self.last_random is not None:
            following,mixed,difference=self.last_random
            expected[18:24]=[0,mixed&255,difference>>8,difference&255,following>>8,following&255]
        expected[12]=initial[12]+2
        expected[15]=self.r
        return expected
