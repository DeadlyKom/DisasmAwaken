"""Полный путь кнопки Контракт с проверенными байтами локальной 48K ROM, без запуска Unreal."""
import argparse,collections,hashlib,json
from pathlib import Path
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckMapViewCenter import reference as center


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rom',required=True,type=Path);parser.add_argument('--basic48',required=True,type=Path);args=parser.parse_args()
 raw=args.rom.read_bytes();basic48=args.basic48.read_bytes();assert len(raw)==65536 and len(basic48)==16384
 selected_rom=raw[49152:];differences=[i for i,(a,b) in enumerate(zip(selected_rom,basic48)) if a!=b]
 assert differences==[0x6D] and selected_rom[:32]==basic48[:32] and selected_rom[1]==basic48[1]==0xAF
 _,_,base=make_context();assert bytes(Fixture(base).memory.roms[1])==selected_rom
 counts=collections.Counter();caption=bytes(base[0][0x24AA:]).split(bytes((10,)))[21]
 assert caption.decode('cp866')=='Контракт\rЦентрует изображение картыотносительно звезды следующего выбранного контракта.'
 for first,second in ((0x4B38,0x4AF3),(0x0038,0x0102),(0x0101,0xFFFF),(0x7F7F,0xA75D)):
  for cursor in (0x99A3,0x99AD,0xFFFF):
   for page in (0x10,0x18):
    for info in (False,True):
     for matched in (False,True):
      f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;m.roms=(m.roms[0],list(selected_rom));m.out7ffd(page)
      put(m,0x6DA9,(11,0));put(m,0xF1AD,(1,1,12,12,6,0));put(m,0x7690,(19,0));put(m,0xF22D,(16,0,16,24,6,13));put(m,0xF3DE,(0x8F,0x76,1,1) if info else (1,1))
      put(m,0x6300,(0,0,0,0,80,72));put(m,0x983F,(0x70,0x70,0x70,0x70,0));key=first.to_bytes(2,'little')+second.to_bytes(2,'little');put(m,0x98B0,key);m[0x98BF]=0xA7;put(m,0x7CCC,cursor.to_bytes(2,'little'))
      put(m,0x990A,bytes((255,0,0,0,0))*10+bytes((0x80,)));put(m,0x993D,bytes((255,0,0,0,0))*10+bytes((0x80,)));m[0x99A3]=0x80;m[0x99B4]=1;m[0x988E]=0;m[0x78D7]=0xA7
      if matched:put(m,0x990A,key+bytes((5,)))
      x=((first&255)<<8)|(second&255);y=(first&0xFF00)|(second>>8);cx,cy,_=center(x,y,80,72);reads=[];tails=[]
      def observe(f,pc):
       if pc in (0x7CCF,0x7CDE):assert m[1]==0xAF;reads.append(pc)
       if pc==0x7D14:
        assert r[4:8]==[first>>8,first&255,second>>8,second&255];tails.append(pc)
       if pc==0x7B9B:
        assert bytes(m[0x6300:0x6304])==bytes((cx&255,cy&255,cx>>8,cy>>8))
      f.run(0x7CC6,observe)
      assert reads==[0x7CCF,0x7CDE] and tails==[0x7D14] and bytes(m[0x7CCC:0x7CCE])==bytes((0xA3,0x99))
      assert bytes(m[0x9844:0x9849])==key+bytes((5 if matched else 0,)) and bytes(m[0x98B0:0x98B4])==key and m[0x98BF]==1
      assert bytes(m[0x6300:0x6304])==bytes((cx&255,cy&255,cx>>8,cy>>8)) and m[0x78D7]==0xA7
      assert m.o7ffd==m[0x6306]==0x10 and m[0x9B16]==0 and f.wakes==2+int(info) and r[10:12]==f.initial[10:12]
      counts['full_contract_map']+=1;counts['real_im2']+=f.wakes
 report=dict(passed=True,cases_by_path=dict(counts),caption=caption.decode('cp866').split('\r')[0],source_text_index=20,
  checked_local_rom_name=args.rom.name,combined_rom_sha256=hashlib.sha256(raw).hexdigest(),identified_48k_chunk_offset=49152,
  checked_local_48k_name=args.basic48.name,basic48_sha256=hashlib.sha256(basic48).hexdigest(),absolute_byte_0001=175,
  full_48k_chunk_exactly_matches_separate_image=False,separate_48k_difference_offsets=differences,
  selected_rom_chunk_sha256=hashlib.sha256(selected_rom).hexdigest(),full_chunk_matches_previous_model_rom=True,
  rom_assigned_to_model_bank1=True,unreal_process_state_verified=False,
  source_absolute_reads_preserved=True,always_selects_first_offer_key_for_stable_af=True,independent_center_coordinates=True,
  original_map_and_optional_information_redraw=True,independent_whole_bitmap=False,irq_only_at_halt=True,music_disabled=True,
  rom_opcodes_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ContractRomProfileVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
