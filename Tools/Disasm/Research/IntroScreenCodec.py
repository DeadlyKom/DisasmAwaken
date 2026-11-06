"""Байтовый битовый поток экранного декодера, независимая грамматика и прямые/обратные ссылки."""
from collections import Counter


def physical(address):
    if address>=0x5800:return address
    high,low=address>>8,address&255
    value=(low&0xF8)^(high&7)
    return ((high&0xF8)|(low&7))*256+(((value<<2)|(value>>6))&255)


class Stream:
    def __init__(self,data):
        self.data=data;self.position=0;self.bits=0;self.remaining=0
    def byte(self):
        value=self.data[self.position];self.position+=1;return value
    def bit(self):
        if self.remaining==0:self.bits=self.byte();self.remaining=8
        value=self.bits>>7;self.bits=(self.bits<<1)&255;self.remaining-=1
        return value
    def group(self):
        if self.bit():return 0xFF
        a=self.bit()
        if self.bit():return 0xFD+a
        b=self.bit()
        if self.bit():return 0xF9+2*a+b
        c,d=self.bit(),self.bit()
        return 0xE9+8*a+4*b+2*c+d


def decode(data,limit=6912):
    stream=Stream(data);output=bytearray((stream.byte(),));counts=Counter(literals=1)
    groups=Counter();references=[]
    while True:
        if stream.bit():
            output.append(stream.byte());counts['literals']+=1
        else:
            code=stream.group();groups['length_'+format(code,'02X')]+=1
            if code==0xF9:
                extension=stream.byte()
                if extension==0:break
                length=257-extension;counts['extended_lengths']+=1
            elif code<0xF9:length=256-code
            else:length=257-code
            high=stream.group();groups['offset_'+format(high,'02X')]+=1
            reverse=stream.bit();low=stream.byte()
            offset=high*256+low-65536
            length=(length+(high<0xFD)-1)%256+1
            start=len(output)+offset
            # Копирование истории в выбранном направлении, новые байты доступны последующим выборкам.
            for index in range(length):
                source=start+(-index if reverse else index)
                assert 0<=source<len(output),(source,start,length,len(output),offset,reverse)
                output.append(output[source])
            counts['matches']+=1;counts['matched_bytes']+=length
            counts['reverse_matches' if reverse else 'forward_matches']+=1
            references.append(dict(position=len(output)-length,length=length,offset=offset,reverse=bool(reverse)))
        assert len(output)<=limit,('output_overflow',len(output),limit)
    return dict(data=bytes(output),counts=dict(counts),groups=dict(groups),references=references,
        stream_position=stream.position,remaining_bits=stream.remaining,bit_buffer=stream.bits)


class Writer:
    def __init__(self):self.data=bytearray();self.remaining=0;self.bit_index=None
    def byte(self,value):self.data.append(value)
    def bit(self,value):
        if self.remaining==0:
            self.bit_index=len(self.data);self.data.append(0);self.remaining=8
        self.remaining-=1;self.data[self.bit_index]|=value<<self.remaining
    def group(self,code):
        if code==0xFF:bits=(1,)
        elif 0xFD<=code<=0xFE:bits=(0,code-0xFD,1)
        elif 0xF9<=code<=0xFC:
            value=code-0xF9;bits=(0,value>>1,0,value&1,1)
        else:
            assert 0xE9<=code<=0xF8
            value=code-0xE9;bits=(0,(value>>3)&1,0,(value>>2)&1,0,(value>>1)&1,value&1)
        for value in bits:self.bit(value)
    def literal(self,value,first=False):
        if not first:self.bit(1)
        self.byte(value)
    def match(self,length,offset,reverse=False,extended=False):
        assert -5888<=offset<=-1
        high,low=(offset&65535)>>8,offset&255
        base=(length-(high<0xFD)-1)%256+1
        self.bit(0)
        if extended or base>23:
            assert 2<=base<=256
            self.group(0xF9);self.byte(257-base)
        else:
            assert 2<=base<=23
            self.group((257 if base<=7 else 256)-base)
        self.group(high);self.bit(int(reverse));self.byte(low)
    def end(self):self.bit(0);self.group(0xF9);self.byte(0)
