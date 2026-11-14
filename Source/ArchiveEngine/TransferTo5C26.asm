                module ArchiveEngine
                module TransferTo5C26
                ; Документация [отдельный переход](../../Docs/ArchiveEngineAnimation.md#отдельный-переход-по-40a9)
                ; -----------------------------------------
                ; выбор страницы 0 и передача управления по #5C26
                ; In:
                ;   операнд SelectPage.Dispatch настроен
                ; Out:
                ;   PC - #5C26, страница 0 выбрана, исходные SP и IFF сохранены
                ; Corrupt:
                ;   AF, банковое окно до передачи управления
                ; Note:
                ;   #5C26 занимает часть STRMS в обычной среде BASIC, для осмысленного исполнения нужен иной контекст
                ;   вызывающий путь и требуемое содержимое #5C26 пока не установлены
                ; -----------------------------------------
Entry:          LD A, @ArchiveEngineConst.BarPage
                CALL @ArchiveEngine.SelectPage.Entry
                JP #5C26

                endmodule
                endmodule
