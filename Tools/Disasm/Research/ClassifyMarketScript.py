"""Точечное выделение исходного сценария, без сборки и без полного экспорта."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from MarketScriptTable import PATH,PREFIX,TAIL,START,render,parse
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/MarketScriptScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeMarketScriptClassification'


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert not CANDIDATE.exists() and not HISTORY.exists()
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==5);source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    source_map=read('SourceMap');old=next(item for item in source_map if item['path']=='Source/Resources/05_LANG/AfterAssignmentScratch.bin');assert (old['slot'],old['offset'],old['length'])==(5,0xA81,0x1000-0xA81)
    old_path=(ROOT/old['path']).resolve();assert old_path.is_relative_to(ROOT);old_bytes=old_path.read_bytes();assert old_bytes==source[0xA81:0x1000]
    text,new_symbols,end=render(source);active,parsed_symbols=parse(text);assert parsed_symbols==new_symbols and source[0xA81:START]+active+source[end:0x1000]==old_bytes
    pending={ROOT/PREFIX:source[0xA81:START],ROOT/PATH:text.encode('utf-8'),ROOT/TAIL:source[end:0x1000]}
    assert all(not p.exists() for p in pending)
    additions=[]
    for begin,stop,kind,path,origin in ((0xA81,START,'unclassified',PREFIX,None),(START,end,'typed_data',PATH,0xC000+START),(end,0x1000,'unclassified',TAIL,None)):
        additions.append(dict(slot=5,offset=begin,length=stop-begin,kind=kind,path=path,origin=origin,sha256=hashlib.sha256(source[begin:stop]).hexdigest()))
    index=source_map.index(old);source_map[index:index+1]=additions
    symbols=read('Symbols');assert not any(k in symbols for k in new_symbols);symbols.update(new_symbols)
    inventory=read('Inventory');inventory['ranges_by_kind']=dict(collections.Counter(i['kind'] for i in source_map));sizes=collections.Counter()
    for item in source_map:sizes[item['kind']]+=item['length']
    inventory['physical_bytes_by_kind']=dict(sizes)
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    p=ROOT/'Source/Files/05_LANG.inc';s=p.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённой рабочей записи\n                incbin "../Resources/05_LANG/AfterAssignmentScratch.bin"\n                assert $ == #1000';assert s.count(needle)==1
    replacement='\n'.join(['                ; Unknown, четырнадцать исходных байтов между рабочей записью и сценарием','                incbin "../Resources/05_LANG/BeforeMarketScript.bin"','                assert $ == #'+format(START,'04X'),'                disp #'+format(0xC000+START,'04X'),'                include "../Text/Data/MarketScript.asm"','                ent','                assert $ == #'+format(end,'04X'),'                ; исходный хвост после первого NUL, дополнительные потребители пока не установлены','                incbin "../Resources/05_LANG/AfterMarketScript.bin"','                assert $ == #1000'])
    pending[p]=s.replace(needle,replacement).encode('utf-8')
    p=ROOT/'Source/Text/RunMarketScript.asm';s=p.read_text('utf-8');assert s.count('LD IX, #CA8F')==1;s=s.replace('LD IX, #CA8F','LD IX, @MarketScript.Entry');anchor='; Подробный разбор [команды, стек, CR и условные блоки](../../Docs/ScriptControl.md)';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n                ; Исходный сценарий [товары, незаконная продажа и границы проверки](../../Docs/OriginalTradeScript.md)');pending[p]=s.encode('utf-8')
    plan=[]
    for path,data in pending.items():
        relative=path.relative_to(ROOT);before=path.read_bytes() if path.exists() else None;target=CANDIDATE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((path,relative,before,data))
    for path,relative,before,data in plan:assert (path.read_bytes()==before if before is not None else not path.exists());assert (CANDIDATE/relative).read_bytes()==data
    for path,relative,before,data in plan:
        if before is not None:target=HISTORY/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=HISTORY/old['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_bytes)
    for path,relative,before,data in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old_path.is_relative_to(ROOT) and old_path.read_bytes()==old_bytes and (HISTORY/old['path']).read_bytes()==old_bytes
    old_path.unlink()
    report=dict(passed=True,original_range_bytes=len(old_bytes),prefix_unknown_bytes=START-0xA81,script_bytes=len(active),tail_preserved_bytes=0x1000-end,
                script_labels=len(new_symbols),all_original_bytes_preserved=True,source_bytes_verified_without_assembly=True,
                ordinary_build_requires_python=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MarketScriptClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
