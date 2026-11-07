"""E86B, независимая композиция потока 11, поиска свободной записи и чтений R."""
from ReferenceActionRecordFilters import Machine
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionClampVectorWords import logical_flags
from CheckActionRecordSearch import inc_flags
from CheckActionMissileConsume import dec_flags
from CheckActionRecordIndex import decode


class SpawnMachine(Machine):
    def exx(self):self.r[2:8],self.r[18:24]=self.r[18:24],self.r[2:8]

    def reusable(self):
        self.pair(4,64);pointer=0xA100;self.m1(3)
        for _ in range(1024):
            high=self.read(pointer+1);self.pair(10,pointer);self.m1(6)
            if high!=128:pointer+=64;continue
            low=self.read(pointer);self.m1(4)
            if low==128:self.r[0:2]=[128,0x42];self.path.append('no_free_record');return self.finish()
            old=self.read(pointer+24);self.put(pointer+24,0);self.m1(6)
            if old==255:self.path.append('skip_once');pointer+=64;continue
            self.r[0:2]=[old+1,inc_flags(old,int(low<128))];self.path.append('free_record');return self.finish(1)
        raise AssertionError('нет доступной записи либо маркера, защитный предел модели')

    def address_index(self):
        value=self.r[6]*256+self.r[7];index,flags,hl=decode(value)
        self.r[0:2]=[index,flags];self.pair(6,hl);return self.finish(9)

    def spawn(self):
        ix=self.r[8]*256+self.r[9];flags=0x30|(self.r[1]&1)
        blocked=bool(self.read(ix+24)&4);self.m1(3)
        if blocked:self.r[1]=flags;self.path.append('already_requested');return self.finish()
        self.r[1]=flags|0x44;self.put(0xE8F1,self.r[0]);self.m1(1)
        self.call(0xEBBF,0xE876,lambda:self.stream(11));low=self.r[7]
        self.r[0:2]=[low,cp_flags(low,10)];self.m1(3)
        if low>=10:self.path.append('random_reject');return self.finish()
        self.put(ix+24,self.read(ix+24)|4);self.m1(4)
        counter=(self.r[15]&1)+1;self.r[0:2]=[counter,inc_flags(counter-1,0)];self.r[2]=counter;self.m1(3)
        self.path.append('requested_'+str(counter))
        for _ in range(2):
            self.exx();self.m1(1);self.call(0xE9A1,0xE888,self.reusable);self.m1(1)
            if self.r[1]&64:self.path.append('allocation_return_with_EXX');return self.finish()
            iy=self.r[10]*256+self.r[11];stack=self.r[12]
            self.put_word(stack-2,ix);self.pair(6,ix);self.m1(3)
            self.call(0xE6C7,0xE88F,self.address_index)
            self.put(iy+32,self.r[0]);self.put(iy+33,8);self.m1(4)
            # Расчёт одного BC-смещения для всех трёх компонент, старший байт зависит от текущего R.
            self.m1(2);b=(self.r[15]&1)+1;self.r[2]=b;self.m1(3)
            self.m1(2);c=self.r[15]&127;self.r[3]=c;self.m1(2)
            offset=256*b+c
            for axis in range(3):
                value=(self.word(ix+2*axis)+offset)&65535
                self.pair(6,value);self.put_word(iy+2*axis,value);self.m1(9)
            self.m1(3);negative_r=bool(self.r[15]&128);self.m1(2)
            model_code=136 if negative_r else 140;self.r[3]=model_code
            if not negative_r:self.m1(1)
            self.put(iy+6,model_code);self.put(iy+15,90);self.put(iy+7,0);self.m1(6)
            self.m1(2);phase1=self.r[15]&15;self.m1(3);self.put(iy+8,phase1)
            self.m1(2);phase2=self.r[15]&7;self.m1(3);self.put(iy+9,phase2)
            self.r[1]=logical_flags(phase2)|16
            for field,value in ((17,40),(10,self.read(0xE8F1)),(22,13),(12,0),(18,9),(20,0)):
                self.put(iy+field,value);self.m1(2)
            linked=self.read(ix+11);self.r[0]=linked;self.put(iy+11,linked);self.m1(4)
            for field,value in ((21,255),(19,50),(16,1),(37,2)):
                self.put(iy+field,value);self.m1(2)
            self.exx();self.m1(1);old=self.r[2];self.r[2]=(old-1)&255
            self.r[1]=dec_flags(old,0);self.m1(2);self.path.append('child_written')
            if self.r[2]==0:return self.finish(1)
        raise AssertionError('исходный счётчик должен создавать не больше двух записей')
