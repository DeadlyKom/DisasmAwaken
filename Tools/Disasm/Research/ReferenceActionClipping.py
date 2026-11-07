"""Композиционный эталон случаев ACTION, числовые помощники вместо исполнения их инструкций."""
import re
from CheckSignedMultiply import sbc16_flags
from CheckSignedDivision import expected as division
from ReferenceActionFaceOrientation import multiply
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags

PRODUCT={0xC477:(0xCF37,0,False),0xC496:(0xCF33,95,False),0xC4B5:(0xCF2F,0,True),0xC4D4:(0xCF2B,255,True)}
APPEND={0xC4F3:(0xC477,0xC4F6),0xC53D:(0xC496,0xC540),0xC588:(0xC4B5,0xC58B),0xC5E4:(0xC4D4,0xC5E7)}
CACHED={0xC4F6:(0xCF37,0,False),0xC540:(0xCF33,95,False),0xC58B:(0xCF2F,0,True),0xC5E7:(0xCF2B,255,True)}
COMPARE={0xC66D:(0xCF37,0xCF2F),0xC681:(0xCF37,0xCF2B),0xC695:(0xCF33,0xCF2F),0xC6A9:(0xCF33,0xCF2B)}
DELTA={0xC6BD:(0xCF1B,0xCF0B),0xC6C8:(0xCF1D,0xCF0D)}
CORNERS={0xC641:0,0xC64C:255,0xC657:0x5F00,0xC662:0x5FFF}


