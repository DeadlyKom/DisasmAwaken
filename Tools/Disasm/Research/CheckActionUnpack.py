"""Полётная копия HR, точное соответствие инструкций и все исходные ресурсы."""
import collections
import hashlib
import json
import re
from CheckUnpackResource import ROOT,payload,decode,Simulator,get_registers,PC,SP,I,IFF,IM
from PackedRefreshTrace import PackedRefreshTrace


class RecordedFlat(list):
    recording=False
    def __setitem__(self,address,value):
        if self.recording:
            assert isinstance(address,int)
            self.writes.append((address,value))
        super().__setitem__(address,value)


def main():
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    station=[i for r in flow if r['name']=='Station' for i in r['instructions'] if 0x9EFF<=i['address']<0xA020]
    action=[i for r in flow if r['name']=='Action' for i in r['instructions'] if 0xAB23<=i['address']<0xAC44]
    delta=0xC24
    assert len(station)==len(action)==184
    # Проверка всех мнемоник, длин и целей, постоянные адреса данных не сдвигаются.
    for old,new in zip(station,action):
        normalized=re.sub(r'#([0-9A-F]{4})',lambda m:'#'+format(int(m[1],16)-delta,'04X')
            if 0xAB23<=int(m[1],16)<0xAC44 else m[0],new['operation'])
        assert old['address']+delta==new['address'] and old['operation']==normalized
        assert len(old['hex'])==len(new['hex'])
        raw=bytes.fromhex(new['hex'])
        assert payload(17)[new['offset']:new['offset']+len(raw)]==raw
    records=json.loads((ROOT/'Tools/Disasm/Reports/Screens.json').read_text('utf-8'))
    hashes={(r['slot'],r['index']):r['sha256'] for r in json.loads((ROOT/'Tools/Disasm/Reports/DecodedScreens.json').read_text('utf-8'))}
    original=[0]*65536;original[0x6000:]=payload(17)
    initial=get_registers({'SP':0x5FFE,'AF':0x5A5D,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
        '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    initial[I],initial[IFF],initial[IM]=0xA7,1,2
    counts=collections.Counter();packets=collections.Counter();profiles=[]
    for record in records:
        raw=payload(record['slot'])[record['offset']:record['offset']+record['packed_size']]
        size=record['unpacked_size'];packed=len(raw)
        for source,dest in ((0xC000,0x4000),(0xB000,0xC000),(0xD000,0xC000),(0x6000,0x4000)):
            m=RecordedFlat(original);m[source:source+packed]=raw;m[0x5FFE:0x6000]=[255,63]
            base=max(source,dest+size-packed)
            assert max(source,0xAB23)>=min(source+packed,0xAC44)
            assert max(dest,0xAB23)>=min(dest+size,0xAC44)
            expected=decode(raw,bytes(m[base+packed:base+packed+2]))
            assert hashlib.sha256(expected['data']).hexdigest()==hashes[record['slot'],record['index']]
            # Создание полной ожидаемой RAM вне временных байтов CPU-стека.
            wanted_memory=list(m)
            wanted_memory[base+1:base+packed]=raw[1:]
            wanted_memory[dest:dest+size]=expected['data']
            simulator=Simulator(m,config={'fast_ldir':False});r=simulator.registers;r[:]=initial
            r[15]=(len(profiles)*73)&255
            refresh=PackedRefreshTrace(action,r[15])
            r[6:8]=[source>>8,source&255];r[4:6]=[dest>>8,dest&255];r[PC]=0xAB23
            native=collections.Counter();tail=0;frame=False;m.writes=[];m.recording=True
            for steps in range(600000):
                pc=r[PC]
                if pc==0x3FFF:break
                if pc==0xAB59 and not frame:
                    assert r[SP]==0x5FF8 and bytes(m[0x5FF8:0x6000])==raw[6:12]+bytes((255,63));frame=True
                for address,key in ((0x9F35,'literal_bytes'),(0xA009,'literal_bytes'),(0x9F9A,'matches'),
                    (0x9FB0,'reference_literal_reference'),(0x9FA0,'window_rotations'),(0x9FD4,'word_lengths')):
                    if pc==address+delta:native[key]+=1
                if pc==0x9FE6+delta:
                    assert tail<3 and r[SP]==0x5FF8+2*tail
                    assert bytes(m[r[SP]:r[SP]+2])==raw[6+2*tail:8+2*tail];tail+=1
                refresh.before(m,pc,r[15])
                simulator.run()
                refresh.after(r[15])
            else:raise AssertionError(('instruction_limit',record['slot'],record['index'],r[PC]))
            m.recording=False
            assert bytes(m[dest:dest+size])==expected['data'] and frame and tail==3
            assert r[:8]==[15,0x4A,expected['remaining_bits'],16,expected['window_mask'],4,
                expected['bit_word']>>8,expected['bit_word']&255]
            assert r[8]*256+r[9]==base+expected['stream_position'] and r[10:12]==initial[10:12]
            assert r[16:18]==initial[16:18]
            assert r[18:24]==[0,expected['final_output_count_low'],expected['final_tail_word']>>8,
                expected['final_tail_word']&255,0x27,0x58]
            assert r[SP]==0x6000 and r[I]==initial[I] and r[IFF]==initial[IFF] and r[IM]==initial[IM]
            # Проверка каждой фактической записи, а не только итоговых различий RAM.
            assert all(dest<=a<dest+size or base+1<=a<base+packed or 0x5FF6<=a<0x6000 for a,_ in m.writes)
            assert all(a==b or 0x5FF6<=address<0x6000 for address,(a,b) in enumerate(zip(m,wanted_memory)))
            for key,value in native.items():assert value==expected['counts'].get(key,0)
            counts['relocated_inputs']+=base!=source
            counts['output_bytes']+=size
            if source==0xC000:packets.update(expected['counts'])
            profiles.append(dict(slot=record['slot'],index=record['index'],source=source,dest=dest,
                relocated_base=base,instructions=steps,write_count=len(m.writes),
                refresh=refresh.finish(r[15])))
    # Сопоставление полных сумм с ранее выполненной станционной моделью тех же ресурсов.
    station_report=json.loads((ROOT/'Tools/Disasm/Reports/UnpackResourceVerification.json').read_text('utf-8'))
    assert station_report['passed'] and station_report['full_m1_count_from_original_opcode_prefixes']
    assert len(station_report['profiles'])==len(profiles)==80
    for own,other in zip(profiles,station_report['profiles']):
        assert all(own[key]==other[key] for key in ('slot','index','source','dest','refresh'))
    report=dict(passed=True,total_cases=len(profiles),resources=len(records),instruction_pairs=184,
        address_delta=delta,all_instruction_operands_verified=True,cases_by_path=dict(counts),
        independent_packet_counts=dict(packets),profiles=profiles,
        independent_numeric_decoder=True,
        all_general_registers_and_R_checked=True,full_m1_count_from_original_opcode_prefixes=True,
        each_R_increment_and_bit7_checked=True,fast_ldir=False,
        R_initial_values=sorted({p['refresh']['initial_R'] for p in profiles}),
        R_full_cartesian_input_product=False,independent_full_algorithm_timing_oracle=False,
        station_copy_paired_refresh_profiles=len(profiles),
        full_logical_RAM_except_stack_residue=True,tail_frame_and_return_verified=True,
        every_write_address_range_verified=True,write_multiplicity_independently_proved=False,
        physical_banks_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionUnpackVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='profiles'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
