"""Публикация подтверждённых разреженных физических STRUCT через отдельный кандидат."""
from collections import Counter,defaultdict
import argparse,contextlib,hashlib,importlib,io,json,os,re,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    parser=argparse.ArgumentParser();parser.add_argument('description',choices=('PolygonFillPhysicalData','ClipTargetLowPhysicalData','ActionQueueParameterPhysicalData','ActionPanelPhysicalData','ActionArchivedPlayerPanel','ActionLocalContextPhysicalData','ActionTransferredPlayerFields','ActionRenderHeaderPhysicalData','ActionOwnedCargoPhysicalData','ActionTractorCargoRules','ActionHyperReloadFileKey','ActionClippedLineWorkData','ControlsStationRelayFileKeys','ActionNewsOrdersAndJumpCost','FinalSyncAndPreviewRecord','InterfaceEventAndSpecialRecord','MapDistanceAndRenderState','ControlsResetVectorTemplates','StationBootResourceTables','StationInitialIndexPairs','EquipmentPhysicalTables','ControlsParameterTemplates','PreviewEdgeMaskPages','PreviewClipTablePages','EquipmentTypeSets','PreviewRootSamples','ActionContextControlPairs','StationTransportTradeTables','ActionPolygonScratch','StationOrderCompatibleSlots','StationNewsTransfer','StationPrimaryQuantityTail','IntroStackSnapshot','IntroStackSampleBytes','VoxelRotationTables','CargoLoadScale','PreviewObjectEnd','MapClipTablePages','BankArchiveRouteCopies','ActionPolygonExtraMaskPairs', 'FinalIrqStackData'));args=parser.parse_args()
    facts=importlib.import_module(args.description)
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    for stem in facts.REQUIRED_REPORTS:assert read(stem)['passed'],stem
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    sector_sources=getattr(facts,'USE_SECTORS',())
    sources={e['slot']:(ROOT/(e['path']+('.sectors.bin' if e['slot'] in sector_sources else '.bin'))).read_bytes()
             for e in manifest['entries']}
    proof=facts.validate_sources(sources);sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    pending={};grouped=defaultdict(list);old_rows={};physical_records=physical_symbols=typed_bytes=0
    for slot,origin,table in facts.TABLES:
        start,end=table[2:4];assert start<end and (ROOT/table[1]).resolve().is_relative_to(ROOT/'Source')
        old=next(r for r in sm if r['slot']==slot and r['offset']<=start<end<=r['offset']+r['length'])
        assert old['kind']=='unclassified';key=(slot,old['offset']);old_rows[key]=old
        grouped[key].append((slot,origin,table))
        text,labels=facts.render(sources[slot],origin,table);assert facts.parse(text,origin,table)==(sources[slot][start:end],labels)
        assert not set(labels)&set(symbols);symbols.update(labels)
        p=ROOT/table[1];assert not p.exists();pending[p]=text.encode('utf-8')
        physical_records+=len(table[-1]);physical_symbols+=len(labels);typed_bytes+=end-start
    removed=[];units={}
    for key,definitions in grouped.items():
        old=old_rows[key];slot=key[0];source=sources[slot];cursor=old['offset'];old_end=cursor+old['length'];old_path=ROOT/old['path']
        assert old_path.read_bytes()==source[cursor:old_end];pieces=[]
        def add_unknown(first,end):
            if first==end:return
            path=old['path'].rsplit('/',1)[0]+'/Unclassified'+format(first,'04X')+'_'+format(end,'04X')+'.bin'
            p=ROOT/path;assert not p.exists() and p not in pending;raw=source[first:end];pending[p]=raw
            pieces.append(dict(slot=slot,offset=first,length=end-first,kind='unclassified',path=path,origin=None,sha256=hashlib.sha256(raw).hexdigest()))
        for _,origin,table in sorted(definitions,key=lambda row:row[2][2]):
            start,end=table[2:4];assert cursor<=start;add_unknown(cursor,start)
            pieces.append(dict(slot=slot,offset=start,length=end-start,kind='typed_data',path=table[1],origin=origin+start,sha256=hashlib.sha256(source[start:end]).hexdigest()));cursor=end
        add_unknown(cursor,old_end)
        sm[sm.index(old):sm.index(old)+1]=pieces
        for item in modified:
            if item.get('target_path')==old['path']:
                assert item['target_slot']==slot;owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
                item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
        unit=next((ROOT/'Source/Files').glob(format(slot,'02d')+'_*.inc'));text=units.get(unit,unit.read_text('utf-8'))
        needle='                incbin "../'+old['path'][7:]+'"';assert text.count(needle)==1
        lines=['                ; Документация [таблицы и сохранённые промежутки](../../Docs/'+facts.DOCUMENT+'.md)']
        for p in pieces:
            lines+=['                assert $ == #'+format(p['offset'],'04X')]
            if p['kind']=='typed_data':lines+=['                disp #'+format(p['origin'],'04X'),'                include "../'+p['path'][7:]+'"','                ent']
            else:lines+=['                ; Unknown, соседние байты не объявляются свободными','                incbin "../'+p['path'][7:]+'"']
        units[unit]=text.replace(needle,'\n'.join(lines));removed.append((old_path,old_path.read_bytes()))
    pending.update({p:s.encode('utf-8') for p,s in units.items()})
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');declarations=facts.structures()
    for name in re.findall(r'\bstruct\s+(\w+)',declarations):assert not re.search(r'\bstruct\s+'+re.escape(name)+r'\b',text)
    assert text.count('                endif')==1
    if declarations:pending[p]=text.replace('                endif',declarations+'\n                endif').encode('utf-8')
    p=ROOT/'Includes/Variables/Include.inc';text=p.read_text('utf-8')
    for owner,name,address,target in facts.BINDINGS:
        current=None;lines=[];found=0
        for line in text.splitlines():
            code=line.partition(';')[0].strip();module=re.fullmatch(r'module\s+(\w+)',code,re.I)
            if module:current=module[1]
            elif code.lower()=='endmodule':current=None
            if current==owner and line.startswith(name.ljust(16)+'equ #'+format(address,'04X')):
                line+='\n                assert '+name+' == @'+target;found+=1
            lines.append(line)
        assert found==1,(owner,name,found);text='\n'.join(lines)+'\n'
    if facts.BINDINGS:pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка физических записей, их полей и исходного расположения.
    from MODULE_NAME import TABLES as POLYGON_PHYSICAL_TABLES, BINDINGS as POLYGON_PHYSICAL_BINDINGS, parse as parse_polygon_physical, validate_sources as validate_polygon_physical
    validate_polygon_physical(sources)
    for slot,origin,table in POLYGON_PHYSICAL_TABLES:
        raw,labels=parse_polygon_physical((ROOT/table[1]).read_text('utf-8'),origin,table)
        assert raw==sources[slot][table[2]:table[3]] and all(symbols.get(k.upper())==v for k,v in labels.items())
        offset=0
        for field,width,meaning in table[5]:
            assert symbols[(table[4]+'.'+field).upper()]==offset
            offset+=width
        assert symbols[table[4].upper()]==offset
        rows=[p for p in source_map if p['path']==table[1]]
        assert len(rows)==1 and (rows[0]['slot'],rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(slot,table[2],table[3]-table[2],origin+table[2])
    for owner,name,address,target in POLYGON_PHYSICAL_BINDINGS:assert symbols[(owner+'.'+name).upper()]==symbols[target.upper()]==address

'''.replace('MODULE_NAME',args.description)
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Сохранение физических записей и их исходного расположения.
    from MODULE_NAME import TABLES as POLYGON_PHYSICAL_TABLES, render as render_polygon_physical
    for slot,origin,table in POLYGON_PHYSICAL_TABLES:
        physical_text,physical_labels=render_polygon_physical(data_by_slot[slot],origin,table)
        write(table[1],physical_text);symbols.update(physical_labels)
        special[slot,table[2]]=(table[3],table[1],origin+table[2])

'''.replace('MODULE_NAME',args.description)
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+facts.TAG);history=ROOT/('Tools/Disasm/Research/History/Before'+facts.TAG)
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,data in removed:
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='physical-tables-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    for p,data in removed:
        assert p.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
        assert p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
    result=dict(passed=True,typed_bytes=typed_bytes,physical_records=physical_records,physical_symbols=physical_symbols,files=len(facts.TABLES),
        **proof,original_bytes_addresses_and_instructions_preserved=True,gaps_preserved=True,invalid_pair_gameplay_proved=False,
        cf08_reclassified=False,assembly_executed=False,native_execution=False)
    (ROOT/('Tools/Disasm/Reports/'+facts.TAG+'Classification.json')).write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
