"""Авторские шаблоны блоков станции, все 192 байта и ограничитель 80FF.

Документация: ../../../Docs/ActionSpawnPhysicalRows.md#авторские-блоки-станции-и-слово-80ff
"""
from hashlib import sha256
import json
import re

from ArchivedSourceInventory import load_sources
from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from SpawnPhysicalRows import parse
from VerifySources import structure_symbols


def main():
    archive = ROOT/'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    archive_hash = sha256(archive.read_bytes()).hexdigest()
    assert archive_hash == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    sources,_,_ = load_sources()
    assert len(sources) == 129
    obj = next(s for s in sources if s['member'] == 'awk1.trd' and s['slot'] == 32)
    listing = next(s for s in sources if s['member'] == 'awk1.trd' and s['slot'] == 63)
    lines = obj['content'].split(b'\r')
    assert 'ДАННЫЕ О 3D БЛОКАХ СТАНЦИИ'.encode('cp866') in lines
    word_prefix = bytes.fromhex('068c05680683')
    byte_prefix = bytes.fromhex('068c05670683')
    # Значения берутся из авторского листинга, не подбираются по текущей модели.
    model_offsets = {}
    offset_records = []
    for number,line in enumerate(listing['content'].split(b'\r'),1):
        match = re.fullmatch(rb'(IST(?:[1-9]|1[0-6]))\x06[\x80-\xff]\x04f([0-9]+)',line)
        if match:
            name = match[1].decode('ascii')
            assert name not in model_offsets
            model_offsets[name] = int(match[2])
            offset_records.append(dict(line=number,name=name,value=int(match[2]),raw_hex=line.hex()))
    assert set(model_offsets) == {'IST'+str(i) for i in range(1,17)}
    assert all(model_offsets['IST'+str(i)] == ((0xC4+4*(i-1))&255) for i in range(1,17))
    table_line = lines.index(b'STATTB')
    pointer_names = []
    for line in lines[table_line+1:table_line+17]:
        assert line.startswith(word_prefix)
        name = line[len(word_prefix):].decode('ascii')
        assert re.fullmatch(r'ST(?:[1-9]|1[0-6])k',name)
        pointer_names.append(name)
    assert len(set(pointer_names)) == 16
    # Размещение нормализуется к уже существующей таблице текущей игры.
    base = 0x7799
    positions = {}
    payload = bytearray()
    declarations = []
    for number in range(1,17):
        label = 'ST'+str(number)+'k'
        position = lines.index(label.encode('ascii'))
        assert lines[position+1] == word_prefix+b'#0000,#0000,#0000'
        assert lines[position+2] == byte_prefix+('IST'+str(number)+',#00').encode('ascii')
        assert lines[position+3] == word_prefix+b'#80FF'
        positions[label] = base+32+len(payload)
        raw = bytes(6)+bytes((model_offsets['IST'+str(number)],0,0xFF,0x80))
        payload.extend(raw)
        declarations.append(dict(label=label,current_address=positions[label],authored_model='St'+str(number),
            model_offset=model_offsets['IST'+str(number)],line=position+1,
            source_records_hex=[x.hex() for x in lines[position:position+4]],bytes_hex=raw.hex()))
    serialized = b''.join(positions[name].to_bytes(2,'little') for name in pointer_names)+payload
    assert len(serialized) == 192
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(e for e in manifest['entries'] if e['slot'] == 17)
    original = (ROOT/(entry['path']+'.bin')).read_bytes()
    assert original == disk[entry['offset']:entry['offset']+entry['length']]
    memory = flat_action()
    assert bytes(memory[0x6000:0x7F8F]) == original[0x23D:0x21CC]
    assert bytes(memory[base:base+192]) == serialized
    assert original[0x23D+base-0x6000:0x23D+base-0x6000+192] == serialized
    typed,labels = parse((ROOT/'Source/Action/Data/SpawnTemplates.asm').read_text(encoding='utf-8'))
    assert typed == serialized
    models = json.loads((ROOT/'Tools/Disasm/Reports/ResourceSemanticLimits.json').read_bytes())['model_name_provenance']['named_models']
    models = {m['name']:m for m in models}
    rows = []
    for index,label in enumerate(pointer_names):
        number = int(label[2:-1])
        address = positions[label]
        assert labels['Template'+format(index,'02')] == address-base
        assert labels['End'+format(index,'02')] == address-base+8
        offset = model_offsets['IST'+str(number)]
        pointer = memory[0x9E00+offset] | memory[0x9E01+offset] << 8
        authored = models['St'+str(number)]
        model = next(m for m in models.values() if m['address'] == pointer)
        assert (ROOT/model['source_path']).exists()
        if number < 16:
            assert model['name'] == authored['name']
        else:
            # Байтовый IST16 оборачивается в начало 9E, слово St16 остаётся в следующей странице.
            assert offset == 0 and pointer == 0xC000 and model['name'] == 'KN01pol1'
            assert memory[0x9F00] | memory[0x9F01] << 8 == authored['address']
            assert memory[0x9F02] | memory[0x9F03] << 8 == authored['address']
        near_pointer = memory[0x9E00+offset+2] | memory[0x9E00+offset+3] << 8
        near_model = next(m for m in models.values() if m['address'] == near_pointer)
        rows.append(dict(index=index,archived_label=label,current_address=address,
            source_template='Template'+format(index,'02'),source_end='End'+format(index,'02'),
            authored_model_name=authored['name'],authored_model_bank4_address=authored['address'],
            current_selector_matches_authored_name=model['name'] == authored['name'],
            model_offset=offset,model_name=model['name'],model_bank4_address=pointer,model_source=model['source_path'],
            near_model_name=near_model['name'],near_model_bank4_address=near_pointer))
    fields = structure_symbols()
    assert (fields['FSPAWNTEMPLATEEND.UNKNOWN00'],fields['FSPAWNTEMPLATEEND.ENDCODE']) == (0,1)
    flow = next(x for x in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes()) if x['name'] == 'Action')
    reads = [x for x in flow['instructions'] if x['slot'] == 17 and 0x7859 <= x['address'] < 0x7AC6 and x['operation'] == 'LD A,(IX+#01)']
    assert len(reads) == 1
    read = reads[0]
    assert read['hex'] == 'dd7e01'
    assert bytes(memory[read['address']:read['address']+5]) == bytes.fromhex('dd7e01fe80')
    assert original[read['offset']:read['offset']+5] == bytes.fromhex('dd7e01fe80')
    assert bytes(memory[read['address']:read['address']+9]) == bytes.fromhex('dd7e01fe80c1d1e1c8')
    assert bytes(memory[0xAACC:0xAAD3]) == bytes.fromhex('6f269e7e2c666f')
    assert original[0x4ACC:0x4AD3] == bytes.fromhex('6f269e7e2c666f')
    result = dict(passed=True,method='authored_OBJGENER_station_templates_and_LABELS_offsets_normalized_to_current_layout',
        archive_sha256=archive_hash,original_disk_sha256=manifest['sha256'],
        source=dict(member=obj['member'],slot=obj['slot'],name=obj['name'],sha256=sha256(obj['content']).hexdigest()),
        offset_listing=dict(member=listing['member'],slot=listing['slot'],name=listing['name'],
            sha256=sha256(listing['content']).hexdigest(),records=offset_records),
        normalized_current_base=base,archived_absolute_addresses_proved=False,
        bytes_matched=192,serialized_sha256=sha256(serialized).hexdigest(),
        archived_word_terminators=16,terminator_word=0x80FF,rows=rows,declarations=declarations,
        current_model_names_match_count=sum(r['current_selector_matches_authored_name'] for r in rows),
        IST16_byte_alias_to_KN01pol1_preserved=True,
        current_EndCode_read=dict(address=read['address'],offset=read['offset'],hex='dd7e01fe80'),
        direct_terminator_predicate_reads_high_only=True,header_reader_byte_index_in_9e_proved=True,
        header_reader_prefix_hex='6f269e7e2c666f',
        standalone_low_FF_role_proved=False,all_indirect_consumers_excluded=False,
        execution_model_run=False,native_execution=False,assembly_executed=False)
    path = ROOT/'Tools/Disasm/Reports/ArchivedStationTemplatesVerification.json'
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if path.exists():assert all(json.loads(data)[k] == v for k,v in json.loads(path.read_bytes()).items())
    path.write_bytes(data)
    print(json.dumps(dict(passed=True,bytes=192,templates=16,word_terminators=16,matching_authored_models=15,IST16_current_model='KN01pol1'),ensure_ascii=False))


if __name__ == '__main__':
    main()
