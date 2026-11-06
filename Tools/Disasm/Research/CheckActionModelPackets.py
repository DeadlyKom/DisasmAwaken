"""Физическая разметка 95 потоков OBJECT3D и смысл восьмидесяти подтверждённых банковых целей."""
from collections import Counter,defaultdict
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==24)
    data=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.sectors.bin').read_bytes()
    assert len(data)==entry['allocated_length']==10752
    action=flat_action();aliases=defaultdict(list)
    # Проверка потребителей полей по фактическим инструкциям двух родительских обработчиков.
    for address in (0xDBC3,0xDC21,0xDD29,0xDD6F):assert bytes(action[address:address+2])==bytes((0xE6,0x0F))
    for address in (0xDBDC,0xDD38):assert bytes(action[address:address+6])==bytes((0x0F,0x0F,0x0F,0x0F,0xE6,0x07))
    for address in (0xDC24,0xDD72):assert bytes(action[address:address+2])==bytes((0xCB,0x76))
    for address in (0xDC31,0xDD7F):assert bytes(action[address:address+2])==bytes((0xE6,0x30))
    for index in range(0,256,2):
        offset=action[0x9E00+index]+256*action[0x9E01+index]-0xC000
        assert 0<=offset<entry['length'];aliases[offset].append(index)
    assert len(aliases)==95
    packets=[];fields={};counts=Counter();materials=Counter();line_modes=Counter()
    for start,indices in sorted(aliases.items()):
        # Разбор исходных физических групп и переменных записей до двух разных маркеров конца.
        cursor=start+2;fixed=[];records=[]
        while data[cursor]:
            fixed.append(dict(offset=cursor,mask=data[cursor],components=list(data[cursor+1:cursor+4])))
            for i in range(4):fields[cursor+i]='group_mask' if i==0 else 'group_component'
            cursor+=4
        fixed_end=cursor;cursor+=1
        while data[cursor]&15:
            header=data[cursor];number=header&15;kind='line' if header&128 else 'face'
            vertex_indices=list(data[cursor+1:cursor+1+number])
            assert all(index%5==0 for index in vertex_indices)
            row=dict(offset=cursor,header=header,kind=kind,count=number,indices=vertex_indices)
            fields[cursor]=kind+'_header'
            for i in range(number):fields[cursor+1+i]='vertex_index'
            counts[kind+'_'+str(number)]+=1
            if kind=='face':
                assert 3<=number<=15
                row['material']=(header>>4)&7;materials[row['material']]+=1
                assert row['material']<=4
            else:
                assert 2<=number<=15
                row.update(mode=(header>>4)&3,require_previous_front_face=bool(header&64))
                line_modes[row['mode']]+=1
            records.append(row);cursor+=1+number
        assert data[cursor]==0
        cursor+=1
        assert cursor<=entry['length']
        packets.append(dict(offset=start,end=cursor,length=cursor-start,pointer_indices=indices,
            header_unknown=data[start],scale_exponent=data[start+1],fixed_groups=fixed,
            fixed_end_offset=fixed_end,records=records,variable_end_offset=cursor-1))
    # Проверка отсутствия наложений и сохранения промежутков и хвостов как отдельных непонятых данных.
    gaps=[];cursor=0
    for packet in packets:
        assert cursor<=packet['offset']
        if cursor<packet['offset']:gaps.append(dict(offset=cursor,length=packet['offset']-cursor))
        cursor=packet['end']
    writes=json.loads((reports/'ActionBank4DataWrites.json').read_text('utf-8'));groups=defaultdict(list)
    assert len(writes)==80
    for write in writes:
        assert write['target_bank']==4 and write['target_slot']==24 and write['xor_mask']==0x60
        target=write['target_offset'];source=write['value_source']-0xC000
        assert fields[target]=='face_header' and fields[source]=='face_header'
        assert data[target]&15==data[source]&15
        before=data[source];after=before^0x60
        assert not after&0x80 and ((before>>4)&7) in (2,4) and ((after>>4)&7) in (2,4)
        groups[source].append(dict(target_offset=target,original_header=data[target],written_header=after))
    result=dict(passed=True,bank=4,slot=24,pointer_count=128,distinct_packets=len(packets),
        covered_packet_bytes=sum(p['length'] for p in packets),record_counts=dict(counts),
        face_material_counts=dict(materials),line_mode_counts=dict(line_modes),
        all_vertex_indices_multiple_of_five=True,known_bank4_targets_are_face_headers=True,
        known_writes_preserve_record_lengths=True,known_seed_materials_toggle_2_4=True,
        mutation_groups=[dict(source_offset=s,source_header=data[s],targets=v) for s,v in sorted(groups.items())],
        uninterpreted_gaps=gaps,unreferenced_logical_tail=dict(offset=cursor,length=entry['length']-cursor),
        sector_tail=dict(offset=entry['length'],length=len(data)-entry['length']),
        first_header_byte_meaning_proved=False,all_runtime_writers_proved=False,
        assembly_executed=False,native_execution=False,packets=packets)
    (reports/'ActionModelPacketsVerification.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({k:v for k,v in result.items() if k not in ('packets','mutation_groups')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
