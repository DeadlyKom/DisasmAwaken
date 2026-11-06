"""Добавление текущего проверенного среза к истории проектной документации."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3]
TITLE='Объектный вывод, зеркальный 3DPART и контракты вступления, 2026-11-04'


def main():
    audit=json.loads((ROOT/'Tools/Disasm/Reports/ConformanceAudit.json').read_text('utf-8'))
    inventory=json.loads((ROOT/'Tools/Disasm/Reports/Inventory.json').read_text('utf-8'))
    for stem in ('SourceVerification','SourceLabelsVerification','FilePlacementVerification','DocumentationVerification'):
        assert json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))['passed']
    for relative in ('README.md','Docs/Validation.md','Docs/ConformancePlan.md'):
        path=ROOT/relative;text=path.read_text('utf-8')
        assert '## '+TITLE not in text
        prefix='Docs/' if relative=='README.md' else ''
        capsule='\n## '+TITLE+'\n\n'
        capsule+='Полные обработчики [внутренних записей]('+prefix+'ActionPacketRenderer.md) и [отсекаемых записей]('+prefix+'ActionClippedPacketRenderer.md) проверены на 1850 и 3906 композиционных сценариях. [Обёртка объекта]('+prefix+'ActionQueuedObject.md) прошла 1920 сценариев на всех 128 указателях исходных OBJECT3D. Проверены регистры кроме R, все банки RAM и кратность записей. Подготовительные дочерние процедуры в эталоне обёртки исполняются тем же Z80-кодом, независимое доказательство всей подготовки этим не заявляется.\n\n'
        capsule+='В [3DPART]('+prefix+'ThreeDOverlayMirror.md) доказано совпадение всех 8224 логических байтов с окном ACTION, секторный хвост 224 байта сохранён. Опубликованы 122 фрагмента, 121 с уточнённым контрактом, неоднозначный CF08 оставлен Unknown. Контракты требуют того же внешнего RAM-контекста и резидентных помощников, отдельный нативный запуск 3DPART не выполнен. [Очистка рабочего буфера]('+prefix+'ActionWorkBuffer.md) прошла 1536 сценариев с точными R и временем 18206 тактов без ожиданий и IRQ.\n\n'
        capsule+='Во вступлении уточнены [построитель атрибутов]('+prefix+'IntroAttributeWriter.md), [счётчики масштаба]('+prefix+'IntroTextureScale.md), [экранный перенос]('+prefix+'IntroScatter.md), [косвенный выборщик]('+prefix+'IntroPointerSampler.md) и [скользящий выборщик]('+prefix+'IntroScrolledSampler.md). Их модели прошли 1536, 10256, 1536, 2848 и 3840 сценариев соответственно. Проверены регистры кроме R, вся физическая RAM и кратность записей. Исправлена прежняя неверная трактовка вставки 00 14, она выполняет NOP и INC D, сдвигая приёмник. Во втором построении матрицы атрибутов используются следующие восемь исходных байтов.\n\n'
        capsule+='Текущий срез содержит '+str(inventory['fragments'])+' фрагмента, описаны '+str(inventory['described'])+', остаётся '+str(inventory['unknown'])+' Unknown и '+str(audit['unknown_contract_fragments'])+' недоказанных контрактов, включая '+str(audit['named_fragments_without_proved_contract'])+' уже именованных. Статически сверены '+str(inventory['instructions'])+' инструкций, 5326 меток, 1706 физических диапазонов, 41 размещение и 479744 байта. Общий граф, ссылки и размещение прошли проверку. Последняя пользовательская сборка относится к прежнему срезу 128990 строк, новые исходники ею не покрыты. Codex сборку, аппаратные IRQ и нативный запуск не выполнял. Полный смысловой разбор проекта ещё не завершён.\n'
        path.write_text(text+capsule,encoding='utf-8')
    print('Добавлен проверенный срез в README, Validation и ConformancePlan')


if __name__=='__main__':main()
