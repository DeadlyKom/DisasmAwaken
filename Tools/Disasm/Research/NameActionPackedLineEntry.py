"""Дополнительный вход DDFC использует готовые упакованные концы и пропускает проверку равенства."""
import contextlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionPairedAimLinesVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['paths']['packed_equal_runs_256']==512
    pending={};block=['-----------------------------------------','Дополнительный вход DrawPacked',
        'In, HL и DE содержат упакованные концы, Second в младшем байте, First в старшем, BC и AF числовых аргументов не задают.',
        'In, режим и маски согласованы как у основного входа, весь путь пиксельных записей доступен и не пересекается с исполняемым кодом или внешним CPU-стеком.',
        'Out, для разных концов действует основной договор, исходные FirstPoint и SecondPoint не читаются.',
        'Out, при равных концах проверка равенства пропущена, нулевой B даёт 256 итераций по убыванию Second вместо пустого вывода.',
        'Corrupt, регистры, пиксели, временный SP и операнды из основного договора, R растеризатора независимо не доказан.',
        'Note, 77824 сценария прямого вызывающего включили 512 реальных равных отрезков с First=95, общий профиль равных точек у верхней границы буфера не доказан.',
        '-----------------------------------------','Сохранение CPU-стека и установка исходного SP=32 для шага линейной строки.']
    path=ROOT/'Source/Action/DrawLinearLine.asm';text=path.read_text('utf-8');needle='                LD (@ActionLineRasterState.SavedSP), SP';assert text.count(needle)==1
    pending[path]=text.replace(needle,'\n'.join('                ; '+line for line in block)+'\nDrawPacked:     LD (@ActionLineRasterState.SavedSP), SP').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionLineRasterFacts.py';text=path.read_text('utf-8');assert text.count('LOCAL={0xDE0A:')==1
    text=text.replace('LOCAL={0xDE0A:',"LOCAL={0xDDFC:'DrawPacked',0xDE0A:")
    text+='\n# Дополнительный прямой вход без повторного чтения рабочих точек.\nCOMMENTS[0xDDFC]=('+repr(block)+',None)\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');pending[path]=(text+"\nLABELS['Action',0xDDFC]='DrawPacked'\n").encode('utf-8')
    path=ROOT/'Tools/Disasm/Reports/Symbols.json';symbols=json.loads(path.read_text('utf-8'));key='Action.DrawLinearLine.DrawPacked';assert key not in symbols;symbols[key]=0xDDFC
    pending[path]=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path=ROOT/'Docs/ActionLineRaster.md';text=path.read_text('utf-8')
    text+='''
## Дополнительный вход DrawPacked по DDFC

HL и DE уже содержат упакованные концы, младший байт Second, старший First. Рабочие FirstPoint и SecondPoint не читаются, основная проверка равенства пропущена. Для разных концов сохраняется основной алгоритм. При равных концах B становится нулём, DJNZ выполняет 256 итераций влево. Такой путь записывает пиксели, в отличие от основного входа DDF0. Полная область этих записей должна быть доступна вызывающему и не повреждать код или внешний стек.

Этот вход используется [RequestPairedAimLines](../Source/Action/RequestPairedAimLines.asm). [Проверка вызывающего](../Tools/Disasm/Research/CheckActionPairedAimLines.py) выполнила 77824 сценария, в том числе 512 равных концов на строке 95. Сверены все регистры кроме R растеризатора, восемь банков и кратность записей. Для равных точек у верхней границы буфера полный расширенный профиль не доказан. [Результат](../Tools/Disasm/Reports/ActionPairedAimLinesVerification.json).
'''
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPackedLineEntry';history=ROOT/'Tools/Disasm/Research/History/BeforeActionPackedLineEntry'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes(),a) for p,a in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='packed-line-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,entry=0xDDFC,instruction_bytes_unchanged=True,caller_cases=77824,equal_endpoint_256_iterations_cases=512,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPackedLineEntryVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
