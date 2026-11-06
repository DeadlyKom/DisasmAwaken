"""Числовая семантика CF0B, режимы глубины, два кода смещения, частичные записи и радиус."""
from ReferenceControlsProjectionRatio import evaluate as ratio
from CheckControlsRatioInside import divide_fraction
from ReferenceControlsBufferPoints import sub16_flags


class Projection:
    def __init__(self,banks,registers):
        self.banks=[bytearray(b) for b in banks];self.r=list(registers);self.writes=[];self.path=[]
        self.flags=0;self.coordinate=3

    def read(self,address):return self.banks[2 if address<0xC000 else 1][address&0x3FFF]

    def put(self,address,value):
        bank=2 if address<0xC000 else 1;self.banks[bank][address&0x3FFF]=value;self.writes.append((bank,address&0x3FFF,value))

    def pair(self,index,value):self.r[index:index+2]=[value>>8,value&255]

    def component(self,index):
        pointer=0x9B1E+3*index
        return self.read(pointer)+256*self.read(pointer+1)+65536*(self.read(pointer+2)&127)

    def negative(self,index):return bool(self.read(0x9B20+3*index)&128)

    def finish(self,reject=False):
        if reject:self.r[0:2]=[0,0x44]
        self.r[18:20]=[self.flags,self.coordinate]
        self.r[12]+=2;self.r[24]=0x3FFF
        return self

    def project_coordinate(self,index,depth,direction_bit,set_for_negative):
        if self.negative(index)==set_for_negative:self.flags|=1<<direction_bit
        result=ratio(self.component(index),self.component(depth),self.coordinate)
        self.r[0:2]=[result['a'],result['f']]
        for position,key in ((2,'bc'),(4,'de'),(6,'hl')):self.pair(position,result[key])
        self.flags|=result['flag_mask'];self.coordinate-=1
        self.path.append(result['branch'])
        return not result['reject']

    def run(self):
        mode=self.read(0xCEF9)
        depth=2 if mode<2 else 0;horizontal=0 if mode<2 else 2
        required_negative=mode in (1,2)
        if self.negative(depth)!=required_negative:
            self.path.append('depth_sign_reject');return self.finish(True)
        # Обновление знака глубины выполняется до отношений, частичный отказ его не откатывает.
        if mode<3:self.put(0x9B20+3*depth,self.read(0x9B20+3*depth)&127)
        if not self.project_coordinate(horizontal,depth,0,mode not in (0,2)):
            self.path.append('horizontal_reject');return self.finish(True)
        self.r[0]=self.r[4];self.put(0xD17E,self.r[4])
        if not self.project_coordinate(1,depth,1,False):
            self.path.append('vertical_reject');return self.finish(True)
        self.r[0]=self.r[4];self.put(0xD17D,self.r[4])
        self.r[0]=self.flags;self.put(0xD17F,self.flags)
        magnitude=self.component(depth);word=magnitude>>8
        if magnitude<65536:
            self.pair(6,(0xA000-magnitude)&65535);self.pair(4,magnitude)
            self.r[1]=sub16_flags(0xA000,magnitude)
            if magnitude<=0xA000:
                self.put(0xD180,255);self.r[0]=1;self.path.append('radius_near');return self.finish()
        self.pair(6,(0xA000-word)&65535);self.pair(4,word);self.r[1]=sub16_flags(0xA000,word)
        if word>0xA000:
            self.path.append('radius_far_reject');return self.finish(True)
        if word<256:
            self.r[2]=word;quotient,remainder,flags=divide_fraction(160,word)
            self.path.append('radius_byte')
        else:
            # Расчёт нормализованных коэффициентов по старшему разряду слова глубины, без цикла Z80.
            shift=17-word.bit_length();numerator=160<<(shift-1)
            denominator=(word<<(shift-1))>>8
            self.r[2:4]=[denominator,(word<<shift)&255]
            quotient,remainder,flags=divide_fraction(numerator>>8,denominator,numerator&255)
            self.path.append('radius_word')
        self.pair(4,quotient<<8);self.r[0:2]=[1,flags];self.put(0xD180,quotient)
        return self.finish()
