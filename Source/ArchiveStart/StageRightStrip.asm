                module ArchiveStart
                module StageRightStrip
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; подготовка полосы правого маршрута в фиксированном буфере
                ; In:
                ;   правый маршрут скопирован, его указатели и число кадров доступны
                ; Out:
                ;   при свободном буфере индекс увеличен, перенесены 600 байтов, установлен флаг готовности
                ;   выбрана исходная рабочая страница меню
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение страниц
                ; -----------------------------------------
                ; проверка готовности уже подготовленного буфера
Entry:          LD A, #00
                OR A
                RET NZ                                                          ; выход, если предыдущий буфер ещё ожидает вывода

                ; увеличение индекса кадра и проверка границы маршрута
                LD A, (@ArchiveStartRoutes.RightIndex)
                INC A
                LD HL, @ArchiveStartRoutes.Right.FrameCount
                CP (HL)
                JR NZ, @ArchiveStart.StageRightStrip.StoreIndex                 ; переход, если индекс не равен числу кадров, использовать его

                XOR A
StoreIndex:     LD (@ArchiveStartRoutes.RightIndex), A

                ; чтение указателя полосы по индексу
                LD E, A
                LD D, #00
                LD HL, @ArchiveStartRoutes.Right.Staged00
                ADD HL, DE
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                PUSH HL

                ; выбор исходного BANK и копирование фиксированной длины
                LD A, (@ArchiveStartRoutes.Right.BankIndex)
                CALL @ArchiveStart.SelectBankIndex.Entry
                POP HL
                EX DE, HL
                LD DE, @ArchiveStartBuffers.Right
                LD BC, @ArchiveStartConst.StripBufferSize
                LDIR

                ; публикация готовности и возврат к странице меню
                LD A, #01
                LD (@ArchiveStart.StageRightStrip.Entry + 1), A
                LD A, (@ArchiveStartData.Page.DefaultCode)
                CALL @ArchiveStart.SelectPage.Dispatch
                RET

                endmodule
                endmodule
