                module ArchiveEngine
                module CopyViewportRows
                ; Документация [полный фон кадра](../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; -----------------------------------------
                ; перенос полных 32-байтовых строк в пределах одной группы растра
                ; In:
                ;   HL - начало исходной строки, DE - адрес нижней строки назначения
                ;   AF - A, число строк, штатные вызовы передают 7 или 8
                ;   AdvanceSource содержит пропуск до следующей строки источника
                ; Out:
                ;   HL - первая строка за прочитанным блоком, DE - адрес после уменьшения D на число строк
                ;   BC - пропуск источника, A - 0
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; Note:
                ;   при исходном A=0 выполняются 256 строк, границы группы задаёт вызывающий код
                ; -----------------------------------------
                ; развёрнутый перенос 32 байтов без внутреннего счётчика
Entry:          PUSH DE
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI

                ; переход к соседней строке экрана и следующей строке источника
                POP DE
                DEC D
AdvanceSource:  LD BC, #0000                                                    ; исходное значение, PrepareScenePages записывает 60
                ADD HL, BC
                DEC A
                JR NZ, @ArchiveEngine.CopyViewportRows.Entry                    ; переход, если остались строки в текущей группе

                RET

                endmodule
                endmodule
