"""Приветственное окно, все размеры ключа и реальные банковые печататели."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckWorldSignature import signature,logical_flags
from CheckCompactDecimal import digits
from skoolkit.simutils import SP


def main():
 _,map_source,base=make_context();counts=collections.Counter();keys={};prefixes=[];cursor=0x2722
 for _ in range(16):
  end=map_source.index(10,cursor);prefixes.append(map_source[cursor:end]);cursor=end+1
 # Поиск реальных ключей каждого значения L по независимой формуле, исходный каталог не подменяется.
 for variant in range(256):
  key=(0x4B38,0x4A00,variant);size=signature(*key)['size'];keys.setdefault(size,key)
 assert set(keys)==set(range(1,17))
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));rows=next(g['instructions'] for g in flow if g['name']=='Station')
 direct={i['address']+3 for i in rows if 0x7955<=i['address']<0x79BD and i['operation'].startswith('CALL ')}
 templates=[];p=0xCD82
 for _ in range(4):
  templates.append(p)
  while base[0][p-0xC000] not in (1,10):p+=1
  p+=1
 final=p
 def prepare(page,rect):
  f=Fixture(base,page=page);m=f.memory
  # Проверка оригинального кода B400, список размещается в исходной StationState.DrawList.
  assert bytes(m[0xB400:0xB408])==bytes(base[2][0x3400:0x3408])
  put(m,0x7956,(45,0));p=0xF0FD+16*45;put(m,p,(*rect,7,m[p+5]));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(0x55,0x79,1,1));return f
 finals=[]
 # Проверка полного и ограниченного окна, двух экранных страниц и всех шестнадцати характеристик.
 for size,key in sorted(keys.items()):
  for page in (0x10,0x18):
   for rect in ((0,0,32,24),(0,0,12,8),(0,0,2,3)):
    f=prepare(page,rect);m=f.memory;r=f.sim.registers;put(m,0x983F,(*key[0].to_bytes(2,'little'),*key[1].to_bytes(2,'little'),key[2]));seen=[];buffer_prints=0;expected_name=prefixes[key[1]&15]+b'-'+digits((key[1]&0xF0)|((key[0]>>8)&15))+b'/'+digits(((key[0]>>8)&0xF0)|((key[1]>>8)&15))+b'-'+bytes([0x80+(key[1]>>12),10])
    previous=None;recent=collections.deque(maxlen=24);continuation=None
    def observe(f,pc):
     nonlocal buffer_prints,previous,continuation
     r=f.sim.registers;m=f.memory;sp=r[SP];ret=m[sp]+256*m[sp+1]
     recent.append((hex(pc),hex(sp),m.o7ffd,r[0],hex(r[6]*256+r[7]),hex(ret)))
     assert pc!=0x67E0,('unexpected_ship_list',list(recent))
     assert m.o7ffd in (0x10,0x11,0x18,0x19),('unexpected_bank',list(recent))
     assert pc>=0x6000 or pc==0x3FFF,('unexpected_external_code',list(recent))
     if pc in (0x7966,0x7976,0x79AA):
      # Проверка исходной вершины перед созданием FWelcomeTextFrame через PUSH HL.
      assert sp==0x7FFE;continuation=r[6]*256+r[7]
     caller=previous;previous=pc
     if caller is None or caller+3 not in direct or ret!=caller+3:return
     if caller in (0x7967,0x796F,0x7980,0x7983,0x7989,0x799E,0x79A3,0x79AB,0x79B5):
      # Проверка двух физических слов FWelcomeTextFrame под возвратом вложенного CALL.
      assert sp==0x7FFA and m[sp+2]+256*m[sp+3]==continuation and m[sp+4:sp+6]==[255,63]
      counts['physical_continuation_frames']+=1
     hl=r[6]*256+r[7];de=r[4]*256+r[5]
     if pc==0xBD08:
      seen.append(('text',hl))
      if hl==0x630B:
       assert bytes(m[hl:hl+len(expected_name)])==expected_name;buffer_prints+=1
     elif pc==0xA464:seen.append(('current',))
     elif pc==0xA37A:seen.append(('lf',hl,r[0]))
     elif pc==0xE6AB:seen.append(('name',hl,de))
     elif pc==0xC8C9:seen.append(('variant',hl,de,r[0]))
     elif pc==0xBCAB:seen.append(('number',r[2]*256+r[3]))
    try:f.run(0x7955,observe)
    except AssertionError as error:raise AssertionError((size,key,page,rect,seen[-12:],f.trace.writes[-12:],m[0x6306],r[SP],bytes(m[0x7FE0:0x8000]).hex())) from error
    # Ожидаемая последовательность шаблонных фрагментов сохраняет продолжения через PUSH HL.
    text_calls=[v for v in seen if v[0]=='text'];assert text_calls[0]==('text',templates[0]) and buffer_prints==1
    assert [v for v in seen if v[0]!='text']==[('current',),('lf',0xCCF3,size-1),('name',key[0],key[1]),('variant',key[0],key[1],key[2]),('current',),('number',5*size)],seen
    assert len(text_calls)==5 and m[0xBD26]==1 and m.o7ffd==m[0x6306]==page and f.wakes==1,(seen,m[0xBD26],m.o7ffd,m[0x6306],f.wakes)
    result=signature(*key)
    assert r[4:6]==[result['region'],result['minor']] and r[16:18]==[page,logical_flags(page)]
    assert r[18:24]==[f.initial[2],f.initial[3],(key[1]&0xFFF0)>>8,key[1]&0xF0,(key[0]&0xF0FF)>>8,key[0]&255]
    assert r[8:12]==f.initial[8:12] and r[14]==f.initial[14] and r[26:28]==f.initial[26:28]
    if rect==(0,0,32,24):
     assert text_calls==[('text',templates[0]),('text',templates[1]),('text',0x630B),('text',templates[2]),('text',templates[3])],text_calls
     assert r[6]*256+r[7]==final and r[:2]==[10,0x4A] and r[2:4]==[0,10]
     counts['full_template_and_number']+=1
    else:counts['limited_windows_continue_after_text_refusal']+=1
    finals.append(dict(size=size,page=page,rectangle=rect,hl=r[6]*256+r[7],bc=r[2]*256+r[3],af=r[0]*256+r[1]));counts['real_caption_im2']+=f.wakes
 # Проверка отключённой обёртки для всех F, ни шаблон, ни расчёт ключа не исполняются.
 f=prepare(0x10,(0,0,32,24));m=f.memory;s=f.sim;m[0x7955]=0xC9;before=[bytes(b) for b in m.banks]
 for flags in range(256):
  s.registers[:]=f.initial;r=s.registers;r[1]=flags;s.run(start=0x7955,stop=0x3FFF)
  assert r[:12]==[f.initial[0],flags,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
  counts['disabled_all_flags']+=1
 assert [bytes(b) for b in m.banks]==before
 report=dict(passed=True,cases_by_path=dict(counts),all_key_sizes=sorted(keys),template_segments=templates,template_end=final,
  real_bank_and_text_calls=True,independent_name_and_signature_reference=True,independent_whole_bitmap=False,
  original_im2_only_at_caption_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/WelcomePanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
