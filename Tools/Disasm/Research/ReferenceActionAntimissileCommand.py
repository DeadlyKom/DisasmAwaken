"""722E, независимый поиск ракеты и композиция с действительным входом E835."""
from ReferenceActionLinkedOverlay import LinkedOverlayMachine
from ReferenceControlsPointRespawn import cp_flags
from CheckControlsEvenSpan import and_flags
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert


class AntimissileMachine(LinkedOverlayMachine):
    def antimissile(self,ops):
        self.ports=[];delay=self.read(0xA85F);self.r[:2]=[delay,and_flags(delay)]
        if delay:self.path.append('delay');return self.finish()
        self.r[0]=5;self.put(0xA85F,5)
        virtual={a:self.banks[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
        virtual[PRODUCER]=self.banks[1][0x2C5D];virtual[PRODUCER+1]=self.banks[1][0x2C5E]
        result=insert(virtual,0xF32D)
        for address,value in result['writes']:
            self.banks[1][address-0xC000]=value;self.writes.append((1,address-0xC000,value))
        self.ports=[(0x7FFD,17),(0x7FFD,16)];self.path.append('message_accepted' if result['accepted'] else 'message_dropped')
        self.put_word(0xECA9,0xEDC1);self.pair(4,64);pointer=0xA100
        # Поиск останавливается только исходным маркером, исследовательский предел не задаёт игровую ёмкость.
        for _ in range(100):
            self.pair(6,pointer+1)
            if self.read(pointer+1)==128:
                self.pair(6,pointer);self.r[:2]=[self.read(pointer),cp_flags(self.read(pointer),128)]
                if self.read(pointer)==128:self.path.append('marker');return self.finish()
                pointer+=64;continue
            code=self.read(pointer+18);target=self.read(pointer+15);self.pair(2,(target<<8)|code)
            self.pair(6,pointer+1);self.r[:2]=[code,cp_flags(code,17)]
            if code!=17:pointer+=64;continue
            self.r[:2]=[target,cp_flags(target,26)]
            if target!=26:pointer+=64;continue
            break
        else:raise AssertionError('маркер недоступен')
        stack=self.r[12];ix=self.r[8]*256+self.r[9];self.r[12]-=2;self.put_word(stack-2,ix)
        self.pair(6,pointer);self.pair(8,pointer)
        self.put(pointer+12,self.read(pointer+12)|1);self.put(pointer+12,self.read(pointer+12)|9)
        high=self.read(pointer+27);self.r[:2]=[high,(cp_flags(high,128)&0xC4)|(high&0x28)|1]
        if high==128:self.path.append('vector_marker')
        else:
            self.pair(2,self.word(pointer+26));self.pair(6,self.word(pointer+28));self.pair(4,self.word(pointer+30));self.exx()
            for address,value in ((0xD9B6,3),(0xAF48,3),(0xAF56,3),(0xAF69,3),(0xD7C4,176),(0xD7A2,65535)):self.put_word(address,value)
            self.pair(2,3);self.pair(6,176);self.pair(4,65535)
            self.call(0xE835,0x72BB,lambda:self.check_depth_signs(ops));self.path.append('checked_vectors')
        self.pair(8,ix);self.r[12]=stack
        return self.finish()
