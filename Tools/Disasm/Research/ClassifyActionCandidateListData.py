"""Типизация одиннадцати доказанных байтов списка без подмены соседней рабочей RAM."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionCandidateListData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    for stem in ('ActionCandidateEligibilityVerification','ActionNearestCandidateVerification','ActionClass19SpawnVerification'):
        assert read(stem)['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    sm,symbols,inventory,modified=[read(stem) for stem in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    start,end=facts.TABLE[2:4];assert source[start:end]==bytes([255])*10+bytes([254])
    old=next(p for p in sm if p['slot']==17 and p['offset']<=start<end<=p['offset']+p['length'])
    assert old['kind']=='unclassified';old_path=ROOT/old['path'];old_end=old['offset']+old['length']
    assert old_path.read_bytes()==source[old['offset']:old_end]
    pending={};pieces=[]
    text,labels=facts.render(source);assert facts.parse(text)==(source[start:end],labels)
    assert not set(labels)&set(symbols);symbols.update(labels)
    pending[ROOT/facts.TABLE[1]]=text.encode('utf-8')
    for begin,finish,path,kind in (
        (old['offset'],start,f'Source/Resources/17_ACTION/Unclassified{old["offset"]:04X}_{start:04X}.bin','unclassified'),
        (start,end,facts.TABLE[1],'typed_data'),
        (end,old_end,f'Source/Resources/17_ACTION/Unclassified{end:04X}_{old_end:04X}.bin','unclassified')):
        assert finish>begin and not (ROOT/path).exists()
        if kind=='unclassified':pending[ROOT/path]=source[begin:finish]
        pieces.append(dict(slot=17,offset=begin,length=finish-begin,kind=kind,path=path,
            origin=begin+0x6000 if kind=='typed_data' else None,sha256=hashlib.sha256(source[begin:finish]).hexdigest()))
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm))
    inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            assert item['target_slot']==17
            owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
            item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';include=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert include.count(needle)==1
    lines=[]
    for piece in pieces:
        lines+=['                assert $ == #'+format(piece['offset'],'04X')]
        if piece['kind']=='typed_data':
            lines+=['                disp #A01C','                include "../Action/Data/CandidateList.asm"','                ent']
        else:lines+=['                ; Unknown, соседние байты не классифицированы типизацией списка кандидатов',
                     '                incbin "../'+piece['path'][7:]+'"']
    pending[path]=include.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FCandidateCode' not in text
    pending[path]=text.replace('                endif',facts.structure()+'\n                endif').encode('utf-8')
    # Связывание трёх реальных потребителей с физической первой записью вместо одного адресного EQU.
    for relative in ('Source/Action/CheckCandidateListReady.asm','Source/Action/FindNearestListedRecord.asm',
                     'Source/Action/CreateCargoAndUpdateList.asm','Tools/Disasm/Research/ActionCandidateGateFacts.py',
                     'Tools/Disasm/Research/ActionNearestCandidateFacts.py','Tools/Disasm/Research/ActionClass19SpawnFacts.py'):
        path=ROOT/relative;text=path.read_text('utf-8');old_name='@ActionCandidateListState.BeforeFirst'
        assert old_name in text
        pending[path]=text.replace(old_name,'@ActionCandidateListData.Slot00.Code - 1').encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка физических STRUCT двух малых ресурсов связанных состояний.';assert text.count(needle)==1
    hook='''    # Проверка физических десяти исходных пропусков и завершающего кода списка.
    from ActionCandidateListData import TABLE as CANDIDATE_LIST_TABLE, parse as parse_candidate_list
    raw,labels=parse_candidate_list((ROOT/CANDIDATE_LIST_TABLE[1]).read_text('utf-8'))
    assert raw==sources[17][0x401C:0x4027]==bytes([255])*10+bytes([254])
    assert all(symbols.get(k.upper())==v for k,v in labels.items())
    assert symbols['FCANDIDATECODE']==1 and symbols['FCANDIDATECODE.CODE']==0
    rows=[p for p in source_map if p['path']==CANDIDATE_LIST_TABLE[1]]
    assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(0x401C,11,0xA01C)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические коды начального списка кандидатов, соседние байты остаются неизвестными.
    from ActionCandidateListData import TABLE as CANDIDATE_LIST_TABLE, render as render_candidate_list
    candidate_text,candidate_labels=render_candidate_list(data_by_slot[17])
    write(CANDIDATE_LIST_TABLE[1],candidate_text);symbols.update(candidate_labels)
    special[17,0x401C]=(0x4027,CANDIDATE_LIST_TABLE[1],0xA01C)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    for relative in ('Docs/ActionCandidateGate.md','Docs/ActionNearestCandidate.md','Docs/ActionClass19Spawn.md'):
        path=ROOT/relative
        pending[path]=(path.read_text('utf-8')+'\n[Исходный физический список](ActionCandidateList.md) содержит десять кодов FF и завершающий FE. Это начальная разметка, общий предел произвольного runtime-списка этим не устанавливается.\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionCandidateListData'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionCandidateListData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/old_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_path.read_bytes())
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='candidate-list-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    # Удаление только полностью заменённого бинарного диапазона после проверки его сохранённых байтов.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[old['offset']:old_end]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=11,physical_records=11,initial_skipped_slots=10,end_marker=254,
        original_bytes_preserved=True,consumer_instructions_preserved=True,new_physical_symbols=len(labels),
        arbitrary_runtime_list_capacity_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionCandidateListDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
