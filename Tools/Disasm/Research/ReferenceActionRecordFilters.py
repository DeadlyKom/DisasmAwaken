"""Числовые договоры генератора, фильтров и подстановки, без интерпретации инструкций Z80."""
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh,cp_flags
from CheckActionRecordSearch import inc_flags
from ActionRandomStreamLayout import STREAMS

STREAM_POINTERS={number:pointer for number,_,pointer in STREAMS}


class Machine:
    def __init__(self,banks,registers):
        self.banks=[bytearray(b) for b in banks];self.r=list(registers)
        self.writes=[];self.m1_count=0;self.path=[]

    def bank(self,address):
        assert 0x4000<=address<=0xFFFF
        return 5 if address<0x8000 else 2 if address<0xC000 else 0

    def read(self,address):return self.banks[self.bank(address)][address&0x3FFF]
    def word(self,address):return self.read(address)+256*self.read(address+1)
    def pair(self,index,value):self.r[index:index+2]=[value>>8,value&255]
    def m1(self,count):self.r[15]=refresh(self.r[15],count);self.m1_count+=count

    def put(self,address,value):
        page=self.bank(address);offset=address&0x3FFF
        self.banks[page][offset]=value;self.writes.append((page,offset,value))

    def put_word(self,address,value):self.put(address,value&255);self.put(address+1,value>>8)

    def finish(self,m1=0):
        self.m1(m1);stack=self.r[12];self.r[24]=self.word(stack);self.r[12]=stack+2
        return self

    def call(self,entry,return_address,procedure):
        self.m1(1);self.r[12]-=2;self.put_word(self.r[12],return_address);self.r[24]=entry
        procedure();assert self.r[24]==return_address

    def stream(self,number):
        pointer=STREAM_POINTERS[number];stack=self.r[12]
        value=step(self.word(pointer),self.read(pointer+2))
        self.put_word(stack-2,pointer+2);self.put(pointer+2,value['fold']);self.put_word(pointer,value['word'])
        self.put_word(stack-2,value['word']);self.pair(6,value['word']);self.r[0:2]=[value['fold'],value['flags']]
        self.r[18:24]=[0,value['mixed_low']&255,value['word']>>8,value['word']&255,pointer>>8,pointer&255]
        self.path.append('stream_'+str(number));return self.finish(66)

    def filtered(self,entry):
        assert entry in (0xE6E2,0xE70D,0xE729,0xE745)
        stack=self.r[12]
        if entry==0xE6E2:
            self.call(0xEBB1,0xE6E5,lambda:self.stream(10));low=self.r[7]
            self.r[0:2]=[26,0x0A|int(low<160)];self.m1(6)
            if low>=160:self.path.append('random_gate_26');return self.finish()
        self.m1(3);self.pair(2,64);pointer=0xA100
        for _ in range(1024):
            # Поиск по фактическим записям до активной строки либо маркера, лимит здесь защищает только модель.
            self.put_word(stack-2,0xE6F7 if entry==0xE6E2 else entry+10);self.m1(1)
            while self.read(pointer+1)==128 and self.read(pointer)!=128:
                self.m1(10);pointer=(pointer+64)&65535
            self.pair(10,pointer)
            if self.read(pointer+1)==128:
                self.r[0:2]=[128,0x42];self.path.append('marker');return self.finish(12)
            code=self.read(pointer+18);self.r[5]=code
            first=5 if entry==0xE745 else 6
            comparison_cost=(6 if code==0 else 8 if code==18 else 10) if entry==0xE6E2 else (6 if code==first else 8)
            self.m1(6+comparison_cost)
            accepted=(1<=code<=15 or code==18) if entry==0xE6E2 else code not in (6,7) if entry==0xE70D else code in (6,7) if entry==0xE729 else code in (5,14)
            if not accepted:pointer=(pointer+64)&65535;continue
            self.put_word(stack-2,0xE70B if entry==0xE6E2 else entry+0x1A)
            self.put_word(stack-4,self.r[6]*256+self.r[7]);self.put_word(stack-6,pointer);self.put_word(stack-6,0xE6C5)
            carry=(((pointer>>8)-0xA1)&0x40)>>6
            self.r[0:2]=[(((pointer-0xA100)&65535)//64)&255,inc_flags(code,carry)]
            self.r[5]=(code+1)&255;self.path.append('found_ff_returns_Z' if code==255 else 'found')
            return self.finish(19)
        raise AssertionError('Исследовательский список не завершил поиск, игровой предел этим не задаётся')

    def override(self):
        pointer=self.r[8]*256+self.r[9];value=self.read(pointer+21);carry=self.r[1]&1
        if value==255:self.r[0:2]=[0,0x50|carry];self.path.append('no_override');return self.finish(4)
        flags=(value&0xA8)|(64 if value==0 else 0)|(16 if value&15==15 else 0)|(4 if value==127 else 0)|2|carry
        self.r[0:2]=[value,flags];self.put(pointer+11,value);self.put(pointer+10,2)
        self.path.append('override_'+('zero' if value==0 else 'nonzero'));return self.finish(10)

    def common_class_link(self):
        pointer=self.r[8]*256+self.r[9];self.put(pointer+11,255);self.m1(3)
        if self.r[1]&1:self.path.append('carry_skip');return self.finish()
        self.call(0xE6E2,0x6622,lambda:self.filtered(0xE6E2));self.m1(1)
        if self.r[1]&64:self.path.append('search_Z');return self.finish()
        self.put(pointer+11,self.r[0]);self.put(pointer+10,2);self.path.append('link_written');return self.finish(5)

    def class0(self):
        self.call(0x662B,0x6611,self.override);self.m1(1)
        if not self.r[1]&64:self.path.append('override_return');return self.finish()
        self.m1(2);a=self.r[15];self.r[0:2]=[a,cp_flags(a,112)];self.m1(1)
        pointer=self.r[8]*256+self.r[9];self.put(pointer+10,2);self.m1(2)
        return self.common_class_link()

    def find_code(self):
        stack=self.r[12];wanted=self.r[4];pointer=0xA100
        self.pair(2,64);self.m1(3)
        for _ in range(1024):
            self.put_word(stack-2,0xE997)
            while self.read(pointer+1)==128 and self.read(pointer)!=128:
                pointer+=64;self.m1(10)
            self.pair(10,pointer)
            if self.read(pointer+1)==128:
                self.r[0:2]=[128,0x42];self.path.append('code_'+str(wanted)+'_missing');return self.finish(13)
            if self.read(pointer+18)==wanted:
                self.r[0:2]=[(wanted+1)&255,inc_flags(wanted,0)]
                self.path.append('code_'+str(wanted)+'_found');return self.finish(14)
            self.m1(12);pointer+=64
        raise AssertionError('Исследовательский список поиска класса не завершился')

    def iy_index(self):
        stack=self.r[12];pointer=self.r[10]*256+self.r[11]
        self.put_word(stack-2,self.r[6]*256+self.r[7]);self.put_word(stack-4,pointer);self.put_word(stack-4,0xE6C5)
        index=(((pointer-0xA100)&65535)//64)&255;low=(pointer<<2)&255
        flags=(low&128)|(64 if low==0 else 0)|(4 if low.bit_count()%2==0 else 0)|(index&0x28)
        flags|=((((pointer>>8)-0xA1)&255)>>6)&1
        self.r[0:2]=[index,flags];return self.finish(16)

    def reset_bases(self):
        self.pair(6,0)
        for address in (0xE5B0,0xE5CF,0xE5EA):self.put_word(address,0)
        return self.finish(5)

    def preferred(self,entry):
        assert entry in (0xF51E,0xF527,0xF535,0xF53F,0xF541,0xF54B,0xF54D,0xF557)
        special=False
        if entry==0xF51E:
            self.m1(2);a=self.r[15];self.r[0:2]=[a,cp_flags(a,230)];self.m1(2)
            if a>=230:self.call(0xEBB8,0xF527,lambda:self.stream(2));entry=0xF527
            else:entry=0xF535
        if entry==0xF527:
            a=self.r[7];self.r[0:2]=[a,cp_flags(a,40)];self.m1(3)
            if a<40:
                gate=self.read(0x9BCD);self.r[0:2]=[26,cp_flags(gate,80)];self.m1(4)
                special=gate>=80
            entry=0xF557 if special else 0xF535
        if entry in (0xF53F,0xF54B):self.m1(1);entry=0xF557
        if entry in (0xF535,0xF541,0xF54D):
            for address,code in ((0xF535,0),(0xF541,7),(0xF54D,5)):
                if address<entry:continue
                self.r[4]=code;self.m1(1)
                self.call(0xE98D,address+5,self.find_code);self.m1(1)
                if self.r[1]&64:continue
                self.call(0xE6BE,address+10,self.iy_index)
                if code!=5:self.m1(1)
                entry=0xF557;break
            else:self.path.append('no_reference');return self.reset_bases()
        # Обновление класса 18 разрешено только при отсутствии активного класса 3.
        self.r[0:2],self.r[16:18]=self.r[16:18],self.r[0:2];self.m1(1)
        self.r[4]=3;self.m1(1);self.call(0xE98D,0xF55D,self.find_code);self.m1(1)
        if not self.r[1]&64:self.path.append('class3_blocks');return self.reset_bases()
        self.r[4]=18;self.m1(1);self.call(0xE98D,0xF564,self.find_code);self.m1(1)
        if self.r[1]&64:self.path.append('class18_missing');return self.reset_bases()
        pointer=self.r[10]*256+self.r[11];self.put(pointer+10,11);self.m1(2)
        self.r[0:2],self.r[16:18]=self.r[16:18],self.r[0:2];self.m1(1)
        self.put(pointer+13,self.r[0]);self.put(pointer+22,2);self.m1(4)
        self.path.append('class18_updated');return self.reset_bases()
