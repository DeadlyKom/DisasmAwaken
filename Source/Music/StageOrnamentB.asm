                module Music
                module StageOrnamentB
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Применение отложенной позиции орнамента канала B
                ; исходная запись 10, файловые смещения #043C..#0446
                ; In:
                ;   HL, DE и C сохраняются, E=18 требуется для восстановления JR после отложенной команды
                ;   B и AF сохраняются при выключенной команде, переключатель содержит 18 либо 06
                ;   параметр команды подготовлен в доступном для записи банке MUZ1, прерывания запрещены согласно кадровому входу
                ; Out:
                ;   граница блока находится в StageEnvelopeAndNoise по DF47, собственного RET нет
                ;   при OrnamentCommand=06 OrnamentPos записан в OrnamentCursor, OrnamentCommand получает E, A=E, B=09
                ;   HL, DE, C и F сохранены, альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до следующего блока
                ;   при выключенной команде A и B сохранены, штатный E=18 выключает применённую команду восстановлением JR
                ; Corrupt:
                ;   BC только B, AF только A, OrnamentCommand, OrnamentCursor, R
                ; Note:
                ;   позиция орнамента копируется без проверки его заголовка, последующий синтез не входит в локальный договор
                ; -----------------------------------------
                ; изменяемый JR пропускает команду позиции орнамента B, код 06 открывает её тело
Entry:          JR @Music.StageEnvelopeAndNoise.Entry

                ; перенос ожидающей позиции орнамента в курсор синтеза канала B
                LD A, #00
                LD (@MusicChannelBState.OrnamentCursor), A
                ; выключение однократной команды позиции орнамента кодом JR из E
                LD A, E
                LD (@MusicChannelBState.OrnamentCommand), A
                ; JP @Music.StageEnvelopeAndNoise.Entry, продолжение в StageEnvelopeAndNoise.asm

                endmodule
                endmodule
