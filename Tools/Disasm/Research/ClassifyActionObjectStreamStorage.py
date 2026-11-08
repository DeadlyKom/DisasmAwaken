"""Сохранение исходного содержимого доказанного назначения копирования как отдельного ресурса."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from ActionObjectStreamStorageResources import RESOURCES


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionObjectStreamStorageVerification')
    assert proof['passed'] and proof['read_of_initial_byte_before_first_write'] is False and proof['maximum_original_copy_bytes']==238
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    sm,inventory,modified=[read(n) for n in ('SourceMap','Inventory','ModifiedCode')]
    start,end,path,kind,note=RESOURCES[0]
    old=next(p for p in sm if p['slot']==17 and p['offset']<=start<end<=p['offset']+p['length'])
    assert old['kind']=='unclassified';old_path=ROOT/old['path'];old_end=old['offset']+old['length']
    assert old_path.read_bytes()==source[old['offset']:old_end]
    pending={};pieces=[]
    for begin,finish,new_path,new_kind in (
        (old['offset'],start,f'Source/Resources/17_ACTION/Unclassified{old["offset"]:04X}_{start:04X}.bin','unclassified'),
        (start,end,path,'binary_resource'),
        (end,old_end,f'Source/Resources/17_ACTION/Unclassified{end:04X}_{old_end:04X}.bin','unclassified')):
        assert finish>begin and not (ROOT/new_path).exists()
        pending[ROOT/new_path]=source[begin:finish]
        piece=dict(slot=17,offset=begin,length=finish-begin,kind=new_kind,path=new_path,
            origin=begin+0x6000 if new_kind=='binary_resource' else None,sha256=hashlib.sha256(source[begin:finish]).hexdigest())
        if new_kind=='binary_resource':piece['format']=kind
        pieces.append(piece)
    assert b''.join(pending[ROOT/p['path']] for p in pieces)==old_path.read_bytes()
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm))
    inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            assert item['target_slot']==17
            owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
            item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
    for stem,value in (('SourceMap',sm),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    include_path=ROOT/'Source/Files/17_ACTION.inc';text=include_path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for piece in pieces:
        lines+=['                assert $ == #'+format(piece['offset'],'04X')]
        if piece['kind']=='binary_resource':
            lines+=['                ; Документация [исходное содержимое буфера объекта](../../Docs/ActionObjectStreamStorage.md)',
                    '                ; '+note]
        else:lines+=['                ; Unknown, соседние байты вне доказанного назначения CopyObjectData']
        lines+=['                incbin "../'+piece['path'][7:]+'"']
    pending[include_path]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    # Сохранение каждого исходного байта ровно один раз, без подстановки целых программ из оригинала.';assert text.count(needle)==1
    hook='''    # Исходные байты подтверждённого назначения копирования, модели OBJECT3D в TRD не подставляются.
    from ActionObjectStreamStorageResources import RESOURCES as OBJECT_STREAM_STORAGE
    for start,end,path,kind,_ in OBJECT_STREAM_STORAGE:
        binary_resources[17,start]=(end,path,kind)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    for relative in ('Docs/ActionObjectCopy.md','Docs/ActionObjectVertices.md'):
        path=ROOT/relative
        extra='\n[Исходное содержимое назначения CopyObjectData](ActionObjectStreamStorage.md) сохранено отдельным ресурсом. 238 байтов отражают максимальную копию исходных чётных указателей, а не общий предел произвольного потока.\n'
        pending[path]=(path.read_text('utf-8')+extra).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionObjectStreamStorage'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionObjectStreamStorage'
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
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='object-storage-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[old['offset']:old_end]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,classified_initial_storage_bytes=238,original_bytes_preserved=True,
        copied_model_bytes_not_serialized=True,unknown_neighbor_bytes_preserved=old['length']-238,
        arbitrary_stream_capacity_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectStreamStorageClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
