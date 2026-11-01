"""Создание предложения с настоящими рисователями и фильтр закрытия трёх панелей."""
import collections,hashlib,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckShipModelActions import remove
from skoolkit.simutils import SP


def prepare(base,selector=0,page=0x10):
 f=Fixture(base,page=page);m=f.memory;r=f.sim.registers
 for address,value in ((0x6FC6,31),(0xAA86,32),(0xAA50,33),(0x7F36,0)):
  put(m,address,value.to_bytes(2,'little'))
 for index,rect in ((31,(1,1,16,5)),(32,(1,7,24,12)),(33,(1,20,16,3)),(0,(0,0,32,5))):
  p=0xF0FD+16*index;put(m,p,(*rect,6 if index else 0,m[p+5]))
 put(m,0x983F,(0x38,0x4B,0xF3,0x4A,0));m[0x993D]=0x80;m[0x9E78]=0;m[0xCA20]=6;m[0x99A3]=0;m[0x99A4]=0
 put(m,0x984E,(0xE8,3));m[0x9850]=0;m[0x9851]=255;put(m,0xF3DE,(0xC5,0x6F,0x85,0xAA,0x4F,0xAA,1,1));r[0]=selector;r[4:6]=[0,33];r[6:8]=[0xAA,0x4F];p=0xF0FD+16*33;r[8:10]=[p>>8,p&255]
 return f


def main():
 _,_,base=make_context();counts=collections.Counter();rom_hash=None
 # Проверка полного обновления и его совпадения с отдельно исполненным генератором предложения.
 for seed in range(0,256,17):
  for active in (0,1,2,255):
   for page in (0x10,0x18):
    f=prepare(base,page=page);m=f.memory;r=f.sim.registers;m[0x99A3]=active;m[0xA8AF]=seed;put(m,0x98B4,bytes((0xA7,))*8)
    g=prepare(base,page=page);g.memory[0x99A3]=active;g.memory[0xA8AF]=seed;put(g.memory,0x98B4,bytes((0xA7,))*8);g.run(0xAC14)
    expected=bytes(g.memory[0x98B0:0x98C0]);calls=[]
    if active==1:assert expected[2:4]!=bytes((0xF3,0x4A))
    def observe(f,pc):
     if pc in (0xAC14,0xA49F,0x6FC5,0xAA85,0x7F35,0xA496):calls.append(pc)
    f.run(0xAA3D,observe)
    assert calls[-5:]==[0xA49F,0x6FC5,0xAA85,0x7F35,0xA496] and calls[:-5] and set(calls[:-5])=={0xAC14},calls
    assert bytes(m[0x98B0:0x98C0])==expected and bytes(m[0xA8AF:0xA8B2])==bytes(g.memory[0xA8AF:0xA8B2])
    assert m[0x99A3]==active and m[0x99A4]==0 and bytes(m[0x984E:0x9850])==bytes((0xE8,3))
    assert m[0x6F54]==255 and m[0x9B16]==0 and m.o7ffd==m[0x6306]==0x10 and r[SP]==0x8000 and r[10:12]==f.initial[10:12]
    assert f.wakes==2;counts['complete_offer_and_panels']+=1;counts['real_caption_im2']+=f.wakes
    rom_hash=hashlib.sha256(bytes(m.roms[1])).hexdigest()
 # Проверка всех селекторов, совпадения строк закрытия, callback и физического 128-байтового сдвига.
 keys={0x6FC5:31,0xAA85:32,0xAA4F:33}
 for selector in range(256):
  for same in (False,True):
   f=prepare(base,selector);m=f.memory;r=f.sim.registers;put(m,0x6307,(50,3 if same else 80));m[0xAEC7]=3;put(m,0x9A89,(0x20,0x5F));states=[]
   def observe(f,pc):
    if pc==0xAA5B:states.append(bytes(m[0xF3DE:0xF5DE]))
   f.run(0xAA58,observe);assert len(states)==1
   closed=selector<128 and selector!=1 and same
   if closed:
    wanted,flags,_=remove(states[0],keys,[33,31,32,33],0)
    assert bytes(m[0xF3DE:0xF5DE])==bytes(wanted) and bytes(m[0x9A89:0x9A8B])==bytes((0x58,0x9A))
    assert r[6:8]==[0x9A,0x58] and r[4:6]==[0,33];counts['close_group']+=1
   else:
    assert bytes(m[0xF3DE:0xF5DE])==states[0] and bytes(m[0x9A89:0x9A8B])==bytes((0x20,0x5F))
    counts['selector_or_row_no_close']+=1
   assert f.wakes==0 and m[0x99A3]==0 and r[SP]==0x8000
 report=dict(passed=True,cases_by_path=dict(counts),generator_checked_by_existing_independent_mission_offer_model=True,
  actual_generator_and_draws=True,full_offer_matches_separate_generator=True,all_selector_bytes=True,exact_close_order_and_physical_tails=True,
  native_rom_verified=False,model_rom_sha256=rom_hash,rom_only_read_as_data=True,independent_whole_redraw_bitmap=False,
  irq_only_at_caption_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionPanelActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
