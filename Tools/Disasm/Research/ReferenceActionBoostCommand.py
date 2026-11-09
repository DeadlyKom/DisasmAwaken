"""74A3 и 7504, числовая модель проверки пространства и накопления ускорения."""
from ReferenceActionClass20Spawn import Class20Machine
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionClampVectorWords import logical_flags
from CheckActionRecordSearch import inc_flags
from CheckActionMissileConsume import dec_flags
from ReferenceActionGaugeWordKeys import evaluate as gauge


class BoostMachine(Class20Machine):
    def release(self):
        # Пометка класса 14, эталон результата повторного поиска, служебные слова стека сверяются отдельно.
        end=0xA100
        for _ in range(100):
            if self.read(end+1)==128 and self.read(end)==128:break
            if self.read(end+1)!=128 and self.read(end+18)==20:
                self.put(end+1,128);self.put(end,0);self.put(end+24,255)
            end+=64
        else:raise AssertionError('нет маркера списка')
        self.r[:2]=[128,0x42];self.pair(2,64);self.r[4]=20;self.pair(10,end);self.path.append('release_class14')
        return self.finish()

    def boost(self):
        opcode=self.read(0x6E72);self.r[:2]=[opcode,cp_flags(opcode,201)]
        if opcode==201:self.path.append('return_gate');return self.finish()
        self.r[0]=1;self.put(0x6F56,1);self.pair(4,64);pointer=0xA100
        # Поиск по квантованным старшим байтам, младшие компоненты в оценке не участвуют.
        for _ in range(100):
            high=self.read(pointer+1);self.pair(6,pointer+1)
            if high==128:
                low=self.read(pointer);self.r[:2]=[low,cp_flags(low,128)]
                if low==128:self.path.append('clear_space');return self.advance()
                pointer+=64;continue
            fold=lambda value:value if value<128 else value^255
            first=fold(high);code=self.read(pointer+18);self.pair(2,(code<<8)|first)
            if code>=16 and code!=18:pointer+=64;continue
            combined=first|fold(self.read(pointer+3))|fold(self.read(pointer+5));self.r[3]=combined
            self.r[:2]=[combined,cp_flags(combined,48)]
            if combined>=48:pointer+=64;continue
            self.path.append('near_record');return self.release()
        raise AssertionError('нет маркера списка')

    def advance(self):
        selected=0x9C10 if self.read(0x9C10) else 0x9C11;value=self.read(selected)
        self.pair(6,selected);self.r[0]=value;carry=0
        self.r[3]=(value-1)&255;self.r[1]=dec_flags(value,carry)
        if self.r[3]&128:self.path.append('selected_sign_refusal');return self.release()
        fast=(self.read(0x750D)+1)&255;self.put(0x750D,fast);self.r[:2]=[fast,inc_flags((fast-1)&255,0)]
        if fast==0:
            old=self.read(0x7515);slow=(old+1)&7;self.put(0x7515,slow);self.r[:2]=[slow,logical_flags(slow)|16]
            if slow==0:
                self.put(selected,self.r[3]);oldcurrent=self.read(0x9BD2);self.put(0x9BD2,(oldcurrent-1)&255)
                self.put(0x665C,1);self.r[:2]=[1,dec_flags(oldcurrent,0)];self.path.append('selected_byte_spent')
        # Расчёт двух вращений, второе выполняется только при единичном младшем бите первого.
        old=self.read(0x752C);a=(old>>1)|((old&1)<<7);self.put(0x752C,a)
        self.r[:2]=[a,(self.r[1]&0xC4)|(a&40)|(old&1)]
        if old&1:
            old=self.read(0x7534);a=(old>>1)|((old&1)<<7);self.put(0x7534,a)
            self.r[:2]=[a,(self.r[1]&0xC4)|(a&40)|(old&1)]
            if old&1:
                self.call(0x617D,0x753C,self.spawn20);self.path.append('spawn_called')
        self.pair(6,4096);self.put_word(0x7693,4096);self.r[2]=16
        for i in range(16):
            stack=self.r[12];bc=self.r[2]*256+self.r[3];self.put_word(stack-2,bc);self.r[12]-=2;self.put_word(stack-4,0x7548);self.r[12]-=2
            child=gauge(self.r,0x7680,0,self.read(0x6E72),self.word(0xA78F),4096)
            for address,value in child['writes']:self.put(address,value)
            self.r=child['registers'];self.r[24]=0x7548;self.r[12]+=2;self.pair(2,bc);self.r[2]-=1
        self.path.append('sixteen_gauge_steps');return self.finish()
