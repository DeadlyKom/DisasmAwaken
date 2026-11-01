"""Физические слова семи выделенных команд, между ними находится исполняемый код."""
import re
TABLES=[]
for channel,start,extra,targets,gate in (
 ('A',0xDDC0,0xDDCE,('SetToneSlideA','SetTonePortamentoA','SetSamplePositionA','SetOrnamentPositionA'),'ReadGateTimingA'),
 ('B',0xDDE0,0xDDEE,('SetToneSlideB','SetTonePortamentoB','SetSamplePositionB','SetOrnamentPositionB'),'ReadGateTimingB'),
 ('C',0xDE00,0xDE0E,('SetToneSlideC','SetTonePortamentoC','SetSamplePositionC','SetOrnamentPositionC'),'ReadGateTimingC')):
 entries=tuple((n,label,target) for n,label,target in zip(range(1,6),('Slide','Portamento','SamplePos','OrnamentPos','Gate'),(*targets,gate)))
 TABLES.append(('Deferred'+channel,'Source/Music/Data/Effects'+channel+'.asm',start,entries))
 TABLES.append(('ExtraDeferred'+channel,'Source/Music/Data/ExtraEffects'+channel+'.asm',extra,((8,'EnvelopeSlide','ReadEnvelopeSlide'),(9,'Tempo','SetRowTempo'))))
TABLES=tuple(TABLES)


def render(source,table):
 module,path,start,entries=table;lines=['                module '+module,'                ; Документация [отложенные музыкальные команды](../../../Docs/MusicEffects.md)','                assert $ == #'+format(start,'04X')];labels={}
 for n,(opcode,label,target) in enumerate(entries):
  address=start+2*n;labels[module+'.'+label]=address;line=(label+':').ljust(16)+'FMusicEffectTarget { @Music.'+target+'.Entry }';assert len(line)<80;lines.append(line.ljust(80)+'; Handler, команда '+format(opcode,'02X')+', исходное слово '+format(int.from_bytes(source[address-0xDB00:address-0xDB00+2],'little'),'04X'))
 lines+=['                assert $ == #'+format(start+2*len(entries),'04X'),'                endmodule'];return '\n'.join(lines)+'\n',labels


def parse(text,table,symbols):
 module,path,start,entries=table;found=[];labels={}
 for line in text.splitlines():
  code=line.partition(';')[0].rstrip()
  if not code.strip():continue
  op=code[16:].strip()
  if op.lower().startswith(('module ','assert ')) or op.lower()=='endmodule':continue
  match=re.fullmatch(r'([A-Za-z][A-Za-z0-9_]{0,14}):\s+FMusicEffectTarget\s*\{\s*@([A-Za-z][A-Za-z0-9_.]*)\s*\}',code)
  if not match:raise ValueError('Недопустимая строка музыкальной таблицы '+code)
  n=len(found);assert n<len(entries);opcode,label,target=entries[n];assert match[1]==label and match[2]=='Music.'+target+'.Entry'
  value=symbols[match[2].upper()];found.append(value);labels[(module+'.'+label).upper()]=start+2*n
 assert len(found)==len(entries)
 return b''.join(v.to_bytes(2,'little') for v in found),labels
