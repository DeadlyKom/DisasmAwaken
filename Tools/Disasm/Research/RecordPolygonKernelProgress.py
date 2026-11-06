"""Фиксация полного опубликованного диапазона заполнителя и честных границ его модели."""
import json
from ClassifyControlsTextDisplay import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    def read(stem):return json.loads((reports/(stem+'.json')).read_text('utf-8'))
    inventory,audit=read('Inventory'),read('ConformanceAudit')
    assert inventory['fragments']==1248 and inventory['instructions']==42696
    assert audit['unknown_contract_fragments']==211 and not audit['missing_include_order']
    for name in ('SourceVerification','DocumentationVerification','FilePlacementVerification','SourceLabelsVerification'):
        assert read(name)['passed']
    proof=read('ActionPolygonFillBitmapVerification')
    assert proof['passed'] and proof['total_cases']==11562 and proof['all_physical_ram_bytes_proved']
    assert read('ActionPolygonFlowNamesVerification')['code_bytes']==1033
    heading='Строковое ядро и полная модель RAM заливки ACTION, 2026-11-04'
    for relative,prefix in (('README.md','Docs/'),('Docs/Validation.md',''),('Docs/ConformancePlan.md','')):
        path=ROOT/relative;text=path.read_text('utf-8')
        if '## '+heading in text:continue
        body=(f'\n## {heading}\n\n'
            f'Весь исполняемый диапазон [линейной заливки]({prefix}ActionPolygonFill.md) D1C0..D5C8 опубликован двенадцатью исходниками, '
            'сохранены 1033 байта и 679 инструкций. Шесть коротких переходников прошли 132096 локальных сценариев. '
            'Общий числовой эталон прошёл 11562 сценария полного входа D511, сверены изображение, основные, альтернативные и индексные регистры, '
            'все физические банки и кратность записей. У колонки 255 сохранены 225 попыток записи неизменённых значений вне обычной пиксельной области. '
            'Одиннадцать числовых межфайловых переходов получили доказанные имена.\n\n'
            'Всего 1248 фрагментов, описаны 1144, остаются 104 Unknown и 211 недоказанных договоров, включая 107 уже именованных. '
            'Статические проверки исходников, размещения, меток, ссылок и общего графа прошли. '
            'Гарантии модели ограничены выпуклыми контурами положительного обхода 3..60 точек внутри 256×96 и режимами 0..4. '
            'R/T, IRQ, все совместные входы и нативный игровой запуск не доказаны. Последняя пользовательская сборка остаётся срезом 128990 строк, '
            'новые исходники ею не покрыты. Codex сборку не запускал. Полный проект ещё не завершён.\n')
        path.write_bytes((text.rstrip()+'\n'+body).encode('utf-8'))
    print(json.dumps(dict(passed=True,fragments=1248,unknown=104,whole_project_complete=False)))


if __name__=='__main__':main()
