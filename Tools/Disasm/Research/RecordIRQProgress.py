"""Фиксация проверенного исследовательского среза IRQ и загрузчиков, без сборки."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3]
TITLE='Загрузчики, экранный поток и настоящее IM 1 в моделях вступления, 2026-11-04'


def main():
    audit=json.loads((ROOT/'Tools/Disasm/Reports/ConformanceAudit.json').read_text('utf-8'))
    inventory=json.loads((ROOT/'Tools/Disasm/Reports/Inventory.json').read_text('utf-8'))
    for stem in ('SourceVerification','SourceLabelsVerification','FilePlacementVerification','DocumentationVerification'):
        assert json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))['passed']
    plan=[]
    for relative in ('README.md','Docs/Validation.md','Docs/ConformancePlan.md'):
        path=ROOT/relative;before=path.read_bytes();text=before.decode('utf-8')
        assert '## '+TITLE not in text
        prefix='Docs/' if relative=='README.md' else ''
        capsule='\n## '+TITLE+'\n\n'
        capsule+='[Переносчики загрузчиков]('+prefix+'BootstrapRelocation.md) прошли 1024 сценария до передачи управления по 4000 и 4200, [остановка финала]('+prefix+'FinalHalt.md) 16384 сценария, включая запрет paging. [Полётный HR-декодер]('+prefix+'ActionUnpack.md) прошёл все 20 ресурсов в 80 вызовах и 27 переносах входа. Его 184 инструкции соответствуют станционной копии со сдвигом C24.\n\n'
        capsule+='[Экранный декодер вступления]('+prefix+'IntroScreen.md) получил независимую битовую грамматику и прошёл 1322 сценария, все группы длины и смещения, оба направления ссылок и расширения 1..255. Исходный экран 6912 байтов совпал полностью, сохранено оборачивание длины 256 в 1 при дальней ссылке. Необъяснённые 149 хвостовых байтов сохранены. [Табличный перенос]('+prefix+'IntroLookupTransfer.md) прошёл 768 сценариев с двумя реальными сгенерированными цепочками, граница проверки до входа 6BBC отмечена явно.\n\n'
        capsule+='В отличие от прежних локальных срезов без IRQ, новые модели исполняют настоящий 48K ROM-обработчик IM 1. [Ожидание кадра]('+prefix+'IntroWaitInterrupt.md) прошло 3072 сценария с точными FRAMES и стеком. [Вывод матрицы]('+prefix+'IntroPresentAttributes.md) прошёл 1536 сценариев, IFF остаётся единицей, писатель заканчивается до следующего IRQ в проверенном периоде. [Полный чередующийся кадр]('+prefix+'IntroInterlacedFrame.md) прошёл 3072 сценария, учтены один либо два IRQ в зависимости от разрешённого входного IFF и момента входа. [Продолжение текстурного кадра]('+prefix+'IntroLookupContinuation.md) прошло 3072 сценария с двумя сериями выборок, двумя обновлениями масштаба и двумя IRQ.\n\n'
        capsule+='Контролируемый профиль IRQ использует IY=5C3A, неактивные KSTATE, отсутствие клавиш и период 69888. Проверены регистры кроме R, RAM и кратность записей. Для кадровых композиций проверены все физические банки, для отдельного WaitInterrupt логическая RAM. Требование обязательного DI у писателя уточнено до отсутствия вмешательства IRQ во временный SP, синхронный вызов после HALT проверен отдельно. Для вложенного кадрового пути установлены 16 байтов временного CPU-стека. Нативный Unreal этим не заменяется.\n\n'
        capsule+='Срез содержит '+str(inventory['fragments'])+' фрагмента, описаны '+str(inventory['described'])+', остаётся '+str(inventory['unknown'])+' Unknown и '+str(audit['unknown_contract_fragments'])+' недоказанных контрактов, включая '+str(audit['named_fragments_without_proved_contract'])+' именованных. Неразобранные физические данные также остаются, завершённость по числу имён не заявляется. Сверены '+str(inventory['instructions'])+' инструкций, 5326 меток, 1706 диапазонов, 41 размещение и 479744 байта, общий граф и ссылки прошли статическую проверку. Последняя пользовательская сборка 128990 строк относится к прежним исходникам. Codex сборку и нативный запуск не выполнял. Полный проект ещё не завершён.\n'
        plan.append((path,before,(text+capsule).encode('utf-8')))
    # Проверка сохранности пользовательского текста перед добавлением нового среза.
    for path,before,_ in plan:assert path.read_bytes()==before
    for path,_,after in plan:path.write_bytes(after)
    print('README, Validation и ConformancePlan дополнены проверенным срезом IRQ')


if __name__=='__main__':main()
