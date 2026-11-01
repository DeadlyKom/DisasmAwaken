"""Итоги доказанных строк и фаз, без объявления завершённости всего дизассемблера."""
from pathlib import Path
import collections, json

ROOT = Path(__file__).resolve().parents[3]


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    inventory, audit = read('Inventory'), read('ConformanceAudit')
    source_map = read('SourceMap')
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in source_map if item['kind'] == kind)
                                           for kind in sorted({item['kind'] for item in source_map})}
    assert sum(inventory['physical_bytes_by_kind'].values()) == read('SourceVerification')['covered_bytes']
    inventory['ranges_by_kind'] = dict(collections.Counter(item['kind'] for item in source_map))
    (ROOT/'Tools/Disasm/Reports/Inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    rows, phases, original = (read(stem) for stem in ('MusicPatternRowsVerification', 'MusicPatternPhasesVerification', 'OriginalMusicSynthesisVerification'))
    assert all(x['passed'] for x in (rows, phases, original, read('MusicPatternsClassification')))
    assert inventory['fragments'] == 1186 and audit['unknown_contract_fragments'] == 370
    checkpoint = read('InteractionCheckpoint')
    checkpoint.update(fragments=inventory['fragments'], described=inventory['described'], unknown=inventory['unknown'],
        instruction_count=inventory['instructions'], unproved_contracts=audit['unknown_contract_fragments'],
        named_without_contract=audit['named_fragments_without_proved_contract'],
        unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified'])
    for key in ('remaining_by_region', 'pending_by_region', 'remaining_unknown_by_region'):
        checkpoint[key] = dict(Music=0, **audit['pending_by_region'])
    checkpoint['music_patterns'] = dict(row_cases=rows['total_cases'], phase_cases=phases['total_cases'],
        original_tune_decoder_calls=original['pattern_calls_by_channel'], original_tune_bc_phases=original['independently_checked_bc_phases'],
        described_blocks=7, physical_bytes_preserved=True, reserved_effects_executed=False,
        full_game_or_arbitrary_streams_proved=False, native_audio_verified=False, assembly_executed=False)
    checkpoint['music_synthesis']['pattern_decoder_independently_proved'] = True
    checkpoint['music_pattern_dispatch']['full_decode_proved'] = True
    checkpoint['music_pattern_dispatch']['proof_scope'] = 'Конечные строки с эффектами 1..5, 8, 9, все фактические строки исходной композиции до первой петли'
    checkpoint['music_ay_output']['pending_pattern_parse'] = None
    advance = read('MusicAdvanceAVerification')
    assert advance['passed'] and read('MusicAdvanceAClassification')['passed']
    checkpoint['music_advance_a'] = dict(report='Tools/Disasm/Reports/MusicAdvanceAVerification.json',
        cases=advance['total_cases'], original_tune_executions=original['independently_checked_advance_a'],
        original_tune_position_changes=original['independently_checked_position_changes'],
        original_tune_position_loops=original['independently_checked_position_loops'],
        original_position_times_two_preserved=True, original_sp_restore_proved=True,
        assembly_executed=False, native_audio_verified=False)
    tables = read('MusicPlayerTablesClassification')
    assert tables['passed']
    checkpoint['music_player_data'] = dict(report='Tools/Disasm/Reports/MusicPlayerTablesClassification.json',
        typed_bytes=tables['typed_bytes'], physical_instances=tables['physical_instances'], source_files=tables['source_files'],
        volume_zero_overlay_preserved=True, composition_records_not_yet_typed=False, assembly_executed=False)
    composition, tail = read('MusicCompositionClassification'), read('MusicSectorTailClassification')
    assert composition['passed'] and tail['passed']
    checkpoint['music_composition'] = dict(report='Tools/Disasm/Reports/MusicCompositionClassification.json',
        source_parts=72, preserved_bytes=4137, physical_struct_instances=257,
        command_and_parameter_groups=2861, shared_pattern_streams=41, sample_steps=77, ornament_steps=57,
        unknown_header_byte='Unknown63, offset 99, original value 02',
        physical_placement_verified=True, assembly_executed=False, native_audio_verified=False)
    checkpoint['music_sector_tail'] = tail
    initialization = read('MusicInitializeAndMuteVerification')
    assert initialization['passed'] and read('MusicInitializationClassification')['passed']
    checkpoint['music_initialization'] = dict(report='Tools/Disasm/Reports/MusicInitializeAndMuteVerification.json',
        cases=initialization['total_cases'], exact_initialize_af='FF43', exact_mute_f='42 OR input Carry',
        ay_ram_buffer_not_cleared=True, partial_reset_only=True, public_and_module_entries_checked=True,
        assembly_executed=False, native_audio_verified=False)
    cleanup = read('ResearchCleanupMusicVerification')
    assert cleanup['passed'] and cleanup['active_files_unchanged']
    checkpoint['temporary_cleanup'] = ('695 прежних снимков сохранены в LegacySnapshots-20261031.zip. '
        'Ещё 302 проверенных снимка, 4455 распакованных файлов и 1149203729 байтов сохранены '
        'в RecentSnapshots-20261101-Music.zip размером 77536565 байтов. Проверены 4022 неизменённых '
        'рабочих файла. Маркеры защищают от повторного экспорта, восстановление через ResearchArchive.py. '
        'Три используемых кандидата, сценарии, оригиналы, отчёты и данные сборки сохранены.')
    checkpoint['next_semantic_work'] = [
        'Музыка, переход позиций и договор AdvancePatternA, оставшиеся именованные входы без доказанных контрактов, физические таблицы и данные композиции MUZ1. Зарезервированные эффекты не исполнены.'
        if x.startswith('Музыка, четыре Unknown') else x for x in checkpoint['next_semantic_work']]
    checkpoint['next_semantic_work'] = [
        'Музыка, Unknown63 в заголовке композиции, интегральный договор PlayFrame и независимая композиция оставшейся подготовки полного кадра, аппаратные IRQ и нативный звук. Все 49 зарегистрированных блоков имеют описанный контракт, зарезервированные эффекты не исполнены.'
        if x.startswith(('Музыка, переход позиций', 'Музыка, физические таблицы', 'Музыка, Unknown63')) else x for x in checkpoint['next_semantic_work']]
    for stem in ('MusicPatternRowsVerification', 'MusicPatternPhasesVerification', 'MusicPatternsClassification', 'MusicAdvanceAVerification', 'MusicAdvanceAClassification', 'MusicPlayerTablesClassification', 'MusicCompositionClassification', 'MusicCompositionLayout', 'MusicSectorTailClassification', 'ResearchCleanupMusicVerification', 'MusicInitializeAndMuteVerification', 'MusicInitializationClassification'):
        path = 'Tools/Disasm/Reports/' + stem + '.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    (ROOT / 'Tools/Disasm/Reports/InteractionCheckpoint.json').write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path in ('README.md', 'Docs/Validation.md', 'Docs/ConformancePlan.md'):
        p = ROOT / path
        text = p.read_text('utf-8')
        for old, new in (('1183 фрагмент', '1186 фрагмент'), ('назначение 993 фрагментов', 'назначение 1000 фрагментов'),
                         ('190 Unknown', '186 Unknown'), ('375 недоказанных', '370 недоказанных'), ('371 недоказанных', '370 недоказанных'),
                         ('190 с неизвестным назначением и 375 без', '186 с неизвестным назначением и 370 без'),
                         ('186 с неизвестным назначением и 371 без', '186 с неизвестным назначением и 370 без'),
                         ('Исходных фрагментов: 1183.', 'Исходных фрагментов: 1186.'),
                         ('роли интерфейса: 993.', 'роли интерфейса: 1000.'), ('Назначение Unknown: 190.', 'Назначение Unknown: 186.'),
                         ('контракта: 375, включая 185', 'контракта: 370, включая 184'),
                         ('контракта: 371, включая 185', 'контракта: 370, включая 184'),
                         ('185 у уже именованных', '184 у уже именованных'),
                         ('Декодирование паттернов пока не доказано независимо, аппаратные IRQ и нативный звук не проверены.',
                          'Декодирование поддерживаемых строк доказано отдельно, аппаратные IRQ и нативный звук не проверены.')):
            text = text.replace(old, new)
        link = 'Docs/MusicPattern.md' if path == 'README.md' else 'MusicPattern.md'
        text = text.replace('но оставшиеся договоры, физические данные, зарезервированные эффекты и нативная проверка ещё не завершены.',
                            'все 49 музыкальных блоков имеют описанные договоры, но физические данные, зарезервированные эффекты и нативная проверка ещё не завершены.')
        paragraph = ('[Декодирование паттернов A/B/C и распределитель фаз B/C](' + link + ') описаны семью физическими блоками. '
            'Независимые модели прошли 46992 строки и 13216 фаз. На исходной композиции отдельно совпали все 2304 вызова декодеров '
            'и 5377 проходов фаз до первого повтора позиций. Проверены общие хвосты, порядок отложенных эффектов, память, регистры '
            'и физические кадры стека. Среди зарегистрированных музыкальных блоков Unknown больше нет, '
            'все 49 музыкальных блоков имеют описанные договоры, но физические данные, зарезервированные эффекты и нативная проверка ещё не завершены.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        initialization_link = 'Docs/MusicInitialization.md' if path == 'README.md' else 'MusicInitialization.md'
        paragraph = ('[Инициализация и глушение AY](' + initialization_link + ') проверены 132864 сценариями. '
            'Для Stop и ClearAyRegisters перебраны все 65536 AF на каждый вход, RAM не изменяется. '
            'Initialize и InitializeModule возвращают точный AF=FF43, выполняют частичную настройку состояния '
            'и оставляют прежний RAM-буфер AY. Проверены все 48 преобразованных указателей, SP и состояние IFF. '
            'Комментарии и адресные имена обновлены без изменения инструкций, сборка не выполнялась.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        data_link = 'Docs/MusicPlayerData.md' if path == 'README.md' else 'MusicPlayerData.md'
        paragraph = ('[Физические таблицы проигрывателя](' + data_link + ') оформлены 163 экземплярами пяти структур, '
            '545 исходных байтов сохранены побайтно. Разобраны 48 указателей, 14-байтовый буфер AY, '
            'три счётчика строк, 15 строк громкости и 96 слов периодов. Нулевая строка громкости наложена '
            'на буфер AY и счётчики, начало следующей строки также используется как пустой сэмпл и орнамент. '
            'Данные самой композиции оформлены отдельно в исходниках. Сборка не выполнялась.')
        text = text.replace('Данные самой композиции пока остаются исходным PT3-ресурсом.', 'Данные самой композиции оформлены отдельно в исходниках.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        composition_link = 'Docs/MusicComposition.md' if path == 'README.md' else 'MusicComposition.md'
        paragraph = ('[Исходная композиция Antichrist](' + composition_link + ') оформлена 72 частями, все 4137 байтов сохранены. '
            'Описаны 28 позиций, 19 троек указателей, 41 общий поток с 2861 группой команд и параметров, '
            '12 сэмплов с 77 шагами и 14 орнаментов с 57 шагами. Общие ссылки и нулевые относительные слова сохранены. '
            'Байт Unknown63 остаётся явно неразобранным. Отдельный 215-байтовый секторный хвост MUZ1.C сохранён целиком. '
            'Физический порядок включений проверен, сборка не выполнялась.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        paragraph = ('[Переход позиций A](' + link + ') прошёл 5712 синтетических сценариев и все 1793 исполнения исходной композиции, '
            '29 смен позиций и одну петлю. Проверены исходное удвоение байта позиции, три POP указателей, '
            'относительная адресация по модулю 65536 и восстановление SP перед декодером. Сборка не выполнялась.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        p.write_text(text, encoding='utf-8')
    print(json.dumps(checkpoint['music_patterns'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
