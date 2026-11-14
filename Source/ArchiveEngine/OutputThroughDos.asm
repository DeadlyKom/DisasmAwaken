                module ArchiveEngine
                module OutputThroughDos
                ; Документация [выбор страниц](../../Docs/ArchiveEnginePaging.md)
                ; -----------------------------------------
                ; отправка значения в порт из ROM TR-DOS
                ; In:
                ;   BC - порт, AF - A, отправляемый байт
                ; Out:
                ;   HL - адрес OUT (C), A в ROM, BC и AF сохранены
                ;   промежуточный RET из #3D2F снимает адрес инструкции OUT со стека
                ; Corrupt:
                ;   HL, временно выбирается дисковая ROM
                ; -----------------------------------------
                ; подготовка возврата из точки подстановки ROM к инструкции вывода
Entry:          LD HL, @ArchiveEngineConst.RomOutput
                PUSH HL
                JP @TrDosLegacy.RomReturn

                endmodule
                endmodule
