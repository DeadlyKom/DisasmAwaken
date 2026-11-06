"""Фиксация текущего доказательства отсечения и растеризации, не запуск сборки."""
import json
from ClassifyControlsTextDisplay import ROOT


def main():
    reports = ROOT/'Tools/Disasm/Reports'
    # Проверка фактических итогов перед записью датированного среза.
    def read(stem):
        return json.loads((reports/(stem+'.json')).read_text('utf-8'))
    inventory, audit = read('Inventory'), read('ConformanceAudit')
    assert inventory['fragments']==1236 and inventory['unknown']==104
    assert audit['unknown_contract_fragments']==211 and audit['named_fragments_without_proved_contract']==107
    for stem in ('SourceVerification','DocumentationVerification','SourceLabelsVerification','FilePlacementVerification',
                 'ActionClipCaseRegistersVerification','ActionPolygonVerification','ActionSingleEdgeVerification',
                 'ActionLineRasterVerification','ActionPolygonFillBitmapVerification','ActionLineModesVerification'):
        assert read(stem)['passed']
    # Уточнение происхождения моделей в двух реестрах, без переисполнения публикации исходников.
    for stem in ('ActionPolygonClassification','ActionSingleEdgeClassification'):
        path=reports/(stem+'.json');record=read(stem)
        if 'independent_model_cases' in record:
            record['compositional_model_cases']=record.pop('independent_model_cases')
        record['independent_geometry_proved']=False
        path.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    heading='Полные договоры отсечения и линейная растеризация ACTION, 2026-11-04'
    for relative, prefix in (('README.md','Docs/'),('Docs/Validation.md',''),('Docs/ConformancePlan.md','')):
        path=ROOT/relative;text=path.read_text('utf-8')
        if '## '+heading in text:
            continue
        body=(f'\n## {heading}\n\n'
            f'[Группа случаев отсечения]({prefix}ActionClipCases.md) проверена в 176640 сценариях с полными регистрами кроме R, всей физической RAM и кратностью записей. Опубликованы 70 договоров, 36 внутренних адресных меток заменены доказанными именами. [Полный цикл полигона]({prefix}ActionPolygon.md) прошёл 5171 сценарий, [одиночное ребро]({prefix}ActionSingleEdge.md) 24832. Модели композиционные, независимое геометрическое доказательство отсечения не заявляется. Две точки CF0B/CF1B оформлены реальными FRenderProjectedPoint с сохранением десяти байтов.\n\n'
            f'[DrawLinearLine]({prefix}ActionLineRaster.md) выделен с сохранением 256 байтов и 153 инструкций. Пройдены 56064 сценария AND/OR/XOR, включая 6144 вне штатной вертикальной области. Сверены регистры кроме R, RAM и кратность записей. Расширенные записи в рабочие области сохраняются, их игровая допустимость не доказана. Оформлены 16 физических масок, зарегистрированы восемь писателей opcode, сохранение SP и два внешних писателя MaskOffset. Подготовка режимов прошла 7168 сценариев.\n\n'
            f'[Заливка граней]({prefix}ActionPolygonFill.md) прошла 11522 сценария изображения и основных, альтернативных и индексных регистров. Полный эталон изменяемых операндов и временного стека пока не завершён. [CF08]({prefix}ActionClipTableAlias.md) доказан как часть таблицы, возможное исполнение тех же байтов остаётся Unknown.\n\n'
            'Статические проверки прошли, сохранены 42017 инструкций, 41 размещение и 479744 байта. Проверены 4855 меток и 1661 физический диапазон. Всего 1236 фрагментов, описаны 1132, остаются 104 Unknown и 211 недоказанных договоров, включая 107 уже именованных. Последняя пользовательская сборка относится к прежнему срезу 128990 строк, 1,609 с с полным совпадением TRD. Новые исходники ею не покрыты. Codex сборку, IRQ и нативный запуск не выполнял. Полный проект ещё не завершён.\n')
        path.write_bytes((text.rstrip()+'\n'+body).encode('utf-8'))
    print(json.dumps(dict(passed=True,fragments=1236,unknown=104,unproved_contracts=211,assembly_executed=False)))


if __name__=='__main__':
    main()
