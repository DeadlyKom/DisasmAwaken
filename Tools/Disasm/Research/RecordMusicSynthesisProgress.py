"""Фиксация проверенного этапа ядра музыки, без сборки и изменения игровых байтов."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))

    inventory = read('Inventory')
    audit = read('ConformanceAudit')
    synthetic = read('MusicSynthesisVerification')
    original = read('OriginalMusicSynthesisVerification')
    # Проверка независимых моделей и текущего сохранения исходных инструкций.
    assert synthetic['passed'] and original['passed'] and read('SourceVerification')['passed']
    assert inventory['fragments'] == audit['registered_functions'] == 1183
    checkpoint = read('InteractionCheckpoint')
    for field, value in dict(fragments=inventory['fragments'], described=inventory['described'],
                             unknown=inventory['unknown'], unproved_contracts=audit['unknown_contract_fragments'],
                             named_without_contract=audit['named_fragments_without_proved_contract'],
                             instruction_count=inventory['instructions'],
                             unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified']).items():
        checkpoint[field] = value
    for field in ('remaining_by_region', 'pending_by_region', 'remaining_unknown_by_region'):
        checkpoint[field] = audit['pending_by_region']
    checkpoint['music_gate_ticks']['parent_a_b_unknown_preserved'] = False
    checkpoint['music_gate_ticks']['parent_a_b_now_described'] = True
    checkpoint['music_synthesis'] = dict(report='Tools/Disasm/Reports/MusicSynthesisVerification.json',
        cases=synthetic['total_cases'], original_tune_frames=original['frames'],
        channel_a_b_finish_cases=read('MusicChannelABFinishVerification')['cases'],
        new_instructions=54, newly_extracted_bytes=87, physical_loop_header_and_step_layout_checked=True,
        source_arithmetic_quirks_preserved=True, pattern_decoder_independently_proved=False,
        native_audio_verified=False, assembly_executed=False)
    checkpoint['next_semantic_work'] = [
        'Музыка, четыре Unknown-фрагмента декодирования паттернов, полные кадровые договоры TickDispatch и AdvancePatternA, физические таблицы и данные композиции MUZ1.'
        if x.startswith('Музыка, шесть Unknown') else x for x in checkpoint['next_semantic_work']]
    for stem in ('MusicSynthesisVerification', 'OriginalMusicSynthesisVerification',
                 'MusicChannelABFinishVerification', 'MusicSynthesisClassification'):
        assert read(stem)['passed']
        path = 'Tools/Disasm/Reports/' + stem + '.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    # Обновление только итоговых показателей и описания завершённого локального этапа.
    for path in ('README.md', 'Docs/Validation.md', 'Docs/ConformancePlan.md'):
        p = ROOT / path
        text = p.read_text('utf-8')
        for before, after in (
            ('1181 фрагмент', '1183 фрагмент'), ('39759 проверенных инструкций', '39813 проверенных инструкций'),
            ('назначение 989 фрагментов', 'назначение 993 фрагментов'),
            ('192 Unknown', '190 Unknown'), ('379 недоказанных контрактов', '376 недоказанных контрактов'),
            ('187 у уже именованных', '186 у уже именованных'), ('1769 ссылок', '1771 ссылок'),
            ('192 с неизвестным назначением и 379 без', '190 с неизвестным назначением и 376 без'),
            ('Исходных фрагментов: 1164.', 'Исходных фрагментов: 1183.'),
            ('роли интерфейса: 964.', 'роли интерфейса: 993.'),
            ('Назначение Unknown: 200.', 'Назначение Unknown: 190.'),
            ('контракта: 379, включая 187', 'контракта: 376, включая 186'),
            ('Размеченных инструкций: 39576.', 'Размеченных инструкций: 39813.')):
            text = text.replace(before, after)
        link = 'Docs/MusicSynthesis.md' if path == 'README.md' else 'MusicSynthesis.md'
        paragraph = ('[Ядро музыкального синтеза](' + link + ') разобрано для каналов A, B и C. '
            'Независимая модель прошла 67328 сценариев и совпала с 5377 кадрами исходной композиции до первого повтора позиций. '
            'Проверены промежуточные состояния, записи памяти и фактические обращения к портам AY. '
            'Сохранены особенности адресации сэмпла A/B, выход индекса ноты за основную таблицу и остаточный старший байт ограниченного скольжения. '
            'Декодирование паттернов пока не доказано независимо, аппаратные IRQ и нативный звук не проверены. Сборка не выполнялась.')
        if paragraph not in text:
            text = text.rstrip() + '\n\n' + paragraph + '\n'
        p.write_text(text, encoding='utf-8')
    (ROOT / 'Tools/Disasm/Reports/InteractionCheckpoint.json').write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(checkpoint['music_synthesis'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
