"""Независимое описание HR-потока, общая очередь байтов и слов битов, LZ и вставки литералов."""
import collections


class Stream:
 def __init__(self,data):
  self.data=data;self.position=12;self.remaining=16;self.word=self.read_word()
 def byte(self):
  value=self.data[self.position];self.position+=1;return value
 def read_word(self):return self.byte()|(self.byte()<<8)
 def bit(self):
  value=self.word>>15;self.word=(self.word<<1)&65535;self.remaining-=1
  if self.remaining==0:self.word=self.read_word();self.remaining=16
  return value
 def sentinel(self,start):
  value=start
  while True:
   high=value>>7;value=((value<<1)|self.bit())&255
   if not high:return value


def decode(data,lookahead=bytes(2)):
 assert data[:2]==b'HR' and int.from_bytes(data[4:6],'little')==len(data)
 size=int.from_bytes(data[2:4],'little');stream=Stream(data+lookahead);output=bytearray();counts=collections.Counter();window=0xBF;count_high=0;count_low=data[6]
 def literal():output.append(stream.byte());counts['literal_bytes']+=1
 def match(offset):
  nonlocal count_high,count_low
  length=(count_high<<8)|count_low;length=length or 65536;source=len(output)+offset
  assert source>=0 and len(output)+length<=size-6,('bad_reference',source,length,len(output),size)
  for i in range(length):output.append(output[source+i])
  count_high=count_low=0;counts['matches']+=1;counts['matched_bytes']+=length
 def triple(low):
  nonlocal count_high,count_low
  distance=256-low;source=len(output)-distance;assert source>=0 and len(output)+3<=size-6
  output.append(output[source]);count=(count_high<<8)|low;count=(count-1)&65535;count_high,count_low=count>>8,count&255
  output.append(stream.byte());output.append(output[source+2]);counts['reference_literal_reference']+=1
 def offset(mode):
  nonlocal count_high,count_low,window
  if mode=='one':
   match(-256+stream.sentinel(0xDF));counts['one_byte_short_offset']+=1;return
  prefix=stream.sentinel(0xBF)
  if mode=='two':
   high=(prefix+1)&255
   if high==0:match(-256+stream.sentinel(0xF7));counts['five_bit_short_offset']+=1;return
  else:
   prefix=(prefix+1)&255
   if prefix==0:high=stream.sentinel(window)
   else:
    high=(prefix+1)&255
    if high==0:match(-256+stream.sentinel(0xF7));counts['five_bit_short_offset']+=1;return
  low=stream.byte()
  if high!=255 or low<224:
   signed=((high<<8)|low)-65536;match(signed);counts['word_offsets']+=1;return
  escape=(((low<<1)&255)|(low>>7))^count_low;escape=(escape+1)&255
  if escape==0:
   window=(window>>1)|((window&1)<<7);counts['window_rotations']+=1
  else:triple((escape-16)&255)
 # Первым всегда идёт один буквальный байт, далее управляющий бит выбирает литерал либо код длины.
 literal()
 while True:
  assert len(output)<=size-6
  if stream.bit():literal();continue
  accumulated=1
  while True:
   value=stream.bit()*2+stream.bit()
   if value<3:break
   accumulated+=3
   if accumulated==16:value=0;break
  value+=accumulated
  if value!=4:
   count_low=value if value<4 else value-1
   offset('one' if count_low<2 else ('two' if count_low==2 else 'long'));continue
  # Специальный код длины 4 вводит тройку, пачку литералов, длинную длину либо конец потока.
  if stream.bit():
   triple(stream.sentinel(0xEF));continue
  if stream.bit():
   length=2*(stream.sentinel(0xEF)-0xEA)
   for _ in range(length):literal()
   count_high=0;counts['literal_runs']+=1;continue
  value=stream.sentinel(0xFC)
  if value==15:
   assert len(output)==size-6,('wrong_end',len(output),size)
   output.extend(data[6:12]);counts['restored_tail_bytes']+=6;break
  if value<15:count_high=value;count_low=stream.byte();counts['word_lengths']+=1
  else:count_low=value;counts['extended_byte_lengths']+=1
  offset('long')
 return dict(data=bytes(output),counts=dict(counts),stream_position=stream.position,bit_word=stream.word,remaining_bits=stream.remaining,
  window_mask=window,final_output_count_low=count_low,final_tail_word=int.from_bytes(data[10:12],'little'),lookahead_bytes_read=max(0,stream.position-len(data)))
