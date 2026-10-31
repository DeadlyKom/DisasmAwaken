"""Числовая классификация C6, включая модульный обход при нештатном числе вершин."""


def outside(word,limit,negative_bit,positive_bit):
 if word&32768:return negative_bit
 return positive_bit if word>=limit else 0


def classify(buffer,next_offset,limit_first,limit_second):
 memory=bytearray(buffer);length=(next_offset-4)&255;count=(length*205)&255;count=count or 256;accumulated=0;written=[]
 for index in range(count):
  offset=(5*index)&255
  second=memory[offset]+256*memory[(offset+1)&255]
  if second>>8==128:return dict(buffer=memory,accepted=False,accumulator=0,previous_accumulator=accumulated,mask=0,length=length,written=written)
  first=memory[(offset+2)&255]+256*memory[(offset+3)&255]
  mask=outside(second,limit_second,2,1)|outside(first,limit_first,8,4)
  code=((mask^15)<<4)|mask;target=(offset+4)&255;memory[target]=code;written.append((target,code));accumulated|=code
 return dict(buffer=memory,accepted=True,accumulator=accumulated,previous_accumulator=accumulated,mask=mask,length=length,written=written)
