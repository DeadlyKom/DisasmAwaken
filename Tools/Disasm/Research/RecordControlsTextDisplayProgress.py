"""Фиксация разобранной цепочки и фактических границ ручной проверки сборки."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    inventory, audit = read('Inventory'), read('ConformanceAudit')
    proof = read('ControlsTextDisplayVerification')
    assert proof['passed'] and read('ControlsTextDisplayClassification')['passed']
    assert read('SourceVerification')['passed'] and read('DocumentationVerification')['passed']
    checkpoint = read('InteractionCheckpoint')
    checkpoint.update(fragments=inventory['fragments'], described=inventory['described'], unknown=inventory['unknown'],
        instruction_count=inventory['instructions'], unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified'],
        unproved_contracts=audit['unknown_contract_fragments'], named_without_contract=audit['named_fragments_without_proved_contract'])
    for key in ('remaining_by_region', 'pending_by_region', 'remaining_unknown_by_region'):
        checkpoint[key] = dict(Music=0, **audit['pending_by_region'])
    checkpoint['controls_text_display'] = dict(report='Tools/Disasm/Reports/ControlsTextDisplayVerification.json',
        cases=proof['total_cases'], described_fragments=6, independent_screen_model=True,
        actual_calls_without_stubs=True, exact_register_model=False, irq_executed=False,
        native_execution=False, assembly_executed=False)
    # Проверка существующего результата ручной сборки, ассемблер здесь не вызывается.
    build = read('BuildVerification')
    image = (ROOT / 'Awakenv02.trd').read_bytes()
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert image == original and len(image) == 655360
    assert build['status'] == 'passed' and build['byte_identical'] is True
    checkpoint['manual_build_check'] = dict(status='passed_before_latest_source_changes',
        task='Ctrl+B, Builder/Main.asm', image='Awakenv02.trd', size=len(image),
        sha256=hashlib.sha256(image).hexdigest(), checked_at_utc=build['checked_at_utc'],
        active_allocations=build['active_allocations'], source_changes_after_build=True,
        current_source_assembly_verified=False, codex_assembler_executed=False)
    checkpoint['latest_user_native_observation'] = dict(emulator='Unreal', image='Awakenv02.trd',
        observation='вроде бы работает!', date='2026-11-02', full_gameplay_verified=False,
        relates_to_build_before_controls_text_display=True)
    for stem in ('ControlsTextDisplayVerification', 'ControlsTextDisplayClassification'):
        path = 'Tools/Disasm/Reports/' + stem + '.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    checkpoint['next_semantic_work'] = [item for item in checkpoint['next_semantic_work']
        if not item.startswith('Controls, производитель очереди')]
    checkpoint['next_semantic_work'] = [item for item in checkpoint['next_semantic_work']
        if not item.startswith('Controls, потребитель ECA2')]
    task = f"Controls, потребитель ECA2, десятичный вывод, шестистрочный рисователь и прокрутка описаны. Остаются {audit['pending_by_region']['Controls']} Unknown и точный состав шрифта. Полная регистровая модель и аппаратные IRQ не доказаны."
    if task not in checkpoint['next_semantic_work']:
        checkpoint['next_semantic_work'].append(task)
    bcd_path = ROOT / 'Tools/Disasm/Reports/ControlsBcdCounterClassification.json'
    if bcd_path.is_file():
        bcd = read('ControlsBcdCounterVerification')
        assert bcd['passed'] and read('ControlsBcdCounterClassification')['passed']
        checkpoint['controls_bcd_counter'] = dict(report='Tools/Disasm/Reports/ControlsBcdCounterVerification.json',
            cases=bcd['total_cases'], described_fragments=3, gate_period_calls=8,
            overflow_modulus=100000000, invalid_bcd_proved=False,
            independent_full_flag_model=False, assembly_executed=False)
        for stem in ('ControlsBcdCounterVerification', 'ControlsBcdCounterClassification'):
            value = 'Tools/Disasm/Reports/' + stem + '.json'
            if value not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(value)
    marker_path = ROOT / 'Tools/Disasm/Reports/ControlsMarkerClassification.json'
    if marker_path.is_file():
        marker = read('ControlsMarkerVerification')
        assert marker['passed'] and read('ControlsMarkerTableClassification')['passed']
        checkpoint['controls_marker'] = dict(report='Tools/Disasm/Reports/ControlsMarkerVerification.json',
            original_position_cases=marker['original_position_cases'], physical_records=8, typed_bytes=32,
            low_byte_wrap_preserved=True, overlapping_position_caveat_explicit=True, assembly_executed=False)
        for stem in ('ControlsMarkerVerification', 'ControlsMarkerTableClassification', 'ControlsMarkerClassification'):
            value = 'Tools/Disasm/Reports/' + stem + '.json'
            if value not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(value)
    if (ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyWorkerVerification.json').is_file():
        buffer = read('ControlsBufferCopyVerification')
        worker = read('ControlsBufferCopyWorkerVerification')
        assert buffer['passed'] and worker['passed']
        published = (ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyClassification.json').is_file()
        checkpoint['controls_buffer_copy_research'] = dict(composite_calls=buffer['original_calls'],
            direct_worker_calls=worker['direct_worker_calls'], pixel_bytes_per_composite_call=3072,
            semantic_source_publication=published, waiting_for_current_manual_build_result=False,
            all_documented_register_outputs_checked=worker['all_documented_register_outputs_checked'],
            documentation='Docs/ControlsBufferCopy.md', assembly_executed=False)
        for stem in ('ControlsBufferCopyVerification', 'ControlsBufferCopyWorkerVerification') + (('ControlsBufferCopyClassification',) if published else ()):
            value = 'Tools/Disasm/Reports/' + stem + '.json'
            if value not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(value)
        checkpoint['manual_build_check']['requested_for_current_sources'] = False
    (ROOT / 'Tools/Disasm/Reports/InteractionCheckpoint.json').write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name in ('README.md', 'Docs/Validation.md', 'Docs/ConformancePlan.md'):
        path = ROOT / name
        text = path.read_text('utf-8')
        for pattern, replacement in (
            (r'\b\d+ Unknown\b', str(inventory['unknown']) + ' Unknown'),
            (r'\b\d+ недоказанных контрактов\b', str(audit['unknown_contract_fragments']) + ' недоказанных контрактов'),
            (r'В реестре \d+ фрагмент(?:ов)?, \d+ с неизвестным назначением и \d+ без доказанного контракта',
             f"В реестре {inventory['fragments']} фрагментов, {inventory['unknown']} с неизвестным назначением и {audit['unknown_contract_fragments']} без доказанного контракта")):
            text = re.sub(pattern, replacement, text)
        target = 'Docs/ControlsTextDisplay.md' if name == 'README.md' else 'ControlsTextDisplay.md'
        if '](' + target + ')' not in text:
            text += ('\n[Потребитель очереди и текстовое окно Controls](' + target + ') описаны шестью фрагментами. '
                'Независимая экранная модель прошла 13827 сценариев с настоящими вызовами рисователя и прокрутки, '
                'включая общий вход EFF1 с другим экранным адресом. Проверены экран, курсоры, освобождение записей, '
                'числовой интервал, LF и повторные CR. Сохранены исходный правый узор и отсутствие проверки диапазона знаков. '
                'Полная независимая модель регистров и IRQ не доказаны. Предыдущая ручная сборка совпала с оригинальным TRD, '
                'пользователь сообщил «вроде бы работает!». После этого изменены имена и комментарии, '
                'новая сборка текущих исходников не выполнялась.\n')
        bcd_target = 'Docs/ControlsBcdCounter.md' if name == 'README.md' else 'ControlsBcdCounter.md'
        if bcd_path.is_file() and '](' + bcd_target + ')' not in text:
            text += ('\n[BCD-счётчик панели](' + bcd_target + ') описан тремя процедурами и проверен 74752 сценариями. '
                'Подтверждены все входные байты и колонки вывода тетрады, все маски обновления пар и состояния делителя, '
                'переносы корректного BCD и переполнение 99999999 в нуль. Порядок памяти E,D,L,H, '
                'зависимость обновления старших пар от младших битов маски и пунктуация вместо букв A..F сохранены. '
                'Единицы счётчика, некорректные BCD-данные и полный игровой запуск этой проверкой не доказаны. '
                'Ассемблер не запускался.\n')
        marker_target = 'Docs/ControlsMarker.md' if name == 'README.md' else 'ControlsMarker.md'
        if marker_path.is_file() and '](' + marker_target + ')' not in text:
            text += ('\n[XOR-маркер буфера](' + marker_target + ') проверен на всех 65536 положениях. '
                'Описаны 11 XOR-записей и восемь физических FMarkerPhaseMasks, сохранены все 32 байта таблицы. '
                'Потеря переноса в горизонтальных INC L и DEC L и возможность перекрыть само положение '
                'для произвольного входа явно документированы. Проверены каждый байт RAM, все записи и конечные основные пары. '
                'Сборка и нативный кадр этой проверкой не подтверждены.\n')
        buffer_target = 'Docs/ControlsBufferCopy.md' if name == 'README.md' else 'ControlsBufferCopy.md'
        if (ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyClassification.json').is_file() and '](' + buffer_target + ')' not in text:
            text += ('\n[Перенос линейного буфера в экран](' + buffer_target + ') описан двумя процедурами. '
                'Проверены 512 полных переносов растра 256 на 96 пикселей и 1728 прямых вызовов общего копировщика, '
                'экран, точное множество записей и все документированные регистры, включая основные и альтернативные флаги. '
                'Указаны условия выравнивания, отсутствие перекрытия и граница трети экрана. '
                'Нулевой счётчик и аппаратные IRQ не объявлены проверенными. Инструкции и адреса сохранены, ассемблер не запускался.\n')
        path.write_text(text, encoding='utf-8')
    print(json.dumps(dict(described=inventory['described'], unknown=inventory['unknown'],
        unproved_contracts=audit['unknown_contract_fragments'], codex_assembler_executed=False), indent=2))


if __name__ == '__main__':
    main()
