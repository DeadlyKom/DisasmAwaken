"""624B и 62B5, проверка выбранной записи перед геометрией либо временным состоянием."""
from CheckActionNearestCandidate import NearestMachine
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes


class MotionGateMachine(NearestMachine):
    def enter_timed(self):
        stack=self.r[12];ix=self.r[8]*256+self.r[9]
        for pair,address in ((2,stack),(4,stack+2),(6,stack+4)):self.pair(pair,self.word(address))
        self.r[12]+=6;self.put(ix+25,self.read(ix+10));self.m1(9)
        self.timer_read_m1=self.m1_count
        nibble=self.r[15]&15;self.r[0:2]=[nibble+5,add_flags(nibble,5)]
        self.put(ix+23,self.r[0]);self.put(ix+10,17);self.pair(2,0x8080)
        self.path.append('enter_timed_state');result=self.finish(8)
        self.total_refresh_m1=self.m1_count
        return result

    def select_iy(self):
        stack=self.r[12];saved=self.r[6]*256+self.r[7]
        self.put_word(stack-2,saved);self.put_word(stack-4,0xE6A2)
        value=self.r[0];pointer=0xA100+64*value
        self.put_word(stack-4,pointer);self.pair(10,pointer)
        self.r[0:2]=[pointer>>8,add_flags(value>>2,0xA1)]
        return self.finish(19)

    def motion_gate(self,ratio,root,return_address=0x3FFF):
        ix=self.r[8]*256+self.r[9];stack=self.r[12]
        values=[self.r[p]*256+self.r[p+1] for p in (6,4,2)]
        for k,value in enumerate(values):self.put_word(stack-2-2*k,value)
        self.r[12]-=6;self.r[0]=self.read(ix+11);self.m1(5)
        self.call(0xE69E,0x6254,self.select_iy)
        iy=self.r[10]*256+self.r[11];high=self.read(iy+1)
        self.r[0:2]=[high,cp_flags(high,128)];self.m1(4)
        if high!=128:
            self.call(0xEAE9,0x625E,self.distance);value=self.r[0]
            self.r[1]=cp_flags(value,10);self.m1(2)
            if value<10:return self.enter_timed()
        self.path.append('ordinary_geometry');self.ports=[]
        for pair,value in zip((6,4,2),values):self.pair(pair,value)
        self.r[12]+=6;self.m1(3)
        self.m1(1);self.r[12]-=2;self.put_word(self.r[12],0x6268)
        child=geometry(self.r,ratio,root,return_address=0x6268)
        stepped=apply_codes(child['registers'],self.read(ix+8),self.read(ix+9),self.read(ix+37),return_address)
        for address,value in child['writes']+stepped['writes']:self.put(address,value)
        self.r=stepped['registers'];self.ports=child['ports']
        self.total_refresh_m1=self.m1_count+child['refresh_m1']+stepped['refresh_m1']
        return self
