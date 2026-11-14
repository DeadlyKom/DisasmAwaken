"""Прямые писатели связи и условия вызова F24F, без доказательства всех косвенных записей.

Документация: ../../../Docs/ActionSpawnContinue.md#происхождение-связи-и-проверки-родителей
"""
from hashlib import sha256
import json
import re
from CheckIntro import ROOT


def main():
    sources = {}
    writers = []
    callers = []
    for path in sorted((ROOT / 'Source/Action').glob('*.asm')):
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        selected = []
        for number, line in enumerate(lines, 1):
            code = line.split(';', 1)[0].strip()
            # Поиск только явно именованных прямых записей, LDIR и числовые адреса сюда не входят.
            if re.search(r'\bLD\s+\((?:IX|IY)\s*\+\s*@FActionRecord\.(LinkedIndex|LinkOverride)\),', code):
                field = 'LinkOverride' if '.LinkOverride)' in code else 'LinkedIndex'
                writers.append(dict(path=path.relative_to(ROOT).as_posix(), line=number, field=field, instruction=code))
                selected.append(number)
            if '@Action.CreateMissileAndContinueOffsets.Entry' in code:
                callers.append(dict(path=path.relative_to(ROOT).as_posix(), line=number, instruction=code))
                selected.append(number)
        if selected:
            sources[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    expected_callers = {'Source/Action/HandleLinkedTargetState.asm', 'Source/Action/HandleLinkedPhaseState.asm'}
    assert {item['path'] for item in callers} == expected_callers
    # Сверка фактических операций передачи произвольного байта подстановки.
    override = (ROOT / 'Source/Action/CopyRecordLinkOverride.asm').read_text(encoding='utf-8-sig')
    assert 'LD A, (IX + @FActionRecord.LinkOverride)' in override
    assert 'LD (IX + @FActionRecord.LinkedIndex), A' in override
    parent = (ROOT / 'Source/Action/HandleLinkedTargetState.asm').read_text(encoding='utf-8-sig')
    assert 'JP Z, @Action.CreateMissileAndContinueOffsets.Entry' in parent
    # Обычное преобразование индекса не имеет специального исключения FF.
    result = dict(method='static_named_direct_writer_and_caller_inventory',
        sources_sha256=sources, direct_writers=writers, direct_callers=callers,
        ordinary_target_addresses={f'{i:02X}': 0xA100 + 64 * i for i in (24, 26, 61, 62, 255)},
        context_FF_special_address=0xA780, creator_FF_ordinary_address=0xE0C0,
        override_non_FF_byte_copied_without_upper_bound=True,
        caller_guards={'State02': ['context Component0.High not 80', 'vector-context Carry clear', 'MissileRepeatDelay originally 1'],
                       'State05': ['context Component0.High not 80', 'MissileRepeatDelay originally 1']},
        State05_does_not_reload_vector_context_here=True,
        source_of_LinkOverride=['FF initializers', 'current Phase0OrLink in ApproachTargetRecordAndResolve'],
        all_reachable_indices_proved=False, index_61_or_62_native_reachability_proved=False,
        direct_named_writers_only=True, indirect_bulk_or_numeric_writes_exhausted=False,
        semantic_completion_proved=False, source_modified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnLinkDomainInspection.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(direct_writers=len(writers), direct_callers=len(callers), bounded_index_domain_proved=False)))


if __name__ == '__main__':
    main()
