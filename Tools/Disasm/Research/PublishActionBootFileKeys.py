"""Разметка шести фактически используемых ключей, без изменения загрузчика и дисковых вызовов."""
from collections import Counter
import contextlib
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from CheckIntro import ROOT
from ActionBootFileKeys import PATH, KEYS, render, parse
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_text('utf-8'))
    source_map,symbols,inventory=(read(name) for name in ('SourceMap','Symbols','Inventory'))
    old=next(row for row in source_map if row['slot']==17 and row['offset']==0x113)
    assert old['kind']=='unclassified' and old['length']==54
    original=ROOT/old['path']
    raw=original.read_bytes()
    assert raw==(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()[0x113:0x149]
    text,labels=render(raw)
    assert parse(text)==raw
    pending={ROOT/PATH:text.encode('utf-8')}
    source_map[source_map.index(old)]=dict(old,path=PATH,kind='typed_data',origin=0x42D0)
    for name,value in labels.items():
        assert name not in symbols
        symbols[name]=value
    path=ROOT/'Source/Files/17_ACTION.inc'
    text=path.read_text('utf-8')
    needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/17_ACTION/Unclassified000.bin"'
    assert text.count(needle)==1
    pending[path]=text.replace(needle,'                disp #42D0\n                include "../ActionBoot/Data/FileKeys.asm"\n                ent').encode('utf-8')
    path=ROOT/'Source/ActionBoot/InitializeFlight.asm'
    text=path.read_text('utf-8')
    for index,(name,_) in enumerate(KEYS):
        old_operand=f'LD HL, #{0x42D0+9*index:04X}'
        assert text.count(old_operand)==1
        text=text.replace(old_operand,'LD HL, @ActionBootFileKeys.'+name)
    text=text.replace('                module InitializeFlight','                module InitializeFlight\n                ; Имена ресурсов [физические ключи](../../Docs/ActionBootFileKeys.md)',1)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py'
    text=path.read_text('utf-8')
    text=text.replace('def name_operands(region, function_address, operation):',
        'def name_operands(region, function_address, operation):\n    operation = action_boot_file_key_name_operands(region, function_address, operation)',1)
    text+='\nfrom ActionBootFileKeys import name_operands as action_boot_file_key_name_operands\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py'
    text=path.read_text('utf-8')
    marker='    # Проверка исходного bitmap вступления, физических строк атрибутов и всего прочитанного упакованного потока.'
    assert text.count(marker)==1
    hook='''    # Проверка всех шести ключей ресурсов перенесённого загрузчика полёта.
    from ActionBootFileKeys import PATH as action_boot_file_keys_path, parse as parse_action_boot_keys, render as render_action_boot_keys
    action_boot_keys_raw=sources[17][0x113:0x149]
    assert parse_action_boot_keys((ROOT/action_boot_file_keys_path).read_text('utf-8'))==action_boot_keys_raw
    _, action_boot_keys_labels=render_action_boot_keys(action_boot_keys_raw)
    assert all(symbols[key.upper()]==value for key,value in action_boot_keys_labels.items())

'''
    pending[path]=text.replace(marker,hook+marker).encode('utf-8')
    inventory['ranges_by_kind']=dict(Counter(row['kind'] for row in source_map))
    totals=Counter()
    for row in source_map:totals[row['kind']]+=row['length']
    inventory['physical_bytes_by_kind']=dict(totals)
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[reports/(name+'.json')]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionBootFileKeys'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionBootFileKeys'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() if path.exists() else None for path in (*pending,original)}
    for path,data in pending.items():
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Проверка совпадения текущей рабочей копии с сохранённым основанием кандидата.
    for path,data in before.items():
        assert path.read_bytes()==data if data is not None else not path.exists()
        if data is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in pending.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='action-keys-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(data)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert original.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
    assert original.read_bytes()==(history/original.relative_to(ROOT)).read_bytes()
    original.unlink()
    print('Шесть ключей загрузчика, 54 исходных байта и все шесть потребителей сверены')


if __name__=='__main__':main()
