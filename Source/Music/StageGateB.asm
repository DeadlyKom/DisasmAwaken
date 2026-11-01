                module Music
                module StageGateB
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Применение отложенных длительностей чередования канала B
                ; исходная запись 10, файловые смещения #041E..#0430
                ; In:
                ;   HL, DE и C сохраняются, E=18 требуется для восстановления JR после отложенной команды
                ;   B и AF сохраняются при выключенной команде, переключатель содержит 18 либо 06
                ;   параметр команды подготовлен в доступном для записи банке MUZ1, прерывания запрещены согласно кадровому входу
                ; Out:
                ;   граница блока находится в StageSampleB по DF31, собственного RET нет
                ;   при GateCommand=06 он получает E, EnabledTicks записан в GateEnabled и GateCounter, DisabledTicks в GateDisabled
                ;   при выполненной команде A=DisabledTicks, B=11
                ;   HL, DE, C и F сохранены, альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до следующего блока
                ;   при выключенной команде A и B сохранены, штатный E=18 выключает применённую команду восстановлением JR
                ; Corrupt:
                ;   BC только B, AF только A, GateCommand, GateEnabled, GateDisabled, GateCounter, R
                ; Note:
                ;   команда не меняет текущее разрешение канала E0EE, счётчик всегда запускается значением EnabledTicks
                ;   нулевые длительности копируются без нормализации, дальнейшее поведение задаёт DEC счётчика
                ; -----------------------------------------
                ; изменяемый JR пропускает команду длительностей B, код 06 открывает её тело
Entry:          JR @Music.StageSampleB.Entry

                ; выключение однократной команды длительностей кодом JR из E
                LD A, E
                LD (@MusicChannelBState.GateCommand), A
                ; перенос длительности включённого B в перезагрузку и текущий счётчик
                LD A, #00
                LD (@MusicChannelBState.GateEnabled), A
                LD (@MusicChannelBState.GateCounter), A
                ; перенос длительности выключенного B в отдельную перезагрузку
                LD A, #00
                LD (@MusicChannelBState.GateDisabled), A
                ; JP @Music.StageSampleB.Entry, продолжение в StageSampleB.asm

                endmodule
                endmodule
