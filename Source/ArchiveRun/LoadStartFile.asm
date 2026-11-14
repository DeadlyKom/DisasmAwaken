                module ArchiveRun
                module LoadStartFile
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; сохранение режима памяти и передача управления загрузчику START.C
                ; In:
                ;   выбран режим памяти 0..2, TR-DOS доступен
                ; Out:
                ;   режим записан по #5F5E, IM 1, страница #10
                ;   ROM получает ключ START и адрес #6000, на стеке лежит адрес #6000
                ; Corrupt:
                ;   HL, DE, BC, AF, SP и IM
                ; -----------------------------------------
                ; замена стека меню и сохранение режима для следующего блока
Entry:          LD SP, @ArchiveRunConst.StackTop
                IM 1
                LD A, (@ArchiveRunMenus.Memory.Current)
                LD (@ArchiveRunConst.MemoryMode), A

                ; возврат к базовой конфигурации страниц и подготовка ключа
                LD A, @ArchiveRunConst.LoadPage
                LD BC, @Hardware.PagingPort
                OUT (C), A
                LD HL, @ArchiveRunFileKey.Start
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR

                ; подготовка адреса загрузки и продолжения, вход в TR-DOS
                LD HL, @ArchiveRun.RunMenu.Entry
                PUSH HL
                LD C, @TrDos.LoadFile
                LD A, @ArchiveRunConst.LoadByName
                JP @TrDos.Dispatch

                endmodule
                endmodule
