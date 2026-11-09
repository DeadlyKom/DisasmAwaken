"""6417, младшее двухбитовое поле и исходный код списка из R-образованного HL."""
from ReferenceActionChildSpawn import SpawnMachine
from CheckActionNearestCandidate import NearestMachine
from CheckActionRecordSearch import inc_flags
from CheckActionRecordIndex import add_flags
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import cp_flags


class Class19Machine(SpawnMachine,NearestMachine):
    def class19_spawn(self,prepared=False):
        if prepared:
            ix=self.r[8]*256+self.r[9];marked=bool(self.r[7]&128)
            self.r[2]=self.r[7]
            self.r[0:2],self.r[16:18]=self.r[16:18],self.r[0:2]
            self.m1(2)
        else:
            ix=self.r[8]*256+self.r[9];old=self.read(ix+24);count=old&3
            self.r[3]=old;self.r[0:2]=[count,logical_flags(count)|16];self.m1(5)
            if count==0:self.path.append('zero_count');return self.finish()
            count-=1;updated=(old&252)|count;self.put(ix+24,updated);self.r[2]=count;self.m1(7)
            self.m1(2);raw=self.r[15];self.r[6]=raw;self.m1(4)
            kind=raw&31
            if kind>=27:kind-=5;self.m1(1)
            marked=kind<5;self.r[7]=kind|(128 if marked else 0);self.m1(3+2*marked)
            control=((raw&112)>>4)+1;self.r[2]=self.r[7]
            self.r[0:2],self.r[16:18]=self.r[16:18],[control,inc_flags(control-1,0)]
            self.m1(9)
        self.call(0xE9A1,0x6446,self.reusable);self.m1(1)
        if self.r[1]&64:self.path.append('no_child_slot');return self.finish()
        iy=self.r[10]*256+self.r[11];self.exx();self.m1(1);self.pair(4,200)
        for axis in range(3):
            word=(self.word(ix+2*axis)+200)&65535;self.pair(6,word);self.put_word(iy+2*axis,word)
            self.m1(10 if axis==0 else 9)
        for field,value in ((6,152),(10,4),(11,255),(12,0)):
            self.put(iy+field,value);self.m1(2)
        for parent,child in ((7,13),(8,14),(9,15)):
            self.r[0]=self.read(ix+parent);self.put(iy+child,self.r[0]);self.m1(4)
        source_rate=self.read(ix+16);rate=max(source_rate-30,0);self.m1(4+int(source_rate<30))
        self.r[0:2]=[min(rate,69),cp_flags(rate,70)];self.m1(2+int(rate>=70))
        self.put(iy+16,self.r[0]);self.m1(2)
        self.r[0:2],self.r[16:18]=self.r[16:18],self.r[0:2];self.m1(1)
        self.put(iy+17,self.r[0]);self.put(iy+18,19);self.put(iy+19,20);self.m1(6)
        self.exx();self.m1(1)
        self.r[1]=(self.r[1]&1)|(0x90 if marked else 0x54)|(self.r[2]&0x28);self.r[0]=16;self.m1(4)
        if not marked:self.r[0:2]=[0,0x44];self.m1(1)
        self.put(iy+24,self.r[0]);self.r[2]&=127;self.put(iy+35,self.r[2]);self.m1(6)
        packed=self.r[6]*256+self.r[7];self.call(0xE6C7,0x64C4,self.address_index)
        generated=self.r[0];self.r[5]=generated;self.pair(6,0xA01B);self.m1(2)
        self.path.append('generated_FE' if generated==254 else 'generated_other')
        self.path.append('packed_HL_differs_from_child' if packed!=iy else 'packed_HL_equals_child')
        for _ in range(1024):
            cursor=(self.r[6]*256+self.r[7])+1;self.pair(6,cursor);value=self.read(cursor)
            self.r[0:2]=[value,cp_flags(value,254)];self.m1(4)
            if value==254:self.path.append('list_end_without_insertion');return self.finish(1)
            if value==255:
                self.put(cursor,generated);self.path.append('replace_ff');return self.finish(3)
            self.r[0]=value;self.exx();self.m1(1);self.call(0xE6A7,0x64D5,self.index_address)
            pointer=self.r[6]*256+self.r[7];self.r[7]=(self.r[7]+1)&255
            high=self.read(pointer+1);self.r[0:2]=[high,cp_flags(high,128)];self.m1(3)
            self.exx();self.m1(2)
            if high!=128:self.path.append('keep_active_list_item');continue
            self.put(cursor,generated);self.path.append('replace_unavailable');return self.finish(2)
        raise AssertionError('список не достиг FE либо заменяемой ячейки')
