                module ArchiveStart
                module LoadChooseScreen
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; загрузка экранного файла и одноцветная настройка атрибутов
                ; In:
                ;   HL - девятибайтовый ключ choose1 или choose2, нужная экранная страница выбрана
                ; Out:
                ;   при успешном чтении растр загружен по #C000, 768 атрибутов равны #07
                ; Corrupt:
                ;   HL, DE, BC, AF, дополнительно состояние TR-DOS согласно ПЗУ
                ; Note:
                ;   запись атрибутов следует и после возврата ошибки чтения
                ; -----------------------------------------
                ; перенос ключа и чтение экранного файла по #C000
Entry:          LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, @ArchiveStartConst.Window
                LD A, @ArchiveStartConst.LoadByName
                LD C, @TrDos.LoadFile
                CALL @TrDos.Dispatch

                ; заполнение атрибутов без записи пиксельной области
                LD HL, @ArchiveStartConst.FirstAttributes
                LD DE, @ArchiveStartConst.NextAttribute
                LD (HL), @ArchiveStartConst.BlankAttribute
                LD BC, @ArchiveStartConst.AttributeTail
                LDIR
                RET

                endmodule
                endmodule
