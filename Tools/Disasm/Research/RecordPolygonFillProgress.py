"""Фиксация пяти опубликованных частей линейной заливки без объявления всего ядра завершённым."""
import json
from ClassifyControlsTextDisplay import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    def read(stem):return json.loads((reports/(stem+'.json')).read_text('utf-8'))
    inventory,audit=read('Inventory'),read('ConformanceAudit')
    assert inventory['fragments']==1241 and inventory['instructions']==42546
    assert audit['unknown_contract_fragments']==211 and not audit['missing_include_order']
    for name in ('SourceVerification','DocumentationVerification','FilePlacementVerification','SourceLabelsVerification'):
        assert read(name)['passed']
    tags=('ActionPolygonPreparation','ActionPolygonRowSelection','ActionPolygonLeftEdge',
          'ActionPolygonRightEdge','ActionPolygonRightShortStep')
    assert sum(read(tag+'Classification')['confirmed_code_bytes'] for tag in tags)==836
    assert all(read(tag+'Classification')['passed'] and read(tag+'Verification')['passed'] for tag in tags)
    heading='Подготовка и рёбра линейной заливки ACTION, 2026-11-04'
    for relative,prefix in (('README.md','Docs/'),('Docs/Validation.md',''),('Docs/ConformancePlan.md','')):
        path=ROOT/relative;text=path.read_text('utf-8')
        if '## '+heading in text:continue
        body=(f'\n## {heading}\n\n'
            f'Выделены пять частей [заливки граней]({prefix}ActionPolygonFill.md), сохранены 836 байтов и 529 инструкций. '
            'Подготовитель прошёл 3398 сценариев с точной RAM, обе цепочки 97090 сценариев с высотами 1..95, наклонами −255..255 и пропусками до 58 вершин. '
            'Общий выбор предела исчерпал 884736 сочетаний строк, короткий отрицательный хвост 65536 комбинаций AF. '
            'Для всех частей проверены регистры кроме R, значения и кратность записей. Зарегистрированы 35 писателей операндов, жёсткий порядок продолжения правой цепочки отмечен в include.\n\n'
            'Весь проект содержит 1241 фрагмент, описаны 1137, остаются 104 Unknown и 211 недоказанных договоров, включая 107 уже именованных. '
            'Статические проверки прошли, сверены 42546 инструкций, 4918 меток, 1668 физических диапазонов, 41 размещение и 479744 байта. '
            'Полный эталон временного стека и изменяемых операндов всего строкового ядра ещё не завершён. '
            'Последняя пользовательская сборка относится к прежнему срезу 128990 строк и не покрывает новые исходники. Codex сборку, IRQ и нативный запуск не выполнял. Полный проект ещё не завершён.\n')
        path.write_bytes((text.rstrip()+'\n'+body).encode('utf-8'))
    print(json.dumps(dict(passed=True,fragments=1241,code_bytes=836,instructions=529,whole_project_complete=False)))


if __name__=='__main__':main()
