"""63B6, фазовый допуск, расход третьей шкалы и два прямых входа в XOR-растеризатор."""
from ReferenceActionRecordFilters import Machine
from CheckActionLineRaster import raster
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceControlsBufferPoints import sub8_flags


class PairedAimMachine(Machine):
    def packed_line(self,return_address):
        stack=self.r[12];first=(self.r[7],self.r[6]);second=(self.r[5],self.r[4])
        assert first[1]==95 and 0<=second[1]<=95
        opcode=self.read(0x8D4E);branch=self.read(0x8D4F);table=bytes(self.read(0xE010+k) for k in range(8))
        result=raster(first,second,opcode,branch,table,self.banks[2],packed_entry=True)
        self.writes.extend(result['writes']);self.put_word(0xDEED,stack)
        self.put(result['patch'][0],opcode);self.put(result['patch'][1],branch)
        for pair,key in ((6,'hl'),(4,'de'),(2,'bc')):self.pair(pair,result[key])
        self.r[0:2],self.r[16:18]=result['af'],result['alt_af']
        self.m1(result['refresh_m1']);self.r[12]+=2;self.r[24]=return_address
        if first==second:self.path.append('packed_equal_runs_256')
        self.path.append('packed_line')
        return self

    def paired_aim(self):
        old=self.read(0x63B7);step=self.read(0x63B9);phase=(old+step)&255
        self.r[0:2]=[phase,add_flags(old,step)];self.put(0x63B7,phase);self.m1(4)
        if old+step<256:self.path.append('phase_no_carry');return self.finish()
        charge=self.read(0xA8BC);self.r[0:2]=[charge,cp_flags(charge,2)];self.m1(3)
        if charge<2:self.path.append('charge_below_two');return self.finish()
        self.put(0xA8BC,charge-2);self.put(0x666B,1);self.put(0xE310,0);self.put_word(0xECA9,0xEE34)
        self.put_word(0x8D4E,0x38A9);self.put(0xDE0F,16);self.m1(12)
        self.m1(2);raw_x=self.r[15];jitter_x=(raw_x&1)*(-1 if raw_x&16 else 1);self.m1(10+2*int(bool(raw_x&16)))
        self.m1(2);raw_y=self.r[15];jitter_y=(raw_y&1)*(-1 if raw_y&16 else 1)
        x=(self.read(0x9B19)+8+jitter_x)&255;y=(self.read(0x9B1A)+6+jitter_y)&255
        self.r[3]=raw_y;self.pair(4,y*256+x);self.r[0:2]=[y,add_flags((self.read(0x9B1A)+6)&255,jitter_y&255)]
        self.m1(10+2*int(bool(raw_y&16)))
        stack=self.r[12];self.put_word(stack-2,y*256+x);self.r[12]-=2;self.pair(6,0x5F40);self.m1(2)
        self.call(0xDDFC,0x6410,lambda:self.packed_line(0x6410))
        self.pair(6,0x5FC0);self.r[12]+=2;self.pair(4,y*256+x)
        # Учёт LD HL,nn, POP DE и хвостового JP ко второй линии.
        self.m1(3)
        self.path.append('two_aim_lines');return self.packed_line(self.word(self.r[12]))
