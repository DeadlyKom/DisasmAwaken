"""Актуальные показатели после копировщика, точек, таблиц и арифметического делителя."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]


def main():
    from RecordControlsTextDisplayProgress import main as record_previous
    record_previous()
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def write(stem,value):
        (ROOT / ('Tools/Disasm/Reports/'+stem+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checkpoint = read('InteractionCheckpoint')
    points,division = read('ControlsBufferPointsVerification'),read('ControlsDivisionVerification')
    assert points['passed'] and division['passed']
    for stem in ('ControlsBufferPointsClassification','ControlsBufferPointsTableClassification','ActionBitmapTablesClassification','ControlsDivisionClassification'):
        assert read(stem)['passed']
    checkpoint['controls_buffer_points'] = dict(report='Tools/Disasm/Reports/ControlsBufferPointsVerification.json',
        cases=points['total_cases'],physical_records=35,typed_bytes=70,field_order=['Y','X'],
        zero_initializers_preserved=True,generator_orbit=points['generator_orbit'],assembly_executed=False)
    checkpoint['action_bitmap_tables'] = dict(report='Tools/Disasm/Reports/ActionBitmapTablesClassification.json',
        runtime_bytes=1024,exact_af='2062',exact_alternate_af='8083',static_data_added=False,assembly_executed=False)
    checkpoint['controls_division'] = dict(report='Tools/Disasm/Reports/ControlsDivisionVerification.json',
        cases=division['total_cases'],all_fraction_a_b_pairs=True,zero_divisor_all_words=True,
        quotient_overflow_recurrence_explicit=True,exact_registers_and_flags=True,assembly_executed=False)
    span_published = (ROOT / 'Tools/Disasm/Reports/ControlsSpanMasksClassification.json').is_file()
    if span_published:
        masks = read('ControlsSpanMasksVerification')
        assert masks['passed'] and read('ControlsSpanMasksClassification')['passed']
        checkpoint['controls_span_masks'] = dict(report='Tools/Disasm/Reports/ControlsSpanMasksVerification.json',
            cases=masks['total_cases'],exact_registers_and_flags=True,all_x_y_bytes=True,
            shared_d18c_has_no_local_output_effect=True,assembly_executed=False)
    for stem in ('ControlsBufferPointsVerification','ControlsBufferPointsClassification','ControlsBufferPointsTableClassification',
                 'ActionBitmapTablesClassification','ControlsDivisionVerification','ControlsDivisionClassification') + (('ControlsSpanMasksVerification','ControlsSpanMasksClassification') if span_published else ()):
        value = 'Tools/Disasm/Reports/'+stem+'.json'
        if value not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(value)
    checkpoint.setdefault('last_user_confirmed_build',dict(date='2026-11-02',
        errors=0,warnings=0,compiled_lines=114539,work_seconds=1.468,
        full_image_byte_identical=True,size=655360,source_changes_after_build=True,codex_assembler_executed=False))
    if 'last_verified_build_artifact' in checkpoint:
        checkpoint['last_verified_build_artifact']['source_changes_after_build'] = True
    checkpoint['next_semantic_work'] = [value for value in checkpoint['next_semantic_work']
        if not value.startswith('Controls, потребитель ECA2')]
    checkpoint['next_semantic_work'].append('Controls, дальнейший разбор обновления координат CB00 и вызывающих геометрических процедур CF0B/D10A. Копировщик, генератор точек и оба входа деления описаны. Полный игровой цикл и IRQ не доказаны.')
    write('InteractionCheckpoint',checkpoint)
    modified = read('ModifiedCode')
    for item in modified:
        if item['region'] == 'Controls' and item['target'] in (0xCA8F,0xCA84,0xCA8A):
            item.update(writer_bank=1,target_bank=1,target_region='Controls',target_slot=22)
    write('ModifiedCode',modified)
    for name in ('README.md','Docs/Validation.md','Docs/ConformancePlan.md'):
        path = ROOT / name
        text = path.read_text('utf-8')
        prefix = 'Docs/' if name == 'README.md' else ''
        if ']('+prefix+'ControlsBufferPoints.md)' not in text:
            text += ('\n[Генератор и 35 XOR-точек]('+prefix+'ControlsBufferPoints.md) проверены 66754 сценариями. '
                'Перебраны все состояния Seed и все координаты растра, исполнены настоящие 70 вызовов генератора в каждой подготовке. '
                'Оформлены 35 физических FBufferPoint с исходными нулевыми байтами и точный договор построителя 1024 байтов таблиц. '
                'Установлены неравномерные границы и период 387 после 59 шагов штатного Seed=0. Инструкции сохранены.\n')
        if ']('+prefix+'ControlsDivision.md)' not in text:
            text += ('\n[Оба входа восьмишагового деления]('+prefix+'ControlsDivision.md) проверены 521984 сценариями. '
                'Подтверждены точные регистры, флаги, отсутствие записей RAM, все A,B дробного входа и все делимые при B=0. '
                'Нулевой делитель возвращает FF, переполнение описано исходной байтовой рекурсией. '
                'Условия вызывающих геометрических процедур, IRQ и нативная игра не объявлены доказанными. Сборка Codex не выполнялась.\n')
        if span_published and ']('+prefix+'ControlsSpanMasks.md)' not in text:
            text += ('\n[Краевые маски пиксельного байта]('+prefix+'ControlsSpanMasks.md) описаны двумя помощниками, '
                '135168 проверок охватывают все X,Y, все общие байты D18C и все фазы маски. '
                'Проверены точные регистры, флаги, SavedB и сохранённый AF на CPU-стеке. '
                'Указано, что Z не проверяет возвращаемую маску, а чтение D18C не влияет на эти выходы. '
                'Инструкции сохранены, сборка Codex не выполнялась.\n')
        path.write_text(text,encoding='utf-8')
    print(json.dumps({key:checkpoint[key] for key in ('described','unknown','unproved_contracts','named_without_contract')},indent=2))


if __name__ == '__main__':
    main()
