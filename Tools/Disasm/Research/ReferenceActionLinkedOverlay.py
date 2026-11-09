"""E804, связь по R, знаки и три переполнения перед реальным XOR-сегментом."""
from ReferenceActionOverlayPair import OverlayPairMachine
from CheckActionRecordIndex import decode
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceControlsBufferPoints import sub16_flags


class LinkedOverlayMachine(OverlayPairMachine):
    def linked_vectors(self):
        ix=self.r[8]*256+self.r[9];linked=self.read(ix+11);pointer=self.word(0xE796)
        if linked==26:
            pointer=0xA780;self.r[0:2]=[26,logic_flags(26)|16];self.pair(2,0);self.pair(4,65535);self.pair(6,0xFFB0)
            assigned=((0xD9B6,0),(0xAF48,0),(0xAF56,0),(0xAF69,0),(0xD7C4,0xFFB0),(0xD7A2,65535));cost=24
        elif self.read(pointer+27)==128:
            self.pair(10,pointer);self.r[0:2]=[128,0x41];self.path.append('linked_marker');return self.finish(11)
        else:
            high=self.read(pointer+27);self.r[0:2]=[high,logic_flags(high)|16]
            values=[self.word(pointer+offset) for offset in (0,2,4,26,28,30)]
            self.pair(2,values[3]);self.pair(6,values[4]);self.pair(4,values[5])
            assigned=tuple(zip((0xAF48,0xAF56,0xAF69,0xD9B6,0xD7C4,0xD7A2),values));cost=44
        self.pair(10,pointer)
        for address,word in assigned:self.put_word(address,word)
        return self.finish(cost)

    def linked_overlay(self,ops):
        self.rendered=False;ix=self.r[8]*256+self.r[9];high=self.read(ix+27)
        self.r[0:2]=[high,(cp_flags(high,128)&0xC4)|(high&0x28)|1];self.m1(5)
        if high==128:self.path.append('current_marker');return self.finish()
        self.pair(2,self.word(ix+26));self.pair(6,self.word(ix+28));self.pair(4,self.word(ix+30));self.exx();self.m1(12)
        self.call(0xE794,0xE81F,self.linked_vectors);self.m1(1)
        if self.r[1]&1:return self.finish()
        self.m1(2);random=self.r[15];self.r[0:2]=[random,cp_flags(random,self.read(0xE823))];self.m1(2)
        if random>=self.read(0xE823):
            iy=self.r[10]*256+self.r[11];self.put(iy+12,self.read(iy+12)|1)
            saved=self.r[6]*256+self.r[7];stack=self.r[12]
            self.put_word(stack-2,saved);self.put_word(stack-4,ix);self.put_word(stack-4,0xE831)
            index,flags,_=decode(ix);self.r[0:2]=[index,flags];self.put(iy+11,index);self.m1(19)
            self.path.append('link_written')
        else:self.path.append('link_skipped')
        return self.check_depth_signs(ops)

    def check_depth_signs(self,ops):
        self.rendered=False;ix=self.r[8]*256+self.r[9]
        selected_high=self.r[4];self.exx();a=selected_high&self.r[4]
        self.r[0:2]=[a,logic_flags(a)|16];self.m1(4)
        if a&128:self.path.append('both_depths_negative');return self.finish()
        stack=self.r[12];hl=self.r[6]*256+self.r[7];de=self.r[4]*256+self.r[5];bc=self.r[2]*256+self.r[3]
        for index,(left,right,cost) in enumerate(((self.word(0xD9B6),bc,8),(self.word(0xD7A2),de,8),(hl,self.word(0xD7C4),11))):
            self.put_word(stack-2,hl)
            if index==2:self.put_word(stack-4,de)
            flags=sub16_flags(left,right);self.r[1]=(flags&0xC4)|(a&0x28)|1;self.m1(cost)
            if flags&4:self.path.append('overflow_'+str(index));return self.finish()
        self.put_word(stack-2,ix);self.r[12]-=2;self.m1(2)
        self.call(0xEB41,0xE85F,lambda:self.overlay_pair(ops))
        self.r[12]+=2;self.pair(8,ix);self.r[1]=logic_flags(self.r[0])|16;self.m1(4)
        self.path.append('overlay_returned');return self.finish()
