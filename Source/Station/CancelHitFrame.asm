                module Station
                module CancelHitFrame
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
                ; Проверка входов [GeometryReturnEntriesVerification.json](../../Tools/Disasm/Reports/GeometryReturnEntriesVerification.json)
                ; -----------------------------------------
                ; Удаление двух слов кадра попадания перед возвратом без изменения геометрии
                ; исходная запись 4, файловые смещения #6A15..#6A16
                ; In:
                ;   на SP находятся FGeometryHitFrame и за ним FPointerGuardFrame
                ; Out:
                ;   два слова попадания отброшены, исходный контекст возвращён через ReturnGeometry, Carry=0
                ;   SP увеличен на 16 относительно входа этого продолжения, включая внешний RET
                ;   R получает 10 M1 по модулю 128 с сохранением бита 7 при исходных инструкциях без IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, R и SP
                ; Note:
                ;   RAM и CPU-стек не записываются, кадры только читаются
                ;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
                ;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
                ;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
                ;   это внутреннее продолжение, обычный CALL без вложенного кадра недопустим
                ; -----------------------------------------
                ; отбрасывание FGeometryHitFrame перед возвратом без действия
Entry:          POP BC
                POP BC
                ; JP @Station.ReturnGeometry.Entry, продолжение в ReturnGeometry.asm

                endmodule
                endmodule
