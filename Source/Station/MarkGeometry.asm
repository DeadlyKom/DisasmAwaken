                module Station
                module MarkGeometry
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
                ; Проверка входов [GeometryReturnEntriesVerification.json](../../Tools/Disasm/Reports/GeometryReturnEntriesVerification.json)
                ; -----------------------------------------
                ; Внутренний выход с удалением кадра попадания и запросом перестроения
                ; исходная запись 4, файловые смещения #6A11..#6A14
                ; In:
                ;   на SP находятся FGeometryHitFrame и за ним FPointerGuardFrame
                ; Out:
                ;   два слова попадания отброшены, результат соответствует FinishGeometry
                ;   SP увеличен на 16 относительно входа этого продолжения, включая внешний RET
                ;   R получает 14 M1 по модулю 128 с сохранением бита 7 при исходных инструкциях без IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, R и SP, EventEnabled
                ; Note:
                ;   собственных записей CPU-стека нет, кадры только читаются, единственная запись RAM обнуляет EventEnabled
                ;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
                ;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
                ;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
                ;   исходный переход к этому входу пока не найден, стековый договор проверен отдельной фикстурой
                ;   не делает самостоятельного изменения геометрии или рисунка, только помечает интерфейс
                ; -----------------------------------------
                ; внутренний вход, отбрасывание FGeometryHitFrame перед общим выполненным выходом
Entry:          POP BC
                POP BC
                JR @Station.FinishGeometry.Entry

                endmodule
                endmodule
