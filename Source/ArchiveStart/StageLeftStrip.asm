                module ArchiveStart
                module StageLeftStrip
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; подготовка полосы левого маршрута в фиксированном буфере
                ; In:
                ;   левый маршрут скопирован, его указатели и число кадров доступны
                ; Out:
                ;   при свободном буфере индекс увеличен, перенесены 600 байтов, установлен флаг готовности
                ;   выбрана исходная рабочая страница меню
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение страниц
                ; Note:
                ;   перенос фиксированной длины может обернуться через #FFFF, это исходное поведение
                ; -----------------------------------------
                ; проверка готовности уже подготовленного буфера
Entry:          LD A, #00
                OR A
                RET NZ                                                          ; выход, если предыдущий буфер ещё ожидает вывода

                ; увеличение индекса кадра и проверка границы маршрута
                LD A, (@ArchiveStartRoutes.LeftIndex)
                INC A
                LD HL, @ArchiveStartRoutes.Left.FrameCount
                CP (HL)
                JR NZ, @ArchiveStart.StageLeftStrip.StoreIndex                  ; переход, если индекс не равен числу кадров, использовать его

                XOR A
StoreIndex:     LD (@ArchiveStartRoutes.LeftIndex), A

                ; чтение указателя полосы по индексу
                LD E, A
                LD D, #00
                LD HL, @ArchiveStartRoutes.Left.Staged00
                ADD HL, DE
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                PUSH HL

                ; выбор исходного BANK и копирование фиксированной длины
                LD A, (@ArchiveStartRoutes.Left.BankIndex)
                CALL @ArchiveStart.SelectBankIndex.Entry
                POP HL
                EX DE, HL
                LD DE, @ArchiveStartBuffers.Left
                LD BC, @ArchiveStartConst.StripBufferSize
                LDIR

                ; публикация готовности и возврат к странице меню
                LD A, #01
                LD (@ArchiveStart.StageLeftStrip.Entry + 1), A
                LD A, (@ArchiveStartData.Page.DefaultCode)
                CALL @ArchiveStart.SelectPage.Dispatch
                RET

                endmodule
                endmodule
