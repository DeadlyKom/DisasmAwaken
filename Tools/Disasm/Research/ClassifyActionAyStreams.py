"""Физические структуры пяти проверенных потоков, два неизученных промежутка сохраняются."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionAyStreams as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionAyStreamPlaybackVerification');assert proof['passed'] and proof['physical_stream_bytes']==309
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x8D8F)
    assert (old['length'],old['kind'])==(742,'unclassified');old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x8D8F:0x9075]
    pending={};ranges=[];pieces=[]
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    for path,streams in facts.GROUPS:
        text,labels=facts.render(source,streams);start,end=facts.bounds(streams)
        assert facts.parse(text,streams)==(source[start:end],labels);assert not set(labels)&set(symbols)
        pending[ROOT/path]=text.encode('utf-8');symbols.update(labels)
        ranges.append(piece(start,end,'typed_data',path,start+0x6000))
        pieces.append((start,end,path,True))
    for start,end,suffix in ((0x8DC1,0x8E4D,'BetweenAyStreams'),(0x8F50,0x9075,'AfterAyStreams')):
        path='Source/Resources/17_ACTION/Unclassified044_'+suffix+'.bin';pending[ROOT/path]=source[start:end]
        ranges.append(piece(start,end,'unclassified',path,None));pieces.append((start,end,path,False))
    ranges.sort(key=lambda i:i['offset']);index=source_map.index(old);source_map[index:index+1]=ranges
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FActionAyFrame' not in text
    pending[path]=text.replace('                endif',facts.structure_text()+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for start,end,path,typed in sorted(pieces):
        lines.append('                assert $ == #'+format(start,'04X'))
        if typed:lines+=['                disp #'+format(start+0x6000,'04X'),'                include "../Action/Data/'+path.rsplit('/',1)[-1]+'"','                ent']
        else:lines+=['                ; Unknown, соседние байты вне пяти доказанных потоков','                incbin "../Resources/17_ACTION/'+path.rsplit('/',1)[-1]+'"']
    pending[ROOT/'Source/Files/17_ACTION.inc']=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Пять потоков с доказанными границами, остальные соседние байты не классифицируются.
    if "struct FActionAyFrame" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionAyStreams import GROUPS as AY_STREAM_GROUPS, render as render_ay_streams, bounds as ay_stream_bounds
        for path,streams in AY_STREAM_GROUPS:
            text,bindings=render_ay_streams(data_by_slot[17],streams)
            write(path,text)
            symbols.update(bindings)
            start,end=ay_stream_bounds(streams)
            special[17,start]=(end,path,start+0x6000)
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.';assert text.count(needle)==1
    hook='''    # Проверка пяти исходных потоков, физических строк, терминаторов и каждого поля STRUCT.
    from ActionAyStreams import GROUPS as AY_STREAM_GROUPS, parse as parse_ay_streams, bounds as ay_stream_bounds
    ay_stream_records=0
    for path,streams in AY_STREAM_GROUPS:
        entries=[i for i in source_map if i['path']==path]
        if not entries:continue
        assert len(entries)==1
        start,end=ay_stream_bounds(streams);item=entries[0]
        raw,labels=parse_ay_streams((ROOT/path).read_text('utf-8'),streams)
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,start,end-start,start+0x6000)
        assert raw==sources[17][start:end]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FACTIONAYFRAME']==4
        for offset,field in enumerate(('ToneLow','ToneHigh','MixerBits','Volume')):
            assert symbols[('FActionAyFrame.'+field).upper()]==offset
        ay_stream_records+=sum(s[2] for s in streams)

'''
    text=text.replace(needle,hook+needle);needle="    report['type_delta_records'] = type_delta_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['action_ay_stream_records'] = ay_stream_records").encode('utf-8')
    for relative in ('Docs/DataFormats.md','Tools/Disasm/Research/GenerateDocs.py'):
        path=ROOT/relative;text=path.read_text('utf-8');needle='| FActionRecord | #40 |';index=text.index(needle);begin=text.rfind('\n',0,index)+1
        row='| FActionAyFrame | #04 | 76 физических строк пяти потоков и 5 терминаторов, см. [ActionAyStreams](ActionAyStreams.md) |'
        addition=('               "'+row+'",\n') if relative.endswith('.py') else row+'\n'
        pending[path]=(text[:begin]+addition+text[begin:]).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionAyStreams';history=ROOT/'Tools/Disasm/Research/History/BeforeActionAyStreams'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата, затем проверка отсутствия новых пользовательских изменений.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса после проверки байтов и сохранения истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==(history/old_path.relative_to(ROOT)).read_bytes()==source[0x8D8F:0x9075];old_path.unlink()
    report=dict(passed=True,physical_frames=76,terminators=5,physical_stream_bytes=309,unclassified_neighbor_bytes=433,
        sequences=30,ticks=486,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionAyStreamsClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
