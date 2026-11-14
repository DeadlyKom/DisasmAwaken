                module ArchiveRun
                module CycleMemoryMode
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; переключение режима памяти и обновление подписи на двух экранах
                ; In:
                ;   отображён список Options, код памяти 0..2
                ; Out:
                ;   режим увеличен циклически, указатель подписи и видимые строки обновлены
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, отображение памяти
                ; -----------------------------------------
                ; стирание прежней подписи режима по её фиксированному адресу
Entry:          LD HL, @ArchiveRunConst.ModeCaption
                LD (@ArchiveRunState.Menu.Cursor), HL
                CALL @ArchiveRun.XorModeCaption.Entry

                ; увеличение режима и проверка замыкания цикла
                LD A, (@ArchiveRunMenus.Memory.Current)
                INC A
                LD HL, @ArchiveRunMenus.Memory.Count
                CP (HL)
                JR NZ, @ArchiveRun.CycleMemoryMode.StoreMode                    ; переход, если новый индекс ещё не равен числу режимов, сохранить его

                XOR A

                ; сохранение и вывод нового режима
StoreMode:      LD (@ArchiveRunMenus.Memory.Current), A
                CALL @ArchiveRun.XorModeCaption.Entry
                RET

                endmodule
                endmodule
