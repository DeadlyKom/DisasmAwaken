"""Одноразовая публикация текстов с установленными потребителями без сборки."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from Analyze import payload
from VerifySources import main as verify
from StationPanelTextResources import RESOURCES,path,records,escaped


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    for stem in ('QueuedMessagePanelVerification','EquipmentInfoVerification','DecodedMessageVerification'):
        assert read(stem)['passed']
    source=payload(4);sm=read('SourceMap');inventory=read('Inventory');modified=read('ModifiedCode')
    old=next(r for r in sm if r['slot']==4 and r['offset']==0x6E19)
    assert old['kind']=='unclassified' and old['length']==5397
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x6E19:0x832E]
    pending={};pieces=[];layout=[];decoded=['Тексты банка станции 0, физические байты STATIONF.','']
    for start,end,name,count,separator,consumer in RESOURCES:
        raw=source[start:end];rows=records(raw,separator);assert len(rows)==count
        assert (ROOT/('Source/Station/'+consumer+'.asm')).is_file()
        target=path(name);assert not (ROOT/target).exists();pending[ROOT/target]=raw
        pieces.append(dict(slot=4,offset=start,length=end-start,kind='binary_resource',path=target,
            origin=start+0x6000,format='CP866_PANEL_TEXT_'+separator,sha256=hashlib.sha256(raw).hexdigest()))
        row_layout=[dict(index=i,address=start+0x6000+offset,offset_in_resource=offset,
                         length=len(text),text_escaped=escaped(text)) for i,(offset,text) in enumerate(rows)]
        layout.append(dict(name=name,path=target,start_address=start+0x6000,end_exclusive=end+0x6000,
                           bytes=len(raw),separator=separator,records=row_layout,
                           consumer='Source/Station/'+consumer+'.asm'))
        decoded += [name+' '+format(start+0x6000,'04X')+'..'+format(end+0x6000-1,'04X')]
        decoded += [format(r['index'],'02d')+' '+format(r['address'],'04X')+' '+r['text_escaped'] for r in row_layout]
        decoded += ['']
    # Сохранение соседнего списка без предположения о его игровом потребителе.
    unknown='Source/Resources/04_STATIONF/Unclassified80E4_8262.bin'
    assert not (ROOT/unknown).exists();raw=source[0x80E4:0x8262];pending[ROOT/unknown]=raw
    pieces.append(dict(slot=4,offset=0x80E4,length=len(raw),kind='unclassified',path=unknown,
                       origin=None,sha256=hashlib.sha256(raw).hexdigest()))
    pieces.sort(key=lambda r:r['offset']);assert b''.join(pending[ROOT/r['path']] for r in pieces)==old_path.read_bytes()
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm))
    inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            assert item['target_slot']==4
            owner=next(r for r in pieces if r['offset']<=item['target_offset']<r['offset']+r['length'])
            item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
    for stem,value in (('SourceMap',sm),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    unit=ROOT/'Source/Files/04_STATIONF.inc';text=unit.read_text('utf-8')
    needle='                ; Unknown, остальные сообщения и данные ещё требуют отдельного разбора\n                incbin "../Resources/04_STATIONF/Unclassified085AfterWelcome.bin"'
    assert text.count(needle)==1
    lines=['                ; Документация [исходные потоки панелей](../../Docs/StationPanelTextResources.md)']
    for r in pieces:
        lines+=['                assert $ == #'+format(r['offset'],'04X'),
                '                ; '+('Unknown, потребитель списка абонентов не установлен' if r['kind']=='unclassified' else 'исходный поток CP866, переводы и управляющие коды не исправляются'),
                '                incbin "../'+r['path'][7:]+'"']
    pending[unit]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    verifier=ROOT/'Tools/Disasm/VerifySources.py';text=verifier.read_text('utf-8')
    needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка физических текстовых потоков станции без подстановки перевода в образ.
    from StationPanelTextResources import RESOURCES as PANEL_TEXTS, path as panel_path, records as panel_records
    for start,end,name,count,separator,consumer in PANEL_TEXTS:
        raw=(ROOT/panel_path(name)).read_bytes()
        assert raw==sources[4][start:end] and len(panel_records(raw,separator))==count
        rows=[p for p in source_map if p['path']==panel_path(name)]
        assert len(rows)==1 and rows[0]['kind']=='binary_resource'
        assert (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)

'''
    pending[verifier]=text.replace(needle,hook+needle).encode('utf-8')
    exporter=ROOT/'Tools/Disasm/Research/ExportSources.py';text=exporter.read_text('utf-8')
    needle='    # Сохранение каждого исходного байта ровно один раз, без подстановки целых программ из оригинала.'
    assert text.count(needle)==1
    hook='''    # Тексты панелей банка станции, исходные управляющие коды и написание сохраняются.
    from StationPanelTextResources import RESOURCES as PANEL_TEXTS, path as panel_text_path
    for start,end,name,count,separator,consumer in PANEL_TEXTS:
        binary_resources[4,start]=(end,panel_text_path(name),'CP866_PANEL_TEXT_'+separator)

'''
    pending[exporter]=text.replace(needle,hook+needle).encode('utf-8')
    result=dict(passed=True,classified_resource_bytes=5015,resources=layout,remaining_unknown_bytes=382,
        original_bytes_preserved=True,decoded_document_is_not_executed=True,
        all_equipment_records_gameplay_verified=False,contact_list_consumer_proved=False,
        assembly_executed=False,native_execution=False)
    pending[ROOT/'Tools/Disasm/Reports/StationPanelTextLayout.json']=encode(result)
    pending[ROOT/'Tools/Disasm/Research/Evidence/StationPanelTexts.txt']=('\n'.join(decoded)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/StationPanelTextResources'
    history=ROOT/'Tools/Disasm/Research/History/BeforeStationPanelTextResources'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for p,before,after in plan:
        target=candidate/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/old_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_path.read_bytes())
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='station-text-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/04_STATIONF').resolve())
    assert old_path.read_bytes()==source[0x6E19:0x832E]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    print(json.dumps({k:v for k,v in result.items() if k!='resources'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
