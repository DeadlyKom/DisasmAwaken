"""Именование одного исходного указателя только после публикации доказанного обработчика."""
import argparse,contextlib,importlib,io,json,re,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('address',type=lambda value:int(value,16))
    parser.add_argument('name');parser.add_argument('tag');parser.add_argument('--fallthrough');args=parser.parse_args()
    assert re.fullmatch('[A-Za-z][A-Za-z0-9]*',args.name) and re.fullmatch('[A-Za-z][A-Za-z0-9]*',args.tag)
    reports=ROOT/'Tools/Disasm/Reports'
    functions=json.loads((reports/'Functions.json').read_text('utf-8'))
    function=next(f for f in functions if f['region']=='Action' and f['address']==args.address)
    assert function['name']==args.name and function['semantic_status']=='described'
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    # Проверка исходного слова таблицы, новый указатель и новая память не создаются.
    matches=[i for i in range(22) if int.from_bytes(source[0x8F50+2*i:0x8F52+2*i],'little')==args.address]
    assert len(matches)==1
    path=ROOT/'Tools/Disasm/Research/ActionObjectStateHandlersData.py';text=path.read_text('utf-8')
    qualified='Action.'+args.name+'.Entry';marker='KNOWN_HANDLERS = {'
    assert qualified not in text and text.count(marker)==1
    pending={path:text.replace(marker,marker+f'0x{args.address:04X}: {qualified!r},\n                  ').encode('utf-8')}
    path=ROOT/'Source/Action/Data/ObjectStateHandlers.asm';text=path.read_text('utf-8');literal='#'+format(args.address,'04X')
    assert text.count(literal)==1
    lines=[]
    for line in text.splitlines():
        code,separator,note=line.partition(';')
        if code.strip()==literal:
            assert separator;line=code.replace(literal,'@'+qualified).rstrip().ljust(80)+';'+note
        lines.append(line)
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    if args.fallthrough:
        assert re.fullmatch('[A-Za-z][A-Za-z0-9]*',args.fallthrough)
        target=next(f for f in functions if f['region']=='Action' and f['name']==args.fallthrough)
        assert function['end_offset']==target['offset'] and function['slot']==target['slot']
        path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
        for number,name in enumerate((args.name,args.fallthrough)):
            needle='                include "../Action/'+name+'.asm"';assert text.count(needle)==1
            text=text.replace(needle,needle.ljust(80)+'; ('+str(number)+') жёсткий порядок, последовательное исполнение после CALL')
        pending[path]=text.encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+args.tag+'Binding')
    history=ROOT/('Tools/Disasm/Research/History/Before'+args.tag+'Binding')
    assert not candidate.exists() and not history.exists()
    plan=[(path,path.read_bytes(),after) for path,after in pending.items()]
    # Подготовка отдельного кандидата и проверка основания каждого файла перед публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        import ActionObjectStateHandlersData
        importlib.reload(ActionObjectStateHandlersData)
        import VerifySources
        importlib.reload(VerifySources).main()
    result=dict(passed=True,state_index=matches[0],address=args.address,name=args.name,
        physical_pointer_preserved=True,assembly_executed=False,native_execution=False)
    (reports/(args.tag+'BindingClassification.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
