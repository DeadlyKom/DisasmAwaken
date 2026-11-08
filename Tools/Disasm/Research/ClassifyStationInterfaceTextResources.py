"""Выделение подтверждённых текстов интерфейса, общий ограничитель не дублируется."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from Analyze import payload
from VerifySources import main as verify_sources
from StationInterfaceTextResources import RESOURCES,path,verify
from StationPanelTextResources import escaped


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify_sources()
    source=payload(4);verify(source);sm=read('SourceMap');inventory=read('Inventory');modified=read('ModifiedCode')
    old=next(r for r in sm if r['slot']==4 and r['offset']==0x839A)
    assert old['kind']=='unclassified' and old['length']==3427
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x839A:0x90FD]
    pending={};pieces=[];layout=[];decoded=['Исходные подписи интерфейса станции 0. Управляющие коды показаны явно.','']
    for start,end,name,consumer,lf,cr in RESOURCES:
        raw=source[start:end];target=path(name);assert not (ROOT/target).exists();pending[ROOT/target]=raw
        assert (ROOT/('Source/Station/'+consumer+'.asm')).is_file()
        pieces.append(dict(slot=4,offset=start,length=end-start,kind='binary_resource',path=target,origin=start+0x6000,
            format='CP866_INTERFACE_TEXT',sha256=hashlib.sha256(raw).hexdigest()))
        layout.append(dict(name=name,path=target,address=start+0x6000,end_exclusive=end+0x6000,bytes=len(raw),
            lf_count=lf,cr_count=cr,consumer='Source/Station/'+consumer+'.asm',text_escaped=escaped(raw)))
        decoded += [name+' '+format(start+0x6000,'04X')+'..'+format(end+0x6000-1,'04X'),escaped(raw),'']
    unknown='Source/Resources/04_STATIONF/Unclassified9066_90B2.bin'
    assert not (ROOT/unknown).exists();raw=source[0x9066:0x90B2];pending[ROOT/unknown]=raw
    pieces.append(dict(slot=4,offset=0x9066,length=76,kind='unclassified',path=unknown,origin=None,sha256=hashlib.sha256(raw).hexdigest()))
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
    needle='                incbin "../Resources/04_STATIONF/'+old_path.name+'"';assert text.count(needle)==1
    lines=['                ; Документация [подписи и общие LF](../../Docs/StationInterfaceTextResources.md)']
    for r in pieces:
        lines+=['                assert $ == #'+format(r['offset'],'04X'),
                '                ; '+('Unknown, потребитель соседнего шаблона не установлен' if r['kind']=='unclassified' else 'исходные подписи CP866, общий LF соседних потоков не дублируется'),
                '                incbin "../'+r['path'][7:]+'"']
    pending[unit]=text.replace(needle,'\n'.join(lines)).replace(
        '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+lines[0],lines[0]).encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка подписей интерфейса и общих физических ограничителей LF.
    from StationInterfaceTextResources import RESOURCES as INTERFACE_TEXTS, path as interface_text_path, verify as verify_interface_texts
    verify_interface_texts(sources[4])
    for start,end,name,consumer,lf,cr in INTERFACE_TEXTS:
        assert (ROOT/interface_text_path(name)).read_bytes()==sources[4][start:end]
        rows=[p for p in source_map if p['path']==interface_text_path(name)]
        assert len(rows)==1 and rows[0]['kind']=='binary_resource'
        assert (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8')
    needle='    # Сохранение каждого исходного байта ровно один раз, без подстановки целых программ из оригинала.';assert text.count(needle)==1
    hook='''    # Подписи интерфейса станции, включая строки с общим LF следующего потока.
    from StationInterfaceTextResources import RESOURCES as INTERFACE_TEXTS, path as interface_text_path
    for start,end,name,consumer,lf,cr in INTERFACE_TEXTS:
        binary_resources[4,start]=(end,interface_text_path(name),'CP866_INTERFACE_TEXT')

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    result=dict(passed=True,classified_resource_bytes=3351,remaining_unknown_bytes=76,resources=layout,
        shared_delimiters_preserved=True,original_bytes_preserved=True,all_runtime_indices_valid=False,
        whole_game_verified=False,assembly_executed=False,native_execution=False)
    pending[ROOT/'Tools/Disasm/Reports/StationInterfaceTextLayout.json']=encode(result)
    pending[ROOT/'Tools/Disasm/Research/Evidence/StationInterfaceTexts.txt']=('\n'.join(decoded)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/StationInterfaceTextResources'
    history=ROOT/'Tools/Disasm/Research/History/BeforeStationInterfaceTextResources';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    q=history/old_path.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old_path.read_bytes())
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='interface-text-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/04_STATIONF').resolve())
    assert old_path.read_bytes()==source[0x839A:0x90FD]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    print(json.dumps({k:v for k,v in result.items() if k!='resources'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
