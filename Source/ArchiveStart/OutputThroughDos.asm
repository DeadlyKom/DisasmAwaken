                module ArchiveStart
                module OutputThroughDos
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; передача записи порта команде OUT в ROM TR-DOS
                ; In:
                ;   BC - порт, AF - A, отправляемое значение
                ; Out:
                ;   HL - #2A53, OUT выполняется с заданными BC и A
                ; Corrupt:
                ;   HL, временно выбирается ROM TR-DOS
                ; -----------------------------------------
                ; подстановка адреса вывода для возврата из #3D2F
Entry:          LD HL, @ArchiveEngineConst.RomOutput
                PUSH HL
                JP @TrDosLegacy.RomReturn

                endmodule
                endmodule
