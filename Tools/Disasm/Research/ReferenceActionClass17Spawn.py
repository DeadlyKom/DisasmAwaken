"""60E8, копия альтернативных компонент и связь двух обычных индексов."""
from ReferenceActionChildSpawn import SpawnMachine
from CheckActionNearestCandidate import NearestMachine


class Class17Machine(SpawnMachine,NearestMachine):
    def class17_spawn(self):
        parameter=self.r[0];bc=self.r[2]*256+self.r[3];stack=self.r[12]
        self.put(0x612E,parameter);self.put_word(stack-2,bc);self.r[12]-=2;self.m1(2)
        self.call(0xE9A1,0x60EF,self.reusable);self.r[12]+=2;self.pair(2,bc);self.m1(2)
        if self.r[1]&64:self.path.append('class17_no_slot');return self.finish()
        iy=self.r[10]*256+self.r[11]
        for offset,word in ((0,self.r[22]*256+self.r[23]),(2,self.r[20]*256+self.r[21]),(4,self.r[18]*256+self.r[19])):
            self.put_word(iy+offset,word)
        for field,value in ((6,144),(7,0),(8,0),(9,0),(10,8),(11,0),(12,0),(13,self.r[2]),(15,self.r[3])):
            self.put(iy+field,value)
        self.r[0:2],self.r[16:18]=self.r[16:18],[0,0x44]
        for field,value in ((17,self.r[0]),(18,17),(19,parameter),(37,2)):self.put(iy+field,value)
        self.m1(42);self.r[0]=self.r[3];self.m1(1)
        self.call(0xE6A7,0x6137,self.index_address)
        pointer=(self.r[6]*256+self.r[7])+12
        self.put(pointer,self.read(pointer)|2);self.pair(4,pointer-1);self.pair(6,64);self.m1(7)
        self.call(0xE6BE,0x6142,self.iy_index)
        self.put(pointer-1,self.r[0]);self.r[1]=(self.r[1]&0xC4)|(self.r[0]&0x28)|1
        self.path.append('class17_created');return self.finish(3)
