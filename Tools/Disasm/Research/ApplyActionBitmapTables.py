"""Точный договор и смысловые метки уже именованного построителя, без изменения инструкций."""
from pathlib import Path
import contextlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'),str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from ValidateNotes import validate_notes
from SourcePresentation import format_function
import ActionBitmapTablesFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    assert read('ControlsBufferPointsVerification')['passed']
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionBitmapTables'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionBitmapTables'
    assert not candidate.exists() and not history.exists()
    pending = {}
    symbols = read('Symbols')
    for old,new in facts.RENAMES.items():
        assert old in symbols and new not in symbols
        symbols[new] = symbols.pop(old)
    pending[ROOT / 'Tools/Disasm/Reports/Symbols.json'] = (json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    boot = next(r for r in read('ControlFlow') if r['name'] == 'ActionBoot')
    validate_notes([boot],{'ActionBoot':facts.COMMENTS})
    lines = ['                module ActionBoot','                module BuildBitmapTables',
        '                ; Документация [таблицы и XOR-точки](../../Docs/ControlsBufferPoints.md)',
        '                ; -----------------------------------------',
        '                ; Создание четырёх страниц адресации линейного пиксельного буфера',
        '                ; исходная запись 17, смещения #0212..#023C, рабочий адрес #43CF']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['ActionBoot',0x43CF]):
        lines += ['                ; '+heading+':'] + ['                ;   '+value for value in values]
    lines += ['                ; -----------------------------------------']
    for item in boot['instructions']:
        a = item['address']
        if not 0x43CF <= a < 0x43FA:
            continue
        before,right = facts.COMMENTS.get(a,([],None))
        lines += ['                ; '+value for value in before]
        operation = item['operation'].replace(',',', ')
        if operation.startswith(('JR ','JP ','CALL ','DJNZ ')):
            operation = re.sub(r'#([0-9A-F]{4})',lambda m:'@ActionBoot.BuildBitmapTables.'+facts.LABELS['ActionBoot',int(m[1],16)]
                if ('ActionBoot',int(m[1],16)) in facts.LABELS else m[0],operation)
        operation = facts.name_operands('ActionBoot',0x43CF,operation)
        label = 'Entry' if a == 0x43CF else facts.LABELS.get(('ActionBoot',a),'')
        line = ((label+':').ljust(16) if label else ' '*16)+operation
        lines.append(line.ljust(80)+'; '+right if right else line)
    lines += ['                endmodule','                endmodule']
    pending[ROOT / 'Source/ActionBoot/BuildBitmapTables.asm'] = format_function('\n'.join(lines)+'\n').encode('utf-8')
    path = ROOT / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    assert 'module BufferBitmapTables' not in text
    block = '\n                ; Существующие страницы общей RAM, содержимое строится при загрузке Action\n                module BufferBitmapTables\n'
    for name,address in (('RowHigh',0x9400),('RowLow',0x9500),('ColumnByte',0x9600),('ColumnMask',0x9700)):
        block += name.ljust(16) + ('equ #'+format(address,'04X')).ljust(64) + '; 256 исходных байтов соответствующей страницы\n'
    block += '                endmodule\n'
    pending[path] = text.replace('                endif',block+'\n                endif').encode('utf-8')
    for filename,extra in (
        ('Contracts.py','\nfrom ActionBitmapTablesFacts import CONTRACTS as ACTION_BITMAP_TABLE_CONTRACTS\nCONTRACTS.update(ACTION_BITMAP_TABLE_CONTRACTS)\n'),
        ('SemanticNames.py','\nfrom ActionBitmapTablesFacts import LABELS as ACTION_BITMAP_LABELS, name_operands as action_bitmap_name_operands\nLABELS.update(ACTION_BITMAP_LABELS)\nDOCUMENTS[("ActionBoot",0x43CF)] = ("ControlsBufferPoints","таблицы и XOR-точки")\n'),
        ('ExportSources.py','\nfrom ActionBitmapTablesFacts import COMMENTS as ACTION_BITMAP_COMMENTS\nREGION_COMMENTS.setdefault("ActionBoot",{}).update(ACTION_BITMAP_COMMENTS)\n')):
        path = ROOT / 'Tools/Disasm/Research' / filename
        text = path.read_text('utf-8')
        assert 'from ActionBitmapTablesFacts import' not in text
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle,needle+'\n    operation = action_bitmap_name_operands(region, function_address, operation)')
        if filename == 'ExportSources.py':
            needle = '\n\nif __name__ == "__main__":'
            assert text.count(needle) == 1
            text = text.replace(needle,'\n'+extra+needle)
        else:
            text += extra
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Docs/FunctionDetails/ActionBoot.md'
    text = path.read_text('utf-8')
    start = text.index('## BuildBitmapTables\n')
    end = text.find('\n## ',start+4)
    end = len(text) if end < 0 else end
    text = text[:end].rstrip()+'\n\n[Точный договор и проверка четырёх страниц](../ControlsBufferPoints.md).\n'+text[end:]
    pending[path] = text.encode('utf-8')
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(before)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    report = dict(passed=True,refined_named_contracts=1,renamed_internal_labels=3,
        original_table_bytes_checked=1024,exact_af='2062',exact_alternate_af='8083',
        instructions_changed=0,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionBitmapTablesClassification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
