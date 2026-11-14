                module Station
                module FinishGeometry
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
                ; Проверка входов [GeometryReturnEntriesVerification.json](../../Tools/Disasm/Reports/GeometryReturnEntriesVerification.json)
                ; -----------------------------------------
                ; Запрос перестроения и возврат исходного контекста с Carry после изменения геометрии
                ; исходная запись 4, файловые смещения #6A04..#6A10
                ; In:
                ;   SP указывает на ранее созданный FPointerGuardFrame, вложенных слов поверх него уже нет
                ; Out:
                ;   HL, DE и BC восстановлены из кадра, AF - A из кадра и F=(AND_flags(A) AND #C4) OR (A AND #28) OR 1, IX восстановлен
                ;   InterfaceState.EventEnabled=0, SP после RET соответствует исходному вызову
                ;   SP увеличен на 12 относительно входа этого продолжения, включая внешний RET
                ;   R получает 11 M1 по модулю 128 с сохранением бита 7 при исходных инструкциях без IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, R и SP, EventEnabled
                ; Note:
                ;   собственных записей CPU-стека нет, кадры только читаются, единственная запись RAM обнуляет EventEnabled
                ;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
                ;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
                ;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
                ;   Entry является общим хвостом, отдельный CALL без кадра недопустим
                ; -----------------------------------------
                ; запрос перестроения интерфейса, указатель пока остаётся запрещённым
Entry:          XOR A
                LD (@InterfaceState.EventEnabled), A
                ; снятие базового FPointerGuardFrame с восстановлением исходных регистров
                POP BC
                POP DE
                POP HL
                POP AF
                POP IX
                ; восстановление признаков по исходному A и установка Carry выполненного действия
                AND A
                SCF
                RET

                endmodule
                endmodule
