"""State0A, до трёх больших эффектов класса 17 и допуск периодического создания класса 3."""
from ReferenceActionLargeClassEffect import LargeClassMachine
from CheckActionPeriodicClass3State import PeriodicMachine
from ReferenceControlsPointRespawn import cp_flags
from CheckActionRecordIndex import add_flags
from CheckActionMissileConsume import dec_flags


class SweepMachine(LargeClassMachine,PeriodicMachine):
    def push(self,value,m1=1):self.r[12]-=2;self.put_word(self.r[12],value);self.m1(m1)
    def pop(self,index,m1=1):self.pair(index,self.word(self.r[12]));self.r[12]+=2;self.m1(m1)

    def count_class3(self):
        ix=self.r[8]*256+self.r[9];target=self.read(ix+13);number=0;c=self.r[3];pointer=0xA100;m1=4
        for _ in range(1024):
            low,high=self.read(pointer),self.read(pointer+1)
            if high==128:
                if low==128:m1+=8;break
                m1+=9;pointer+=64;continue
            c=(pointer+1)&255
            if self.read(pointer+18)!=3:m1+=12;pointer+=64;continue
            if self.read(pointer+10)!=2:m1+=19;pointer+=64;continue
            if self.read(pointer+11)!=target:m1+=27;pointer+=64;continue
            number+=1;m1+=31
            if number==2:pointer+=1;break
            pointer+=64
        else:raise AssertionError('список счётчика не завершился')
        self.r[0:2]=[number,cp_flags(number,2)];self.r[2:8]=[number,c,0,64,pointer>>8,pointer&255]
        return self.finish(m1+3)

    def adjust_mode(self):
        old=self.read(0x9BCD);mode=self.read(0x9B83);delta=32+(10 if mode else 0)
        total=(old if old<128 else old-256)+delta;overflow=not -128<=total<=127
        negative=old>=128 if overflow else total<0
        value=max(0,min(127,total))|(32 if old<32 else 0)
        self.put(0x9BCD,value);self.r[0:4]=[value,cp_flags(old,32),old,value]
        return self.finish(15+5*bool(mode)+2*overflow+int(negative)+2*int(old<32))

    def sweep(self,rom):
        ix=self.r[8]*256+self.r[9];old=self.read(0xF49D);phase=(old>>1)|((old&1)<<7)
        self.r[0:2]=[phase,(self.r[1]&0xC4)|(phase&0x28)|(old&1)];self.put(0xF49D,phase);self.m1(4)
        if not old&1:self.path.append('phase_skips_sweep');return self.reset()
        self.r[21]=3;self.pair(6,0xA0C1);self.pair(4,64);self.m1(6)
        for _ in range(1024):
            pointer=((self.r[6]*256+self.r[7])+64)&65535;self.pair(6,pointer)
            high=self.read(pointer);self.r[0:2]=[high,cp_flags(high,128)];self.m1(4)
            if high==128:
                self.r[7]=(self.r[7]-1)&255;low=self.read(pointer-1);self.r[0:2]=[low,cp_flags(low,128)];self.m1(4)
                if low==128:break
                self.r[7]=(self.r[7]+1)&255;self.m1(1);continue
            base=pointer-1;code=self.read(base+18);link=self.read(base+15)
            self.r[2:4]=[link,code];self.put(ix+13,self.read(base+13));self.r[0:2]=[code,cp_flags(code,17)];self.m1(20)
            if code!=17:continue
            self.r[0]=link;self.exx();self.m1(2);self.call(0xE6A7,0xF4DD,self.index_address)
            target=(self.r[6]*256+self.r[7])+18;self.pair(6,target)
            selected_class=self.read(target);self.r[0:2]=[selected_class,cp_flags(selected_class,18)];self.m1(5)
            self.exx();self.m1(2)
            if selected_class!=18:continue
            self.exx();self.m1(1);self.push(self.r[4]*256+self.r[5]);self.exx();self.m1(1)
            self.push(self.r[6]*256+self.r[7]);self.push(self.r[4]*256+self.r[5]);self.push(ix,2)
            self.r[7]=(self.r[7]-1)&255;self.m1(1);self.push(self.r[6]*256+self.r[7]);self.pop(8,2)
            self.call(0xEA29,0xF4F5,lambda:self.large_class_effect(rom))
            self.pop(8,2);self.pop(4);self.pop(6);self.exx();self.m1(1);self.pop(4)
            counter=self.r[5];self.r[5]=(counter-1)&255;self.r[1]=dec_flags(counter,self.r[1]&1)
            self.m1(1);self.exx();self.m1(2);self.path.append('class17_effect')
            if self.r[1]&64:break
        else:raise AssertionError('обход не достиг маркера либо трёх эффектов')
        self.call(0x62CF,0xF502,self.count_class3);self.m1(1)
        if not self.r[1]&1:self.path.append('two_class3_skip_spawn_state');return self.reset()
        self.put(ix+10,11);self.m1(4);value=(self.r[15]&1)+2
        self.r[0:2]=[value,add_flags(value-2,2)];self.put(ix+22,value);self.m1(4)
        link=self.read(ix+13);self.r[0:2]=[link,cp_flags(link,26)];self.r[3]=32;self.m1(4)
        if link==26:self.call(0x638C,0xF51B,self.adjust_mode);self.path.append('immediate_delta_32')
        else:self.m1(1)
        self.m1(1);self.path.append('parent_state_0B');return self.reset()
