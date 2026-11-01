"""Согласование реестров подтверждённой подготовки A, без сборки."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    proof = read('MusicChannelARowVerification')
    assert proof['passed'] and read('MusicChannelARowClassification')['passed']
    flow = next(x for x in read('ControlFlow') if x['name'] == 'Music')
    instructions = {i['address']: i for i in flow['instructions']}
    modified = read('ModifiedCode')
    count = 0
    # Проверка исходных байтов каждой ранее невыделенной цели перед сменой её статуса.
    for item in modified:
        if item['region'] == 'Music' and item.get('target_source_classified') is False:
            owner = instructions[item['target_instruction']]
            assert item['target_original_hex'] == owner['hex']
            assert 0xDE74 <= owner['address'] < 0xDE90
            item['target_source_classified'] = True
            count += 1
    assert count in (0, 7)
    (ROOT / 'Tools/Disasm/Reports/ModifiedCode.json').write_text(
        json.dumps(modified, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    p = ROOT / 'Docs/ModifiedCode.md'
    lines = p.read_text('utf-8').splitlines()
    for n, line in enumerate(lines):
        if line.startswith('| Music |') and ('SetToneSlideA.asm' in line or 'SetTonePortamentoA.asm' in line):
            lines[n] = line.replace(' , целевой код ещё не выделен', '')
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    inventory, audit = read('Inventory'), read('ConformanceAudit')
    assert inventory['instructions'] == 39824 and audit['unknown_contract_fragments'] == 375
    checkpoint = read('InteractionCheckpoint')
    checkpoint.update(instruction_count=inventory['instructions'],
        unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified'],
        unproved_contracts=audit['unknown_contract_fragments'],
        named_without_contract=audit['named_fragments_without_proved_contract'])
    checkpoint['music_channel_a_row'] = dict(report='Tools/Disasm/Reports/MusicChannelARowVerification.json',
        row_cases=proof['row_cases'], direct_jump_cases=proof['direct_jump_cases'],
        newly_extracted_bytes=28, new_instructions=11, full_frame_contract=False,
        all_effect_operand_targets_now_classified=True, assembly_executed=False)
    for stem in ('MusicChannelARowVerification', 'MusicChannelARowClassification'):
        path = 'Tools/Disasm/Reports/' + stem + '.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    checkpoint['next_semantic_work'] = [x.replace('полные кадровые договоры TickDispatch и AdvancePatternA',
        'полный кадровый поток и договор AdvancePatternA') for x in checkpoint['next_semantic_work']]
    (ROOT / 'Tools/Disasm/Reports/InteractionCheckpoint.json').write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path in ('README.md', 'Docs/Validation.md', 'Docs/ConformancePlan.md'):
        p = ROOT / path
        text = p.read_text('utf-8')
        for old, new in (('376 недоказанных', '375 недоказанных'), ('376 без доказанного', '375 без доказанного'),
                         ('контракта: 376, включая 186', 'контракта: 375, включая 185'),
                         ('186 у уже именованных', '185 у уже именованных'), ('39813', '39824')):
            text = text.replace(old, new)
        link = 'Docs/MusicChannelStaging.md' if path == 'README.md' else 'MusicChannelStaging.md'
        paragraph = ('[Вход тика и подготовка строки A](' + link + ') проверены 8768 сочетаниями параметров '
            'и 256 прямыми переходами к синтезу. Установлены точные последствия LD BC вместо JP, EXX, '
            'двух режимов сброса скольжения и трёх изменяемых блоков. Выделены 11 инструкций, 28 исходных байтов. '
            'Полный поток кадра и аппаратные IRQ этой локальной проверкой не доказаны.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        p.write_text(text, encoding='utf-8')
    print(json.dumps(checkpoint['music_channel_a_row'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
