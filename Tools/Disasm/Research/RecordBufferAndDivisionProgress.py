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
    checkpoint['next_semantic_work'] = [value for value in checkpoint['next_semantic_work']
        if not value.startswith('Controls, дальнейший разбор обновления координат CB00')]
    task = 'Controls, дальнейший разбор геометрических процедур CF0B/D0CA/D10A и их данных. CB00, копировщик, генератор точек и оба входа деления описаны. Полный игровой цикл и IRQ не доказаны.'
    if task not in checkpoint['next_semantic_work']:
        checkpoint['next_semantic_work'].append(task)
    # Проверка новых доказательств перед включением в текущую контрольную точку.
    for stem, key in (('ControlsPointRespawnVerification', 'controls_point_respawn'),
                      ('ControlsPointRespawnDispatchVerification', 'controls_point_respawn_dispatch'),
                      ('ControlsPointProductsVerification', 'controls_point_products'),
                      ('ControlsPointMotionVerification', 'controls_point_motion')):
        proof = read(stem)
        assert proof['passed']
        checkpoint[key] = dict(report='Tools/Disasm/Reports/'+stem+'.json',
            cases=proof.get('total_cases', proof.get('cases')), assembly_executed=False,
            irq_executed=False, native_execution=False)
    for stem in ('ControlsPointRespawnVerification','ControlsPointRespawnDispatchVerification',
                 'ControlsPointRespawnCodeClassification','ControlsPointRespawnClassification',
                 'ControlsPointProductsVerification','ControlsPointMotionVerification',
                 'ControlsPointMotionClassification','ActionSineTableClassification'):
        assert read(stem)['passed']
        value = 'Tools/Disasm/Reports/'+stem+'.json'
        if value not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(value)
    checkpoint['action_sine_table'] = dict(report='Tools/Disasm/Reports/ActionSineTableClassification.json',
        typed_bytes=256, physical_records=256, record_type='FFixedSineValue',
        original_action_offset=0x3900, ram_address=0x9900, assembly_executed=False)
    for stem,key in (('ControlsEvenSpan','controls_even_span'),('ControlsInteriorRows','controls_interior_rows'),('ControlsSquares','controls_squares'),('ControlsRasterStep','controls_raster_step'),('ControlsComponentCompare','controls_component_compare'),('ControlsSmallMasks','controls_small_masks'),('ControlsSmallBodies','controls_small_bodies')):
        proof=read(stem+'Verification')
        assert proof['passed'] and read(stem+'Classification')['passed']
        checkpoint[key]=dict(report='Tools/Disasm/Reports/'+stem+'Verification.json',cases=proof['total_cases'],
            exact_registers_flags_memory_writes_and_r=True,assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            value='Tools/Disasm/Reports/'+stem+suffix+'.json'
            if value not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(value)
    for stem in ('ControlsEvenSpanCodeClassification','ControlsSquareTableClassification','ControlsSquareEntrySplitClassification'):
        assert read(stem)['passed']
        value='Tools/Disasm/Reports/'+stem+'.json'
        if value not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(value)
    checkpoint['controls_square_table']=dict(typed_bytes=512,physical_records=512,planes=['C300','C400'],
        record_type='FSquareTableByte',formula_used_for_assembly=False)
    push=read('ControlsPushSpansVerification')
    assert push['passed'] and read('ControlsPushSpansClassification')['passed']
    checkpoint['controls_push_spans']=dict(cases=push['total_cases'],typed_as_code_bytes=88,instructions=64,
        full_rasterizers_proved=False,original_function_status_preserved='unknown',
        actual_helpers_and_nonlocal_returns=True,assembly_executed=False,irq_executed=False,native_execution=False)
    for suffix in ('Verification','Classification'):
        value='Tools/Disasm/Reports/ControlsPushSpans'+suffix+'.json'
        if value not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(value)
    for stem in ('ControlsSmallMaskTablesClassification','ControlsBodyProjectionClassification'):
        assert read(stem)['passed']
        value='Tools/Disasm/Reports/'+stem+'.json'
        if value not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(value)
    if checkpoint.get('last_user_confirmed_build',{}).get('compiled_lines',0)<114939:
        checkpoint['last_user_confirmed_build'] = dict(date='2026-11-02',
            errors=0, warnings=0, compiled_lines=114939, work_seconds=1.375,
            full_image_byte_identical=True, size=655360, source_changes_after_build=True,
            observation='Успешная ручная сборка перед публикацией UpdateBufferPoints',
            codex_assembler_executed=False)
    checkpoint['last_user_confirmed_build']['source_changes_after_build']=True
    write('InteractionCheckpoint',checkpoint)
    modified = read('ModifiedCode')
    for item in modified:
        if item['region'] == 'Controls' and item['target'] in (0xCA8F,0xCA84,0xCA8A,0xCEB4,0xD5B5,0xD600,0xD716,0xD80E,0xD900,0xDA83):
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
        for doc, note in (
            ('ControlsPointRespawn', 'Оба входа возврата точки разобраны с точными выборками R, фазами и нулевым шагом. Вход CE5D извлечён из 71 исходного байта.'),
            ('ActionSineTable', 'Оформлены 256 физических FFixedSineValue исходной синусоиды ACTION, совпадение формулы не используется для генерации сборочных данных.'),
            ('ControlsPointMotion', 'Полная CB00 описана как UpdateBufferPoints. Проверены 3712 сценариев, включая три пути непродвижения, и 262144 случая четырёх умножителей. Все исходные инструкции сохранены, IRQ и нативный игровой кадр не проверены.'),
            ('ControlsEvenSpan','Описаны три физических части динамического заполнителя, проверены 23297 сценариев и 15 целей изменяемого JR. Выделены 24 исполненных байта, два недостижимых в договоре байта сохранены как неизвестные.'),
            ('ControlsInteriorRows','Подготовитель и оба направления внутренней заливки описаны по 134612 сценариям. Установлены 30 внутренних столбцов, ограничение 96 строками, изменение CP/JR и чередование IXL XOR IXH.'),
            ('ControlsSquares','Оформлены 512 физических байтов квадратов. ReadByteSquare и SqrtSquareDiff отделены после исходных RET от UnknownD314 и UnknownD633. Проверены 196608 случаев, все записи стека и R. Остальные хвосты рисования остаются неизвестными.'),
            ('ControlsRasterStep','Оба шага строки прошли 196608 сценариев, включая каждый HL и каждый сохранённый AF. Доказаны обычный и нелокальный возвраты, точные SP, R, переключение IXL и отсутствие записей RAM.'),
            ('ControlsPushSpans','Три цепочки PUSH AF прошли 65280 сценариев с настоящими помощниками строки. Выделены 88 байтов и 64 инструкции, проверены временный SP в растре и нелокальный выход. Полные рисователи сохраняют Unknown.'),
            ('ControlsComponentCompare','CompareComponents описан с точными F, R и продвижением IY. 327680 проверок охватили все пары старших, средних байтов и каждый IY. Оформлены поля FComponent24, младший байт и разряд 7 старшего не участвуют в ключе. Игровой смысл порога прямого допуска остаётся вне локального договора.'),
            ('ControlsSmallMasks','Подготовитель малых масок прошёл 14336 сценариев. Оформлены 18 физических затравок и 12 реально записываемых байтов, повтор Row00 и арифметический SRA сохранены. Следующие 20 байтов остаются неизвестными.'),
            ('ControlsSmallBodies','Малый рисователь полностью описан для исходного шаблона. 83152 сценария проверяют все пары режима и радиуса, смещения, отсечение, пиксели, повторные записи, регистры и R. Оформлен физический FBodyProjection, остальные флаги и большой рисователь остаются неразобранными.')):
            if ']('+prefix+doc+'.md)' not in text:
                text += '\n['+doc+']('+prefix+doc+'.md). '+note+'\n'
        path.write_text(text,encoding='utf-8')
    print(json.dumps({key:checkpoint[key] for key in ('described','unknown','unproved_contracts','named_without_contract')},indent=2))


if __name__ == '__main__':
    main()
