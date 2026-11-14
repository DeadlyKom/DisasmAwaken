                module ArchiveStart
                module LoadEngine
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; загрузка ENGINE.C по #4000 после подтверждения в IRQ
                ; In:
                ;   TR-DOS доступен, селектор страниц настроен
                ; Out:
                ;   передача в #3D13 с ключом ENGINE, адресом #4000 и IM 1
                ;   верхнее слово стека равно #4000 для продолжения после ROM
                ; Corrupt:
                ;   HL, DE, BC, AF, SP и IM
                ; Note:
                ;   стек IRQ здесь сохраняется до первой инструкции самого ENGINE
                ; -----------------------------------------
                ; выбор страницы 0 и перенос ключа в буфер TR-DOS
Entry:          LD A, @ArchiveStartConst.PrimaryPage
                CALL @ArchiveStart.SelectPage.Dispatch
                LD HL, @ArchiveStartEngineKey.Value
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR

                ; подготовка адреса загрузки и переход в ПЗУ
                LD C, @TrDos.LoadFile
                LD A, @ArchiveStartConst.LoadByName
                LD HL, @ArchiveStartConst.EngineAddress
                PUSH HL
                IM 1
                JP @TrDos.Dispatch

                endmodule
                endmodule
