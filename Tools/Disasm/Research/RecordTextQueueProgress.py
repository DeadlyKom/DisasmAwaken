"""Актуальные подтверждённые показатели после разбора очереди Controls."""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[3]


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    audit, inventory = read('ConformanceAudit'), read('Inventory')
    proof, publication = read('ControlsTextQueueVerification'), read('ControlsTextQueueClassification')
    assert proof['passed'] and publication['passed'] and read('SourceVerification')['passed']
    checkpoint = read('InteractionCheckpoint')
    checkpoint.update(fragments=inventory['fragments'], described=inventory['described'], unknown=inventory['unknown'],
        instruction_count=inventory['instructions'], unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified'],
        unproved_contracts=audit['unknown_contract_fragments'], named_without_contract=audit['named_fragments_without_proved_contract'])
    for key in ('remaining_by_region', 'pending_by_region', 'remaining_unknown_by_region'):
        checkpoint[key] = dict(Music=0, **audit['pending_by_region'])
    checkpoint['controls_text_queue'] = dict(report='Tools/Disasm/Reports/ControlsTextQueueVerification.json',
        insertion_cases=proof['insertion_cases'], numeric_role_cases=proof['numeric_role_cases'],
        typed_records=17, typed_bytes=34, last_slot_missed_after_wrap_preserved=True,
        all_free_masks_and_raw_de_words_and_number_af_values=True, complete_consumer_contract=False,
        native_execution=False, assembly_executed=False)
    action = read('ActionTextQueueCallsVerification')
    assert action['passed'] and read('ActionTextQueueCallsClassification')['passed']
    checkpoint['action_text_queue_calls'] = dict(report='Tools/Disasm/Reports/ActionTextQueueCallsVerification.json',
        cases=action['total_cases'], physical_banks_checked=8, page_sequence=[0x11,0x10],
        input_page_not_restored=True, numeric_alternate_a_becomes_11=True, unknown_6054_preserved=True,
        native_execution=False, assembly_executed=False)
    checkpoint['manual_build_check'] = dict(status='requested_pending_user_result', task='Ctrl+B, Builder/Main.asm',
        expected_image='Awakenv02.trd', expected_size=655360,
        expected_sha256='55a11de202a5334547e39a6db42c945242a2a53559dc1cf601522219e3463f32',
        codex_assembler_executed=False)
    for stem in ('ControlsTextQueueVerification', 'ControlsTextQueueClassification', 'ActionTextQueueCallsVerification', 'ActionTextQueueCallsClassification'):
        path = 'Tools/Disasm/Reports/'+stem+'.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    checkpoint['next_semantic_work'] = [x for x in checkpoint['next_semantic_work'] if not x.startswith('Controls, производитель очереди')]
    task = 'Controls, производитель очереди EC56/EC59 и два межбанковых входа Action описаны и проверены. Остаются потребитель ECA2, десятичный вывод, рисование глифов и прокрутка с полными контрактами, отдельный хвост Action Unknown6054.'
    if task not in checkpoint['next_semantic_work']:
        checkpoint['next_semantic_work'].append(task)
    (ROOT/'Tools/Disasm/Reports/InteractionCheckpoint.json').write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for path in ('README.md', 'Docs/Validation.md', 'Docs/ConformancePlan.md'):
        p = ROOT/path
        text = p.read_text('utf-8')
        for pattern, replacement in (
            (r'\b\d+ Unknown\b', str(inventory['unknown'])+' Unknown'),
            (r'\b\d+ недоказанных контрактов\b', str(audit['unknown_contract_fragments'])+' недоказанных контрактов'),
            (r'В реестре \d+ фрагмент(?:ов)?, \d+ с неизвестным назначением и \d+ без доказанного контракта',
             'В реестре '+str(inventory['fragments'])+' фрагментов, '+str(inventory['unknown'])+' с неизвестным назначением и '+str(audit['unknown_contract_fragments'])+' без доказанного контракта'),
            (r'Исходных фрагментов: \d+\.', 'Исходных фрагментов: '+str(inventory['fragments'])+'.'),
            (r'роли интерфейса: \d+\.', 'роли интерфейса: '+str(inventory['described'])+'.'),
            (r'Назначение Unknown: \d+\.', 'Назначение Unknown: '+str(inventory['unknown'])+'.'),
            (r'контракта: \d+, включая \d+', 'контракта: '+str(audit['unknown_contract_fragments'])+', включая '+str(audit['named_fragments_without_proved_contract'])),
            (r'назначение \d+ фрагментов', 'назначение '+str(inventory['described'])+' фрагментов')):
            text = re.sub(pattern, replacement, text)
        text = re.sub(r'Текущие исходники содержат \d+ фрагмент(?:ов)?', 'Текущие исходники содержат '+str(inventory['fragments'])+' фрагментов', text)
        text = text.replace('охватила 1771 ссылок', 'охватила 1772 ссылки')
        link = 'Docs/TextQueueProducer.md' if path == 'README.md' else 'TextQueueProducer.md'
        paragraph = ('[Производитель очереди Controls]('+link+') описан двумя процедурами и 17 физическими двухбайтовыми записями. '
            'Независимая модель прошла 132807 добавлений и отказов, все маски свободных мест, сырые DE и AF числового входа. '
            'Числовое назначение типа 02 подтверждено на 256 значениях с настоящим десятичным обработчиком и рисователем. '
            'Сохранены молчаливый отказ и пропуск последнего свободного элемента после маркера. Полный потребитель и нативная игра ещё не доказаны.')
        if paragraph not in text:
            text = text.rstrip()+'\n\n'+paragraph+'\n'
        link = 'Docs/ActionTextQueueCalls.md' if path == 'README.md' else 'ActionTextQueueCalls.md'
        paragraph = ('[Межбанковые входы Action в очередь Controls]('+link+') прошли 4160 сценариев с реальными вызовами '
            'и сравнением всех восьми физических банков. Подтверждены последовательность 7FFD=11, затем 10, '
            'изменение A′ числового входа на 11, сохранение регистров обёртки DE и отсутствие возврата прежнего paging. '
            'Хвост Unknown6054 выделен отдельно и остаётся неразобранным. Инструкции и физические данные сохранены, сборка Codex не выполнялась.')
        if paragraph not in text:
            text = text.rstrip()+'\n\n'+paragraph+'\n'
        p.write_text(text, encoding='utf-8')
    print(json.dumps(checkpoint['controls_text_queue'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