class Clipping:
    def __init__(self,banks,registers,operations,pc_index,sp_index):
        self.banks=[bytearray(b) for b in banks];self.r=list(registers);self.ops=operations
        self.pc,self.sp=pc_index,sp_index;self.writes=[];self.special=False

    def byte(self,address,value=None):
        bank=5 if address<0x8000 else 2 if address<0xC000 else 0
        assert address>=0x4000
        if value is None:return self.banks[bank][address&0x3FFF]
        self.banks[bank][address&0x3FFF]=value;self.writes.append((bank,address&0x3FFF,value))

    def word(self,address,value=None):
        if value is None:return self.byte(address)+256*self.byte(address+1)
        self.byte(address,value&255);self.byte(address+1,value>>8)

    def pair(self,index,value=None):
        if value is None:return self.r[index]*256+self.r[index+1]
        self.r[index:index+2]=[value>>8,value&255]

    def push(self,value):
        self.r[self.sp]-=2;self.word(self.r[self.sp],value)

    def pop(self):
        value=self.word(self.r[self.sp]);self.r[self.sp]+=2;return value

    def write_pair(self):
        offset=self.byte(0x9BA3);following=(offset+2)&255;previous=(following-1)&255
        carry=self.r[1]&1
        self.byte(0x9000+offset,self.r[5]);self.byte(0x9000+((offset+1)&255),self.r[4]);self.byte(0x9BA3,following)
        self.pair(6,0x9000|following)
        self.r[0:2]=[following,(following&0xA8)|(64 if following==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)|carry]

    def product(self,entry):
        output,bound,vertical=PRODUCT[entry]
        x1,x2,y1,y2=(self.word(a) for a in (0xCF0B,0xCF1B,0xCF0D,0xCF1D))
        left,right,bc=((y1-y2)&65535,(x1-bound)&65535,y2) if vertical else ((y1-bound)&65535,(x1-x2)&65535,bound)
        result=multiply(left,right,bc,self.pair(8))
        # Вложенный CALL умножителя и его временное слово знака AF являются настоящими побочными записями.
        self.push(entry+23);self.push(result['stack_af'][0]*256+result['stack_af'][1]);self.pop();assert self.pop()==entry+23
        self.r[0:2]=result['af']
        for index,key in ((2,'bc'),(4,'low'),(6,'high'),(8,'ix')):self.pair(index,result[key])
        self.word(output,result['low']);self.word(output+2,result['high'])

    def intersection(self,entry):
        product,bound,vertical=CACHED[entry]
        raw=self.word(product)+65536*self.word(product+2);number=raw-(1<<32) if raw&0x80000000 else raw
        x1,x2,y1,y2=(self.word(a) for a in (0xCF0B,0xCF1B,0xCF0D,0xCF1D))
        first,second=(x1,x2) if vertical else (y1,y2);d=(second-first)&65535;d=d-65536 if d&32768 else d
        q,flags,alt_flags,bc,_,ix=division(number,d,int(second<first),self.r[1]&1,self.pair(2))
        self.push(entry+24);assert self.pop()==entry+24
        self.r[16:18]=[q&255,alt_flags];self.pair(2,bc);self.pair(8,(self.pair(8)&0xFF00)|(ix&255))
        base=y1 if vertical else x1;translated=(q+base)&65535
        de=base
        if translated&32768:point=(bound,0) if vertical else (0,bound)
        elif vertical:
            if translated&128:point=(bound,95)
            else:point=(bound,translated&255);de=((translated&255)<<8)|(base&255)
        else:
            value=255 if translated>>8 else translated&255;point=(value,bound);de=(base&0xFF00)|value
        offset=self.byte(0x9BA3);following=(offset+2)&255;previous=(following-1)&255
        self.byte(0x9000+offset,point[0]);self.byte(0x9000+((offset+1)&255),point[1]);self.byte(0x9BA3,following)
        self.pair(4,de);self.pair(6,0x9000|following)
        self.r[0:2]=[following,(following&0xA8)|(64 if following==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)]

    def helper(self,entry):
        if entry in PRODUCT:self.product(entry)
        elif entry in APPEND:
            product,cached=APPEND[entry];self.push(cached);self.product(product);assert self.pop()==cached;self.intersection(cached)
        elif entry in CACHED:self.intersection(entry)
        elif entry in COMPARE:
            a,b=COMPARE[entry];borrow=int(self.word(a)<self.word(b));left,right=self.word(a+2),self.word(b+2)
            self.pair(6,(left-right-borrow)&65535);self.pair(2,right);self.r[1]=sbc16_flags(left,right,borrow)
        elif entry in DELTA:
            a,b=DELTA[entry];left,right=self.word(a),self.word(b)
            self.pair(6,(left-right)&65535);self.pair(4,right);self.r[1]=sbc16_flags(left,right,0)
        elif entry in CORNERS:
            block=self.byte(0xCF03);self.r[0:2]=[block,logic_flags(block)|16]
            if block==0:self.pair(4,CORNERS[entry]);self.write_pair()
        elif entry==0xC6D3:
            self.pair(4,self.byte(0xCF1D)*256+self.byte(0xCF1B));self.write_pair()
        else:raise AssertionError(('неизвестный помощник',hex(entry)))

    def single_edge(self,stop=0x3FFF):
        self.byte(0xCF03,1)
        # Обычный индекс за массивом может направить запись связи прямо в код.
        # Поддерживаются исходный JR NZ и наблюдавшийся JR с тем же смещением.
        branch,offset=self.byte(0xC94B),self.byte(0xC94C)
        assert branch in (0x20,0x18) and offset==0x27,('неподдержанный изменённый вход ClipSingleEdge',branch,offset)
        if branch==0x20 and self.byte(0xCF0F)==0xF0:
            first,second=self.byte(0xCF0F),self.byte(0xCF1F)
            self.byte(0xCF0F,second);self.byte(0xCF1F,first)
            for offset in (0,2):
                first,second=self.word(0xCF0B+offset),self.word(0xCF1B+offset)
                self.word(0xCF1B+offset,first);self.word(0xCF0B+offset,second)
            self.r[2]=0xF0
        self.byte(0x9BA3,0)
        index=((~self.byte(0xCF0F))&240)|(self.byte(0xCF1F)&15)
        target=self.byte(0xCF00+index)+256*self.byte(0xD000+index)
        self.r[0:2]=[index,0x90];self.pair(4,0xC993);self.pair(6,target)
        for _ in range(3):self.push(0xC993)
        self.r[self.pc]=target;self.run(stop=stop)

    def run(self,stop=0x3FFF):
        helpers=set(PRODUCT)|set(APPEND)|set(CACHED)|set(COMPARE)|set(DELTA)|set(CORNERS)|{0xC6D3}
        for _ in range(150):
            pc=self.r[self.pc]
            if pc in (stop,0x3FFF):return
            if pc in helpers:
                self.helper(pc);self.r[self.pc]=self.pop();continue
            if pc==0xC993:
                count=self.byte(0x9BA3);self.pair(4,self.pop());self.pair(4,self.pop());self.r[0:2]=[count,cp_flags(count,4)]
                self.r[self.pc]=self.pop();continue
            if pc==0xC6EA:
                self.pair(0,self.pop());self.pair(2,self.pop());self.pair(6,self.pop())
                remaining=(self.r[2]-1)&255;old=self.pair(6);total=old+remaining;value=total&65535
                # ADD HL сохраняет S/Z/PV от DEC C, SCF сохраняет их и берёт X/Y из восстановленного A.
                dec_flags=(remaining&0xA8)|(64 if remaining==0 else 0)|(4 if remaining==127 else 0)|2
                self.pair(2,remaining);self.pair(6,value);self.r[1]=(dec_flags&0xC4)|(self.r[0]&0x28)|1
                self.special=True;self.r[self.pc]=self.pop();continue
            item=self.ops[pc];operation=item['operation'];following=pc+len(bytes.fromhex(item['hex']))
            if operation=='RET':self.r[self.pc]=self.pop();continue
            match=re.fullmatch(r'(JP|CALL) (?:(M|P|NZ),)?#([0-9A-F]+)',operation)
            if match:
                kind,condition,target=match.groups();taken=condition is None or (bool(self.r[1]&128) if condition=='M' else not self.r[1]&128 if condition=='P' else not self.r[1]&64)
                if taken:
                    if kind=='CALL':self.push(following)
                    self.r[self.pc]=int(target,16)
                else:self.r[self.pc]=following
                continue
            if operation=='LD HL,#CF07':self.pair(6,0xCF07)
            else:
                match=re.fullmatch(r'(BIT|SET) ([0-3]),\(HL\)',operation);assert match,operation
                kind,bit=match.groups();mask=1<<int(bit);address=self.pair(6);value=self.byte(address)
                if kind=='SET':self.byte(address,value|mask)
                else:
                    # В пути используются Z и сохранённый Carry, конечный AF переопределяет общий возврат.
                    self.r[1]=(self.r[1]&1)|16|(0 if value&mask else 0x44)
            self.r[self.pc]=following
        raise AssertionError('число шагов композиции')
