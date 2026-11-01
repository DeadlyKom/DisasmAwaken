                module Music
                module StageOrnamentA
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Применение отложенной позиции орнамента канала A
                ; исходная запись 10, файловые смещения #03AE..#03B8
                ; In:
                ;   HL, DE и C сохраняются, E=18 требуется для восстановления JR
                ;   B и AF сохраняются при выключенной команде, OrnamentCommand содержит 18 либо 06
                ;   OrnamentPos является подготовленным байтом позиции орнамента в доступном банке MUZ1
                ; Out:
                ;   граница блока находится по DEB9, собственного RET нет
                ;   при OrnamentCommand=06 OrnamentPos записан в OrnamentCursor, OrnamentCommand получает E, A=E, B=09
                ;   при OrnamentCommand=18 A и B сохранены, HL, DE, C и F сохранены во всех путях
                ;   альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы следующего блока
                ; Corrupt:
                ;   BC только B, AF только A, OrnamentCommand, OrnamentCursor, R
                ; Note:
                ;   исходный JR пропускает тело, код 06 включает LD B,09 с сохранением длины команды
                ;   значение позиции копируется без проверки длины орнамента, его последующий синтез проверяется отдельно
                ; -----------------------------------------
                ; изменяемый JR пропускает команду позиции орнамента, код 06 открывает её тело
Entry:          JR @Music.StageChannelBRow.Entry

                ; перенос ожидающей позиции орнамента в курсор синтеза канала A
                LD A, #00
                LD (@MusicChannelAState.OrnamentCursor), A
                ; выключение однократной команды позиции орнамента кодом JR из E
                LD A, E
                LD (@MusicChannelAState.OrnamentCommand), A
                ; JP @Music.StageChannelBRow.Entry, продолжение в UnknownDEB9.asm

                endmodule
                endmodule
