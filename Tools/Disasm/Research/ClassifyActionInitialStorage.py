"""Разделение исходных байтов доказанных рабочих областей и сохранение неразобранного промежутка."""
from collections import Counter
import contextlib,hashlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from ActionInitialStorageResources import RESOURCES


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionInitialStorageVerification');assert proof['passed'] and proof['read_of_initial_byte_before_first_write'] is False
    assert read('ActionWorkBufferVerification')['filled_bytes']==3072
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();sm,inventory=[read(n) for n in ('SourceMap','Inventory')]
    old=next(p for p in sm if p['slot']==17 and p['offset']==0x21CC);assert (old['length'],old['kind'])==(5684,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x21CC:0x3800]
    pending={};pieces=[]
    for start,end,path,kind,note in RESOURCES:
        assert not (ROOT/path).exists();pending[ROOT/path]=source[start:end]
        pieces.append(dict(slot=17,offset=start,length=end-start,kind='binary_resource',path=path,origin=start+0x6000,format=kind,
            sha256=hashlib.sha256(source[start:end]).hexdigest()))
    gap_path='Source/Resources/17_ACTION/Unclassified2C00_3100.bin';assert not (ROOT/gap_path).exists()
    pending[ROOT/gap_path]=source[0x2C00:0x3100]
    pieces.append(dict(slot=17,offset=0x2C00,length=1280,kind='unclassified',path=gap_path,origin=None,
        sha256=hashlib.sha256(source[0x2C00:0x3100]).hexdigest()));pieces.sort(key=lambda p:p['offset'])
    assert b''.join(pending[ROOT/p['path']] for p in pieces)==old_path.read_bytes()
    at=sm.index(old);sm[at:at+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm));inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',sm),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    notes={p:note for _,_,p,_,note in RESOURCES};lines=[]
    for p in pieces:
        lines+=['                assert $ == #'+format(p['offset'],'04X')]
        note=notes.get(p['path'],'Unknown, промежуток 8C00..90FF не классифицирован этим разбором')
        lines+=['                ; '+note,'                incbin "../'+p['path'][7:]+'"']
    pending[path]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    # Сохранение каждого исходного байта ровно один раз, без подстановки целых программ из оригинала.';assert text.count(needle)==1
    hook='''    # Начальные байты рабочих областей, вычисленные значения таблиц в образ не подставляются.
    from ActionInitialStorageResources import RESOURCES as ACTION_INITIAL_STORAGE
    for start,end,path,kind,_ in ACTION_INITIAL_STORAGE:
        binary_resources[17,start]=(end,path,kind)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    for relative,extra in (('Docs/ActionWorkBuffer.md','\n[Исходные дисковые байты хвоста линейного буфера](ActionInitialStorage.md) отделены от его содержимого после ClearWorkBuffer. Они сохранены буквально, FF в готовый TRD вместо них не подставляется.\n'),
                           ('Docs/ActionFlightCycle.md','\n[Начальное содержимое рабочих областей](ActionInitialStorage.md) отделено от создаваемых таблиц и кадрового заполнения. Все 1792 табличных байта и 3072 байта буфера проверены на отсутствие чтения прежнего значения до первой записи в соответствующих процедурах. Это не доказательство порядка обращений произвольной другой фазы игры.\n')):
        path=ROOT/relative;pending[path]=(path.read_text('utf-8')+extra).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionInitialStorage';history=ROOT/'Tools/Disasm/Research/History/BeforeActionInitialStorage'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,a) for p,a in pending.items()]
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
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='initial-storage-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x21CC:0x3800]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,classified_initial_storage_bytes=4404,resource_files=8,framebuffer_tail_bytes=2612,generated_table_initial_bytes=1792,
        remaining_unclassified_gap_bytes=1280,original_bytes_preserved=True,generated_values_not_serialized=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionInitialStorageClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
