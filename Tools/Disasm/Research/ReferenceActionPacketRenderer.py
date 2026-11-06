"""Композиционный эталон DD23, дети заменены проверенными числовыми формулами, не Z80-симулятором."""
from ReferenceActionClipping import Clipping
from ReferenceActionFaceOrientation import face
from ReferenceActionPolygonFill import fill
from ActionPolygonFillOracle import registers as fill_registers
from CheckActionLineRaster import raster
from PreviewEdgeRasterOracle import arithmetic
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionPolygon import Polygon as ClipPolygon
from collections import Counter


class PacketRenderer(Clipping):
    def inc(self,index,subtract=False):
        old=self.r[index];value=(old+(-1 if subtract else 1))&255
        self.r[index]=value
        self.r[1]=(value&0xA8)|(64 if value==0 else 0)|(16 if old&15==(0 if subtract else 15) else 0)|(4 if old==(128 if subtract else 127) else 0)|(2 if subtract else 0)|(self.r[1]&1)

    def exchange_af(self):self.r[0:2],self.r[16:18]=self.r[16:18],self.r[0:2]

    def orientation(self):
        self.events['orientation']+=1
        start=self.r[self.sp];pointer=self.pair(6);bc=self.pair(2);count=self.r[0]
        indices=[self.byte(pointer+1+i) for i in range(3 if count<5 else 5)]
        points=[(self.word(0x8E00+i),self.word(0x8E02+i)) for i in indices]
        result=face(points,count,self.pair(8))
        # Все остаточные рамки настоящего вычисления ориентации сохраняются в эталоне RAM.
        for address,value in ((start-2,bc),(start-4,pointer),(0xDFE4,start-4),
            (start-6,result['v_first']),(start-6,result['v_second']),
            (start-6,0xDFF8),(start-8,result['first']['stack_af'][0]*256+result['first']['stack_af'][1]),
            (start-6,result['first']['high']),(start-8,result['first']['low']),
            (start-10,0xDFFE),(start-12,result['second']['stack_af'][0]*256+result['second']['stack_af'][1])):
            self.word(address,value)
        self.r[0:2]=result['af']
        for position,value in ((4,result['low']),(8,result['ix']),(18,result['first']['bc']),
                               (20,result['first']['low']),(22,result['first']['high'])):
            self.pair(position,value)
        self.r[self.pc]=self.pop()

    def line(self):
        self.events['line']+=1
        first=(self.byte(0x8D2A),self.byte(0x8D2B));second=(self.byte(0x8D2C),self.byte(0x8D2D))
        opcode,branch,offset=self.byte(0x8D4E),self.byte(0x8D4F),self.byte(0xDE0F)
        table=[self.byte(0xE000+offset+i) for i in range(8)]
        result=raster(first,second,opcode,branch,table,self.banks[2]);self.writes+=result['writes']
        if result['degenerate']:
            self.r[1]=0x42;self.pair(6,0);self.pair(4,second[1]*256+second[0])
        else:
            self.word(0xDEED,self.r[self.sp]);self.byte(result['patch'][0],opcode);self.byte(result['patch'][1],branch)
            for position,key in ((2,'bc'),(4,'de'),(6,'hl')):self.pair(position,result[key])
            self.r[0:2]=result['af'];self.r[16:18]=result['alt_af']
        self.r[self.pc]=self.pop()

    def polygon(self):
        self.events['fill']+=1
        count=self.byte(0x9BA3)//2;mode=self.byte(0xD560);hl=self.pair(6)
        vertices=[(self.byte(0x9001+2*i),self.byte(0x9000+2*i)) for i in range(count)]
        self.banks,writes=fill(self.banks,vertices,mode,hl,self.r[self.sp]);self.writes+=writes
        result=fill_registers(vertices,mode);incoming_flags=self.r[1]
        self.r[0:2]=result['af'];self.pair(2,result['bc']);self.pair(4,result['de'])
        if result['degenerate']:
            value,flags=arithmetic(count*2,1,True)
            self.r[16:18]=[value,(flags&254)|(incoming_flags&1)]
        else:
            for position,key in ((8,'ix'),(10,'iy'),(18,'alt_bc'),(20,'alt_de'),(22,'alt_hl')):self.pair(position,result[key])
            self.r[16:18]=result['alt_af']
        self.r[self.pc]=self.pop()

    def skip(self,count):
        self.pair(2,(count+1)&255);self.pair(6,(self.pair(6)+count+1)&65535)

    def listed_codes(self):
        self.events['listed_codes']+=1
        pointer=self.pair(6);count=self.r[2];aggregate=0
        self.word(self.r[self.sp]-2,pointer)
        for consumed in range(1,count+1):
            index=self.byte(pointer+consumed);code=self.byte(0x8E00+((index+4)&255))
            if code==0:break
            aggregate|=code
        self.r[0:2]=[0,0x45] if code==0 else [aggregate,logic_flags(aggregate)]
        if code==0:self.events['zero_code_abort']+=1
        self.r[3]=aggregate;self.r[9]=count;self.pair(4,pointer+1+consumed)
        self.r[self.pc]=self.pop()

    def clip_polygon(self):
        self.events['clip_polygon']+=1
        child=ClipPolygon(self.banks,self.r,self.ops,self.pc,self.sp);child.polygon()
        self.banks,self.r=child.banks,child.r;self.writes+=child.writes

    def clipped_line(self,count):
        self.r[8]=0x8E;self.r[0]=self.byte(self.pair(6));self.r[9]=self.r[0];self.pair(6,self.pair(6)+1)
        address=0x8E00+self.r[9]
        self.pair(4,self.word(address));self.word(0x8D3E,self.pair(4))
        self.pair(4,self.word(address+2));self.word(0x8D4A,self.pair(4))
        self.r[0]=self.byte(address+4);self.byte(0x8D4D,self.r[0])
        for _ in range(count-1):
            self.r[0]=self.byte(self.pair(6));self.r[9]=self.r[0];self.pair(6,self.pair(6)+1)
            self.push(self.pair(2));self.push(self.pair(6))
            self.pair(6,self.word(0x8D3E));self.word(0x8D3A,self.pair(6))
            self.pair(6,self.word(0x8D4A));self.word(0x8D3C,self.pair(6))
            first_code=self.byte(0x8D4D);self.r[0]=first_code;self.byte(0x8D4C,first_code);self.r[2]=first_code
            address=0x8E00+self.r[9]
            self.pair(4,self.word(address));self.word(0x8D3E,self.pair(4))
            self.pair(4,self.word(address+2));self.word(0x8D4A,self.pair(4))
            second_code=self.byte(address+4);self.r[1]=logic_flags(first_code)|16
            self.r[0]=second_code;self.byte(0x8D4D,second_code)
            draw=False
            if first_code and second_code:
                aggregate=first_code|second_code;self.r[2]=aggregate
                self.r[0:2]=[(~aggregate)&240,logic_flags((~aggregate)&240)|16]
                if self.r[0]==0:
                    self.r[0:2]=[aggregate&15,logic_flags(aggregate&15)|16]
                    if self.r[0]==0:
                        for target,source in ((0x8D2A,0x8D3A),(0x8D2B,0x8D3C),(0x8D2C,0x8D3E),(0x8D2D,0x8D4A)):
                            self.r[0]=self.byte(source);self.byte(target,self.r[0])
                        draw=True
                    else:
                        # Копирование двух полных точек и настоящий профиль рамки PUSH IX/CALL ClipSingleEdge.
                        for target,source in ((0xCF0B,0x8D3A),(0xCF0D,0x8D3C),(0xCF1B,0x8D3E),(0xCF1D,0x8D4A)):
                            self.pair(6,self.word(source));self.word(target,self.pair(6))
                            if target==0xCF0D:self.r[0]=self.byte(0x8D4C);self.byte(0xCF0F,self.r[0])
                        self.r[0]=self.byte(0x8D4D);self.byte(0xCF1F,self.r[0])
                        self.push(self.pair(8));self.push(0xDD06)
                        self.events['clip_segment']+=1
                        child=Clipping(self.banks,self.r,self.ops,self.pc,self.sp);child.single_edge(stop=0xDD06)
                        self.banks,self.r=child.banks,child.r;self.writes+=child.writes
                        self.pair(8,self.pop())
                        if self.r[1]&64:
                            self.pair(6,0x9000)
                            for i,target in enumerate((0x8D2A,0x8D2B,0x8D2C,0x8D2D)):
                                self.r[0]=self.byte(self.pair(6));self.byte(target,self.r[0])
                                if i<3:self.inc(7)
                            draw=True
            if draw:self.push(0xDCD6);self.line()
            self.pair(6,self.pop());self.pair(2,self.pop());self.r[2]=(self.r[2]-1)&255

    def render(self,clipped=False):
        self.events=Counter()
        for _ in range(1024):
            header=self.byte(self.pair(6));self.r[0:2]=[header,logic_flags(header)|16]
            if header==0:
                self.r[self.pc]=self.pop();return
            count=header&15;assert count>=2
            self.r[2]=count;self.r[0:2]=[count,logic_flags(count)|16]
            if not header&128:
                assert count>=3
                self.push(0xDBC9 if clipped else 0xDD2F);self.orientation()
                if not self.r[1]&128:
                    self.events['face_rejected']+=1
                    self.r[0]=1;self.byte(0x8D5A,1);self.skip(count);continue
                self.r[0:2]=[0,0x54];self.byte(0x8D5A,0)
                if clipped:
                    self.push(0xDBD3);self.listed_codes()
                    if self.r[1]&1:self.skip(count);continue
                    aggregate=self.r[3];self.r[0:2]=[(~aggregate)&240,logic_flags((~aggregate)&240)|16]
                    if self.r[0]:self.skip(count);continue
                mode=(header>>4)&7;assert mode<5
                self.pair(6,self.pair(6)+1);self.r[0:2]=[mode,logic_flags(mode)|16];self.byte(0xD560,mode)
                if clipped:
                    self.r[0:2]=[self.r[3]&15,logic_flags(self.r[3]&15)|16]
                    if self.r[0]:
                        self.push(0xDC0E);self.clip_polygon()
                        if not self.r[1]&1:self.push(0xDC11);self.polygon()
                        continue
                self.pair(4,0x9000);self.r[0],self.r[1]=arithmetic(count,count)
                self.byte(0x9BA3,self.r[0]);self.r[2]=0x8E
                self.r[0]=count;self.r[1]=(self.r[1]&0xC4)|(count&0x28)
                self.exchange_af()
                # Копирование младших координат списка без отсечения, с настоящим чередованием AF.
                for i in range(count):
                    self.r[3]=self.byte(self.pair(6));self.pair(6,self.pair(6)+1)
                    self.r[0]=self.byte(self.pair(2));self.byte(self.pair(4),self.r[0]);self.inc(5)
                    self.inc(3);self.inc(3)
                    self.r[0]=self.byte(self.pair(2));self.byte(self.pair(4),self.r[0]);self.inc(5)
                    self.exchange_af();self.inc(0,True)
                    if i<count-1:self.exchange_af()
                self.push(0xDC08 if clipped else 0xDD5F);self.polygon();continue
            if header&64 and self.byte(0x8D5A):
                self.events['attached_line_rejected']+=1
                self.skip(count);continue
            self.inc(2,True);mode=header&0x30
            opcode,branch,offset=(0xA1,0x30,0x18) if mode==0 else (0xB1,0x38,0x10) if mode==0x10 else (0xA9,0x38,0x10)
            self.r[0:2]=[offset,0x54 if mode==0 else cp_flags(mode,0x10)]
            self.pair(6,self.pair(6)+1);self.pair(4,branch*256+opcode)
            self.word(0x8D4E,branch*256+opcode);self.byte(0xDE0F,offset)
            if clipped:self.clipped_line(count);continue
            self.r[4]=0x8E;self.r[5]=self.byte(self.pair(6));self.pair(6,self.pair(6)+1)
            self.r[0]=self.byte(self.pair(4));self.byte(0x8D2C,self.r[0]);self.inc(5);self.inc(5)
            self.r[0]=self.byte(self.pair(4));self.byte(0x8D2D,self.r[0])
            for _ in range(count-1):
                self.r[4]=0x8E;self.r[5]=self.byte(self.pair(6));self.pair(6,self.pair(6)+1)
                self.push(self.pair(2));self.push(self.pair(6))
                self.pair(6,self.word(0x8D2C));self.word(0x8D2A,self.pair(6))
                self.r[0]=self.byte(self.pair(4));self.byte(0x8D2C,self.r[0]);self.inc(5);self.inc(5)
                self.r[0]=self.byte(self.pair(4));self.byte(0x8D2D,self.r[0])
                self.push(0xDDCA);self.line()
                self.pair(6,self.pop());self.pair(2,self.pop());self.r[2]=(self.r[2]-1)&255
        raise AssertionError('конечный поток записей отсутствует')
