                module Music
                module StageGateAndSampleA
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Применение отложенных длительностей чередования и позиции сэмпла канала A
                ; исходная запись 10, файловые смещения #0390..#03AD
                ; In:
                ;   HL, DE и C сохраняются, E=18 требуется для восстановления JR после отложенной команды
                ;   B и AF могут сохраняться на пути без команд, оба переключателя содержат 18 либо 06
                ;   параметры EnabledTicks, DisabledTicks и SamplePosition подготовлены писателями команд в доступном банке MUZ1
                ; Out:
                ;   граница блока находится в StageOrnamentA по DEAE, собственного RET нет
                ;   при GateCommand=06 он получает E, EnabledTicks записан в GateEnabled и GateCounter, DisabledTicks в GateDisabled
                ;   при SampleCommand=06 SamplePosition записан в SampleCursor, SampleCommand получает E
                ;   при команде позиции A=E, B=09, иначе при команде длительности A=DisabledTicks, B=11
                ;   если обе команды выключены, A и B сохранены, HL, DE, C и F сохранены во всех путях
                ;   альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы следующего блока
                ; Corrupt:
                ;   BC только B, AF только A, GateCommand, GateEnabled, GateDisabled, GateCounter, SampleCommand, SampleCursor, R
                ; Note:
                ;   команды восстанавливают JR только при штатном E=18, это не обычные флаги данных
                ;   команда длительностей не меняет текущее разрешение канала DFEF, текущий счётчик всегда получает EnabledTicks
                ;   нулевые длительности и произвольная позиция сэмпла копируются без проверки его заголовка
                ; -----------------------------------------
                ; изменяемый JR пропускает команду длительностей, код 06 открывает её тело
Entry:          JR @Music.StageGateAndSampleA.ApplySample

                ; выключение однократной команды кодом JR из E
                LD A, E
                LD (@MusicChannelAState.GateCommand), A
                ; чтение длительности включённого состояния и запуск текущего счётчика тем же байтом
                LD A, #00
                LD (@MusicChannelAState.GateEnabled), A
                LD (@MusicChannelAState.GateCounter), A
                ; чтение длительности выключенного состояния для последующего чередования
                LD A, #00
                LD (@MusicChannelAState.GateDisabled), A
                ; изменяемый JR пропускает команду позиции сэмпла, код 06 открывает её тело
ApplySample:    JR @Music.StageOrnamentA.Entry

                ; перенос ожидающей позиции сэмпла в курсор синтеза канала A
                LD A, #00
                LD (@MusicChannelAState.SampleCursor), A
                ; выключение однократной команды позиции сэмпла кодом JR из E
                LD A, E
                LD (@MusicChannelAState.SampleCommand), A
                ; JP @Music.StageOrnamentA.Entry, продолжение в StageOrnamentA.asm

                endmodule
                endmodule
