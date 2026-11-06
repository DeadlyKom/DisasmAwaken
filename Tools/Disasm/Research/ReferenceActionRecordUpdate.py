"""Числовая семантика обновления компонент, отказов и очереди, без исполнения Z80 эталоном."""
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from CheckActionOffsetRestore import cp_flags
from CheckControlsEvenSpan import and_flags


class RecordUpdate:
    def __init__(self,banks,registers):
        self.banks=[bytearray(b) for b in banks];self.r=list(registers);self.writes=[];self.ports=[]
        self.cpu_sp=self.word(0xE605);self.ix=self.r[8]*256+self.r[9];self.path=[];self.queue_result=None

    def read(self,address,bank=0):
        page=5 if address<0x8000 else 2 if address<0xC000 else bank
        return self.banks[page][address&0x3FFF]

    def put(self,address,value,bank=0):
        page=5 if address<0x8000 else 2 if address<0xC000 else bank
        self.banks[page][address&0x3FFF]=value;self.writes.append((page,address&0x3FFF,value))

    def word(self,address):return self.read(address)+256*self.read(address+1)

    def store_word(self,address,value):self.put(address,value&255);self.put(address+1,value>>8)

    def pair(self,index,value):self.r[index:index+2]=[value>>8,value&255]

    def mark(self,pointer):self.put(pointer+1,128);self.put(pointer,0);self.put(pointer+24,255)

    def restore(self):
        code=self.read(self.ix+18);self.r[0:2]=[code,cp_flags(code)]
        if code==20:
            for active,original in zip((0xE5B3,0xE5D2,0xE5ED),(0xE68C,0xE692,0xE698)):
                value=self.word(original);self.store_word(active,value);self.pair(6,value)

    def reject(self):
        self.store_word(self.cpu_sp-2,0xE65F);self.mark(self.ix)
        if self.read(self.ix+18)!=18:self.restore();return
        self.put(0x9B83,0);self.put(0x9B82,0);self.pair(2,64)
        pointer=0xA100
        while True:
            self.store_word(self.cpu_sp-2,0xE677)
            while self.read(pointer+1)==128:
                if self.read(pointer)==128:
                    self.r[0:2]=[128,0x42];self.pair(10,pointer);return
                pointer+=64;assert pointer<=0xA780
            if self.read(pointer+18)==18:
                self.store_word(self.cpu_sp-2,0xE682);self.mark(pointer)
            pointer+=64;assert pointer<=0xA780

    def find_class12(self):
        self.store_word(self.cpu_sp-2,0xE613);self.pair(2,64);self.r[4]=18
        pointer=0xA100
        while True:
            self.store_word(self.cpu_sp-4,0xE997)
            while self.read(pointer+1)==128:
                if self.read(pointer)==128:self.pair(10,pointer);return None
                pointer+=64;assert pointer<=0xA780
            if self.read(pointer+18)==18:self.pair(10,pointer);return pointer
            pointer+=64;assert pointer<=0xA780

    def queue_warning(self):
        flags=and_flags(self.read(0xE644));self.put(0xE644,24)
        de=self.r[4]*256+self.r[5];bc=self.r[2]*256+self.r[3];hl=self.r[6]*256+self.r[7]
        # Создание рамок настоящего межбанкового вызова, внешние PUSH DE и CALL тоже включены.
        for delta,value in ((2,de),(4,0xE655),(6,0x1800|flags),(8,bc),(10,hl),
            (12,0x6048),(14,bc),(12,0x604B),(14,hl),(16,bc),(18,0x1100|flags)):
            self.store_word(self.cpu_sp-delta,value)
        virtual={address:self.read(address,1) for address in range(QUEUE,QUEUE+34)}
        virtual[PRODUCER],virtual[PRODUCER+1]=self.read(PRODUCER,1),self.read(PRODUCER+1,1)
        self.queue_result=insert(virtual,0xF3B9)
        for address,value in self.queue_result['writes']:self.put(address,value,1)
        self.store_word(self.cpu_sp-12,0x6050);self.store_word(self.cpu_sp-14,bc)
        self.ports=[(0x7FFD,17),(0x7FFD,16)]

    def run(self,entry):
        # Расчёт границы из того же числа удвоений, но единым числовым выражением.
        initial_hl=self.r[6]*256+self.r[7]
        threshold=(125-(((initial_hl<<(0xE5A4-entry))&65535)>>8))&255
        self.r[2]=threshold
        for index,(base,active) in enumerate(zip((0xE5B0,0xE5CF,0xE5EA),(0xE5B3,0xE5D2,0xE5ED))):
            old=self.word(self.ix+2*index);difference=(self.word(base)-self.word(active))&65535
            self.pair(6,difference);self.pair(4,old)
            if index==0 and old>>8==128:self.path.append('first_inactive');break
            value=(difference+old)&65535;self.pair(6,value)
            # Проверка знакового переполнения суммы двух 16-битных слов.
            overflow=(~(difference^old)&(difference^value)&32768)!=0
            high=value>>8;normal=high if high<128 else 255-high
            if overflow or normal>=threshold:
                self.path.append(('overflow_' if overflow else 'bound_')+str(index))
                self.reject();break
            # Обновление только уже принятой компоненты, отказ последующей компоненты её не откатывает.
            self.store_word(self.ix+2*index,value)
        else:self.path.append('three_components')
        if not any(p.startswith(('overflow_','bound_')) for p in self.path):
            if self.read(0x9B82)==0:self.path.append('state_off')
            else:
                found=self.find_class12()
                if found is None:self.path.append('class12_missing')
                else:
                    normalized=[]
                    for delta in (5,3,1):
                        value=self.read(found+delta);normalized.append(value if value<128 else 255-value)
                    self.r[2:4]=normalized[0:2]
                    if max(normalized)>=8:self.put(0xE644,128);self.path.append('arm_warning')
                    elif self.read(0xE644)&128:self.queue_warning();self.path.append('request_warning')
                    else:self.path.append('warning_disarmed')
            self.restore()
        self.r[12],self.r[24]=self.cpu_sp+2,0x3FFF
        return self
