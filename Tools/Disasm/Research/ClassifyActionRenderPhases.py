"""Физические фазы и вложенная раскладка снимка, байты и адреса не меняются."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionRenderPhasesData as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ActionRenderCoefficientsClassification')['passed']
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map, symbols, inventory = [read(n) for n in ('SourceMap', 'Symbols', 'Inventory')]
    old = next(i for i in source_map if i['slot'] == 17 and i['offset'] == 0x3A00)
    assert (old['kind'], old['length']) == ('unclassified', 277)
    old_path = ROOT / old['path']
    before_raw = old_path.read_bytes()
    assert before_raw == source[0x3A00:0x3B15]
    prefix = 'Source/Resources/17_ACTION/Unclassified020_BeforeRenderPhases.bin'
    text, labels = facts.render(source)
    assert facts.parse(text) == (source[0x3B12:0x3B15], labels)
    assert not set(symbols) & set(labels)
    symbols.update(labels)
    pending = {ROOT / facts.PATH: text.encode('utf-8'), ROOT / prefix: source[0x3A00:0x3B12]}
    index = source_map.index(old)
    source_map[index:index + 1] = [dict(old, length=274, path=prefix, sha256=hashlib.sha256(source[0x3A00:0x3B12]).hexdigest()),
        dict(slot=17, offset=0x3B12, length=3, kind='typed_data', path=facts.PATH, origin=0x9B12,
             sha256=hashlib.sha256(source[0x3B12:0x3B15]).hexdigest())]
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind'] == kind) for kind in inventory['ranges_by_kind']}
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FRenderPhases' not in text
    needle = '                struct FActionRenderNode\n'
    assert text.count(needle) == 1
    text = text.replace(needle, facts.structure_text() + '\n' + needle)
    lines = text.splitlines()
    i = lines.index('                struct FActionRenderNode')
    j = lines.index('                ends', i)
    block = lines[i:j]
    assert sum(l.startswith('HeaderWord1') for l in block) == 1 and sum(l.startswith('HeaderByte') for l in block) == 1
    block = [l for l in block if not l.startswith(('HeaderWord1', 'HeaderByte'))]
    at = next(k for k, l in enumerate(block) if l.startswith('Components'))
    block.insert(at, 'Phases          FRenderPhases'.ljust(80) + '; Phase0, Phase1 и Phase2, снимок 9B12..9B14')
    lines[i:j] = block
    text = '\n'.join(lines) + '\n'
    text = text.replace('assert FActionRenderNode.HeaderWord1 == #05', 'assert FActionRenderNode.Phases == #05')
    text = text.replace('assert FActionRenderNode.HeaderByte == #07', 'assert FActionRenderNode.Phases.Phase2 == #07')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Source/Files/17_ACTION.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/17_ACTION/' + old_path.name + '"'
    assert text.count(needle) == 1
    replacement = '                incbin "../Resources/17_ACTION/' + prefix.rsplit('/', 1)[-1] + '"\n'
    replacement += '                assert $ == #3B12\n                disp #9B12\n                include "../Action/Data/RenderPhases.asm"\n                ent'
    pending[path] = text.replace(needle, replacement).encode('utf-8')
    # Именование только новых доказанных фаз в собственных исходниках, адреса исходных слов сохраняются.
    relatives = ('Source/Action/BuildRenderCoefficients.asm', 'Tools/Disasm/Research/ActionRenderCoefficientsFacts.py')
    for relative in relatives:
        path = ROOT / relative
        text = path.read_text('utf-8')
        for i in range(3):
            text = text.replace('ActionRenderCoefficientsState.Phase' + str(i), 'ActionRenderPhases.Value.Phase' + str(i))
        if relative.endswith('Facts.py'):
            text = text.replace("'(@ActionRenderCoefficientsState.Phase' + str(index)", "'(@ActionRenderPhases.Value.Phase' + str(index)")
        pending[path] = text.encode('utf-8')
    for relative in ('Source/Action/InsertRenderQueue.asm', 'Source/Action/ReadRenderQueue.asm',
        'Tools/Disasm/Research/ActionRenderQueueInsertFacts.py', 'Tools/Disasm/Research/ActionRenderQueueControlFacts.py',
        'Tools/Disasm/Research/ClassifyActionRenderQueueInsert.py', 'Docs/ActionRenderQueueInsert.md', 'Docs/ActionRenderQueueControl.md'):
        path = ROOT / relative
        text = path.read_text('utf-8').replace('HeaderWord1', 'PhasePair').replace('HeaderByte', 'Phase2')
        if relative.startswith('Source/'):
            lines = []
            for line in text.splitlines():
                code, sep, note = line.partition(';')
                if sep and code.strip() and '@ActionRenderQueueInsertState.' in code:
                    assert len(code.rstrip()) < 80
                    line = code.rstrip().ljust(80) + ';' + note
                lines.append(line)
            text = '\n'.join(lines) + '\n'
        pending[path] = text.encode('utf-8')
    path = ROOT / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    text = text.replace('HeaderWord1', 'PhasePair').replace('HeaderByte', 'Phase2')
    lines = []
    in_coefficients = False
    for line in text.splitlines():
        if 'module ActionRenderCoefficientsState' in line:
            in_coefficients = True
        elif in_coefficients and line.strip() == 'endmodule':
            in_coefficients = False
        if in_coefficients and line.startswith(('Phase0 ', 'Phase1 ', 'Phase2 ')):
            continue
        if line.startswith('PhasePair '):
            line = 'PhasePair       equ #9B12'.ljust(80) + '; слово Phase0/Phase1, low и high физической FRenderPhases'
        elif line.startswith('Phase2 ') and '#9B14' in line:
            line = 'Phase2          equ #9B14'.ljust(80) + '; третий байт физической FRenderPhases'
        lines.append(line)
    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text('utf-8')
    needle = '    # Проверка двух исходных байтов сопровождающей точки и физических полей X/Y.'
    assert text.count(needle) == 1
    hook = '''    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.
    from ActionRenderPhasesData import PATH as RENDER_PHASES_PATH, parse as parse_render_phases
    phase_records=[i for i in source_map if i['path']==RENDER_PHASES_PATH]
    assert len(phase_records)==1
    phase_item=phase_records[0]
    assert (phase_item['slot'],phase_item['offset'],phase_item['length'],phase_item['origin'])==(17,0x3B12,3,0x9B12)
    phase_raw,phase_labels=parse_render_phases((ROOT/RENDER_PHASES_PATH).read_text('utf-8'))
    assert phase_raw==sources[17][0x3B12:0x3B15]
    assert all(symbols.get(k.upper())==v for k,v in phase_labels.items())
    assert symbols['FRENDERPHASES']==3 and symbols['FACTIONRENDERNODE']==14
    for index in range(3):
        assert symbols['FRENDERPHASES.PHASE'+str(index)]==index
        assert symbols['FACTIONRENDERNODE.PHASES.PHASE'+str(index)]==5+index

'''
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = '''    # Три физические фазы построителя ACTION, те же поля вложены в runtime-снимок.
    if "struct FRenderPhases" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionRenderPhasesData import PATH as RENDER_PHASES_PATH, render as render_render_phases
        text,bindings=render_render_phases(data_by_slot[17])
        write(RENDER_PHASES_PATH,text)
        symbols.update(bindings)
        special[17,0x3B12]=(0x3B15,RENDER_PHASES_PATH,0x9B12)
'''
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    for relative in ('Docs/DataFormats.md', 'Tools/Disasm/Research/GenerateDocs.py'):
        path = ROOT / relative
        text = path.read_text('utf-8')
        row = '| FRenderPhases | #03 | Три физических фазы и вложенный снимок узла, см. [коэффициенты](ActionRenderCoefficients.md) |'
        line = next(l for l in text.splitlines(True) if '| FActionRenderNode |' in l)
        addition = '               "' + row + '",\n' if relative.endswith('.py') else row + '\n'
        assert '| FRenderPhases |' not in text
        pending[path] = text.replace(line, line + addition).encode('utf-8')
    # Подготовка кандидата и точной истории, только после проверки удаляется заменённый бинарный фрагмент.
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionRenderPhases'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionRenderPhases'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, old_path: before_raw}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes() == before_raw == (history / old['path']).read_bytes()
    old_path.unlink()
    report = dict(passed=True, physical_phase_bytes=3, physical_phase_records=1, initial_phases=list(source[0x3B12:0x3B15]),
        nested_node_offsets=[5, 6, 7], node_size_preserved=14, original_bytes_preserved=True,
        unclassified_prefix_bytes=274, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderPhasesClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
