"""Проверенное смысловое имя старшего разряда рыночной пары, без изменения данных."""
from pathlib import Path
import contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/MarketLegalityScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeMarketLegalityField'


def main():
    assert not CANDIDATE.exists() and not HISTORY.exists()
    proof=json.loads((ROOT/'Tools/Disasm/Reports/OriginalTradeScriptVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['actual_interpreter_and_original_script_executed'] and proof['illegal_market_fine_cases']>0
    with contextlib.redirect_stdout(io.StringIO()):verify()
    paths=[]
    for directory in ('Source','Includes','Docs'):
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in ('.asm','.inc','.md'))
    for directory in ('Tools/Disasm','Tools/Disasm/Research'):paths.extend((ROOT/directory).glob('*.py'))
    paths.append(ROOT/'Tools/Disasm/Reports/Symbols.json');plan=[]
    for path in paths:
        if path.resolve()==Path(__file__).resolve():continue
        before=path.read_bytes();text=before.decode('utf-8');changed=text.replace('StockAndMark','StockAndSaleBan')
        if path==ROOT/'Includes/Structs/Include.inc':
            changed=changed.replace('StockAndSaleBan    db','StockAndSaleBan db').replace('bit7 маркер неизвестного игрового назначения, bits6..0 количество','bit7 запрет продажи со штрафом, bits6..0 количество')
        if changed==text:continue
        lines=[]
        for old,line in zip(text.splitlines(),changed.splitlines()):
            if old!=line and path.suffix in ('.asm','.inc') and ';' in line and not line.lstrip().startswith(';'):
                code,comment=line.split(';',1);assert len(code.rstrip())<80,(path,code);line=code.rstrip().ljust(80)+';'+comment
            lines.append(line)
        data=('\n'.join(lines)+('\n' if changed.endswith('\n') else '')).encode('utf-8');relative=path.relative_to(ROOT)
        target=CANDIDATE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((path,relative,before,data))
    for path,relative,before,data in plan:assert path.read_bytes()==before and (CANDIDATE/relative).read_bytes()==data
    for path,relative,before,data in plan:
        target=HISTORY/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,relative,before,data in plan:path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    report=dict(passed=True,changed_files=len(plan),physical_field='FMarketRow.StockAndSaleBan',illegal_sale_proof='OriginalTradeScriptVerification.json',
                code_and_data_bytes_unchanged=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MarketLegalityFieldVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
