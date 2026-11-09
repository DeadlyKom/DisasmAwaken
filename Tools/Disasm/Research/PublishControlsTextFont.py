"""624 байта подтверждённого растра шрифта, предшествующий неизвестный диапазон не классифицируется."""
from collections import Counter
import contextlib,hashlib,io,json,sys
from CheckIntro import ROOT
from CheckControlsTextQueue import payload
import ControlsTextFont as font
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('ControlsTextFontVerification');assert proof['passed'] and proof['total_cases']==1024
    sm,inventory,symbols,modified=[read(n) for n in ('SourceMap','Inventory','Symbols','ModifiedCode')]
    old=next(r for r in sm if r['slot']==22 and r['offset']==0x546);assert old['length']==810 and old['kind']=='unclassified'
    old_path=ROOT/old['path'];raw=old_path.read_bytes();source=payload(22);data=source[font.START:font.END]
    assert raw==source[0x546:0x870] and font.pack(font.unpack(data))==data
    assert not any(r.get('target_path')==old['path'] for r in modified)
    pending={ROOT/font.PATH:data,ROOT/font.PREFIX_PATH:raw[:186]};assert all(not p.exists() for p in pending)
    pieces=[]
    for start,end,path,kind in ((0x546,0x600,font.PREFIX_PATH,'unclassified'),(0x600,0x870,font.PATH,'binary_resource')):
        row=dict(slot=22,offset=start,length=end-start,kind=kind,path=path,origin=None,sha256=hashlib.sha256(source[start:end]).hexdigest())
        if kind=='binary_resource':row['format']=font.FORMAT
        pieces.append(row)
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',sm),('Inventory',inventory)):pending[reports/(name+'.json')]=encode(value)
    symbols['ControlsTextFont.Pixels']=0xC600;pending[reports/'Symbols.json']=encode(symbols)
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    block='                ; Документация [пары знаков 4x6](../../Docs/ControlsTextFont.md)\n                module ControlsTextFont\n'
    block+='Pixels          equ #C600'.ljust(80)+'; исходный растр 104 пар, старшая и младшая тетрады содержат соседние знаки\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/22_CONTROL0.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/22_CONTROL0/'+old_path.name+'"';assert text.count(needle)==1
    replacement='                ; Unknown, 186 исходных байтов между точками буфера и растром шрифта\n                incbin "../Resources/22_CONTROL0/'+font.PREFIX_PATH.rsplit('/',1)[-1]+'"\n                assert $ == #0600\n                ; Документация [шрифт и чтения за его границей](../../Docs/ControlsTextFont.md)\n                incbin "../Controls/Resources/TextFont4x6.bin"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Source/Controls/PrintTextGlyph.asm';text=path.read_text('utf-8');assert text.count('LD BC, #C600')==1
    text=text.replace('LD BC, #C600','LD BC, @ControlsTextFont.Pixels')
    needle='                ;   исполнение физически продолжается в DrawGlyphRows, отдельного CALL нет';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n                ;   растр C600..C86F содержит коды 20..EF, остальные 48 кодов читают соседний код C870..C8FF\n                ;   [Физический шрифт и границы](../../Docs/ControlsTextFont.md)')
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ControlsTextDisplayFacts.py';text=path.read_text('utf-8');needle='def name_operands(region, function_address, operation):';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    if (region,function_address)==("Controls",0xEFC4):operation=operation.replace("LD BC, #C600","LD BC, @ControlsTextFont.Pixels")')
    text+='\nCONTRACTS["Controls",0xEFC4][3].append("растр C600..C86F содержит коды 20..EF, остальные 48 кодов читают соседний код C870..C8FF, см. ControlsTextFont.md")\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    binary_resources[7, 0x2900]';assert text.count(needle)==1
    text=text.replace(needle,'    # Растр пар знаков текстового окна CONTROL0, чтения за границей не исправляются.\n    from ControlsTextFont import START as TEXT_FONT_START,END as TEXT_FONT_END,PATH as TEXT_FONT_PATH,FORMAT as TEXT_FONT_FORMAT,PREFIX_PATH as TEXT_FONT_PREFIX_PATH\n    binary_resources[22,TEXT_FONT_START]=(TEXT_FONT_END,TEXT_FONT_PATH,TEXT_FONT_FORMAT)\n    symbols["ControlsTextFont.Pixels"]=0xC600\n'+needle)
    needle='                path = ROOT / binary_path';assert text.count(needle)==1
    text=text.replace(needle,'                if slot==22 and begin==0x546:binary_path=TEXT_FONT_PREFIX_PATH\n'+needle);pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка 4992 физических битов шестистрочных пар знаков CONTROL0.
    import ControlsTextFont as text_font
    text_font_raw=(ROOT/text_font.PATH).read_bytes()
    assert text_font_raw==sources[22][text_font.START:text_font.END]
    assert text_font.pack(text_font.unpack(text_font_raw))==text_font_raw
    assert symbols['CONTROLSTEXTFONT.PIXELS']==0xC600

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsTextFont';history=ROOT/'Tools/Disasm/Research/History/BeforeControlsTextFont';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before in {**{p:b for p,b,_ in plan if b is not None},old_path:raw}.items():
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve()) and old_path.read_bytes()==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,physical_bytes=624,glyphs=208,pixel_bits=4992,unknown_prefix_bytes_preserved=186,
        original_code_and_data_bytes_preserved=True,out_of_range_code_reads_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ControlsTextFontClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
