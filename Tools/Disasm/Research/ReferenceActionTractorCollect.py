"""7317, числовая композиция прицельного запроса, подтягивания трёх слов и байтового сбора."""
from ReferenceActionPairedAimLines import PairedAimMachine
from CheckActionNearestCandidate import NearestMachine
from ReferenceActionClampVectorWords import logical_flags
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert


class TractorCollectMachine(PairedAimMachine,NearestMachine):
    def collect_or_aim(self):
        self.ports=[];mode=self.read(0x7318);self.r[:2]=[mode,and_flags(mode)];self.m1(3)
        if mode==0:
            self.path.append('delegate_paired_aim');self.r[24]=0x63B6;return self.paired_aim()
        target=self.read(0x9B1B);self.r[:2]=[target,logical_flags(target)];self.m1(3)
        if target&128:self.path.append('negative_target');return self.finish()
        self.call(0xE6A7,0x7325,self.index_address);base=self.r[6]*256+self.r[7]
        high=self.read(base+1);self.pair(6,base+1);self.r[:2]=[high,cp_flags(high,128)];self.m1(4)
        if high!=128:
            state=self.read(base+10);self.pair(6,base+10);self.r[:2]=[state,cp_flags(state,4)];self.m1(6)
        if high==128 or state!=4:
            self.r[0]=255;self.put(0x9B1B,255);self.m1(3);self.path.append('drop_invalid_target');return self.finish()
        # Расчёт шага по каждому исходному старшему байту, диапазон FF00..00FF остаётся без движения.
        self.put(base+16,0);stack=self.r[12];self.put_word(stack-2,base);self.put_word(0x73A4,stack-2);self.m1(10)
        values=[self.word(base+2*i) for i in range(3)];near=[v>>8 in (0,255) for v in values]
        for i,value in enumerate(values):
            result=value if near[i] else (value+(50 if value&32768 else -50))&65535
            self.put_word(base+2*i,result)
        count=sum(near);self.r[5]=count;self.pair(2,0 if near[-1] else 0xFFCE);self.pair(6,base)
        self.r[:2]=[count,cp_flags(count,3)]
        self.m1(49+sum(bool(v&32768) for v in values)+2*count)
        if count!=3:self.path.append('pull_far_components');return self.finish()
        # Снятие захвата предшествует проверкам вместимости, код класса выбирает вид и байт пополнения.
        self.put(0x9B1B,255);self.put_word(stack-2,base);class_code=self.read(base+18);self.m1(9)
        if class_code==19:
            kind=self.read(base+35);amount=self.read(base+17);self.m1(7);self.path.append('class19_payload')
        else:
            kind=15 if class_code==16 else 27
            self.m1(3+int(class_code!=16)+2)
            amount=(self.r[15]&7)+1;self.m1(3);self.path.append('quantity_from_R')
        current=self.read(0x9BD2);control=self.read(0x741D+kind);candidate=current
        self.pair(2,(current<<8)|amount);self.pair(4,kind);self.pair(6,base)
        if control&192==0:
            candidate=(current+amount)&255;self.r[2]=candidate;limit=self.read(0x9BD3)
            self.r[:2]=[limit,cp_flags(limit,candidate)]
            if limit<candidate:self.path.append('capacity_refusal_target_already_cleared');return self.finish()
        else:self.path.append('counter_exempt_rule')
        # Расчёт именно байтового адреса, Price и QuantityAndMark не различаются, перенос сложения не проверяется.
        address=0x9BD4+kind;value=(self.read(address)+amount)&255;self.pair(4,address);self.r[:2]=[value,cp_flags(value,201)]
        if value>=201:self.path.append('byte_limit_refusal_target_already_cleared');return self.finish()
        self.put(address,value);self.r[0]=candidate;self.put(0x9BD2,candidate);self.put(base,0);self.put(base+1,128)
        reuse=self.read(base+24);self.r[:2]=[((base&255)+24)&255,16|(reuse&40)|(0 if reuse&16 else 68)]
        if reuse&16:self.put(0xA78C,self.read(0xA78C)|4);self.path.append('marked_record_sets_event2')
        self.pair(6,0xEE1B);self.put_word(0xECA9,0xEE1B)
        virtual={a:self.banks[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
        virtual[PRODUCER]=self.banks[1][0x2C5D];virtual[PRODUCER+1]=self.banks[1][0x2C5E]
        result=insert(virtual,0xF36D)
        for address,value in result['writes']:self.banks[1][address-0xC000]=value;self.writes.append((1,address-0xC000,value))
        self.ports=[(0x7FFD,17),(0x7FFD,16)];self.path.append('collected_message_accepted' if result['accepted'] else 'collected_message_dropped')
        return self.finish()
