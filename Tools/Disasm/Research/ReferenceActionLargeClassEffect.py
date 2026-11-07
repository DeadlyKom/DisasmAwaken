"""EA29, полный большой эффект и отдельная числовая композиция игровых детей классов ниже 16."""
from ReferenceActionRecordFilters import Machine
from ReferenceControlsPointRespawn import cp_flags
from CheckActionRecordSearch import inc_flags


class LargeClassMachine(Machine):
    def put_bank(self,bank,address,value):
        self.banks[bank][address&0x3FFF]=value;self.writes.append((bank,address&0x3FFF,value))

    def large_class_effect(self,rom):
        ix=self.r[8]*256+self.r[9];cls=self.read(ix+18)
        stack=self.r[12];original_bc=self.r[2]*256+self.r[3];alt_bc=self.r[18]*256+self.r[19]
        prime_flags=self.r[17];offset=self.read(ix+6)
        # Расчёт исходного указателя с отдельным оборачиванием младшего индекса таблицы.
        pointer=self.read(0x9E00+offset)+256*self.read(0x9E00+((offset+1)&255))
        def object_read(address):
            address&=65535
            if address<0x4000:return rom[address]
            bank=5 if address<0x8000 else 2 if address<0xC000 else 4
            return self.banks[bank][address&0x3FFF]
        mode=object_read(pointer+1);vector=[self.word(ix+2*k) for k in range(3)]
        self.put(0xEAC4,64 if cls==8 else 160)
        # Создание числового эталона рамок чтения OBJECT3D, сохранённого IX и банкового возврата.
        for address,value in ((stack-2,0xEA3D),(stack-4,0xAAD8),(stack-6,original_bc),
            (stack-4,0xAAE1),(stack-6,original_bc),(stack-2,ix),(stack-4,0xEA5C),
            (stack-6,0x6CF6),(stack-8,alt_bc),(stack-6,0x6D00)):
            self.put_word(address,value)
        for address,value in ((0xEC5A,mode),(0xEC7D,20),(0xEC79,20),(0xEC6C,8)):self.put_bank(3,address,value)
        selected=0xA795;occupied=0
        while self.read(selected+7)>0 and self.read(selected+7)<128:
            selected+=18;occupied+=1;assert occupied<1024
        if self.read(selected+7)==0:
            values=[]
            for word in vector:values.extend((word&255,word>>8))
            values.extend((mode,8,0,196,0,196,1,8,128,2,20,20))
            for index,value in enumerate(values):self.put(selected+index,value)
            self.r[16:18]=[0,0x54];effect_cost=58+7*occupied;self.path.append('large_effect_allocated')
        else:
            self.r[16:18]=[8,prime_flags];effect_cost=16+7*occupied;self.path.append('large_effect_list_full')
        self.put_word(stack-6,0x6D05);self.put_word(stack-8,18)
        ttl=self.read(0x6D3D);self.put(0x6D39,1)
        if ttl<16:self.put(0x6D3D,16)
        self.r[0:8]=[cls,cp_flags(cls,16),0,18,2,128,0xC4,0]
        for register,value in zip((22,20,18),vector):self.pair(register,value)
        self.pair(10,selected);self.ports=getattr(self,'ports',[])+[(0x7FFD,20),(0x7FFD,16),(0x7FFD,19),(0x7FFD,16)]
        self.m1(92+effect_cost+2*int(ttl<16)+int(cls==8))
        if cls<16:
            from ReferenceActionLargeEffectChildren import generate
            generate(self,rom)
        self.put_word(0xECF6,0xEE4D);self.put(ix+1,128);self.put(ix,0);self.put(ix+24,255);self.pair(6,0xEE4D)
        self.path.append('large_current_record_released')
        return self.finish(10)
