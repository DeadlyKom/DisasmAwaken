                module Station
                module ReturnGeometry
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
                ; Проверка входов [GeometryReturnEntriesVerification.json](../../Tools/Disasm/Reports/GeometryReturnEntriesVerification.json)
                ; -----------------------------------------
                ; Возврат исходных регистров и исходного A с очисткой Carry через AND A
                ; исходная запись 4, файловые смещения #6A17..#6A1E
                ; In:
                ;   SP указывает на ранее созданный FPointerGuardFrame без вложенных слов
                ; Out:
                ;   HL, DE и BC восстановлены, AF - A из кадра, F=AND_flags(исходный A) и Carry=0, IX восстановлен
                ;   SP увеличен на 12 относительно входа этого продолжения, включая внешний RET
                ;   R получает 8 M1 по модулю 128 с сохранением бита 7 при исходных инструкциях без IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, R и SP
                ; Note:
                ;   RAM и CPU-стек не записываются, кадры только читаются
                ;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
                ;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
                ;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
                ;   байт A сохраняется, но исходные флаги не восстанавливаются побитно из-за завершающего AND A
                ; -----------------------------------------
                ; снятие базового FPointerGuardFrame, исходный A возвращается отдельно от исходных флагов
Entry:          POP BC
                POP DE
                POP HL
                POP AF
                POP IX
                ; очистка Carry и расчёт S,Z,P/V по восстановленному исходному A
                AND A
                RET

                endmodule
                endmodule
