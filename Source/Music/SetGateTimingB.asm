                module Music
                module SetGateTimingB
                ; Документация [музыкальные эффекты](../../Docs/MusicEffects.md)
                ; -----------------------------------------
                ; Установка двух подготовленных длительностей чередования канала B
                ; исходная запись 10, файловые смещения #02F2..#02FF
                ; In:
                ;   DE указывает на вторую длительность, A содержит первую, F сохраняется
                ; Out:
                ;   HL и BC сохранены, DE=входной DE+1, A=06, F сохранён, альтернативные пары сохранены
                ;   EnabledTicks получает входную A, DisabledTicks получает байт потока, GateCommand=06
                ; Corrupt:
                ;   DE, AF только A, EnabledTicks, DisabledTicks, GateCommand, R
                ; Note:
                ;   нулевые длительности сохраняются без нормализации
                ;   индексные регистры, I, IM и IFF сохранены, SP увеличен на два обычным RET
                ; -----------------------------------------
                ; Установка двух подготовленных длительностей чередования канала B
Entry:          LD (@MusicChannelBState.EnabledTicks), A
                LD A, (DE)
                INC DE
                LD (@MusicChannelBState.DisabledTicks), A
                LD A, @MusicCommandConst.EnableDeferred
                LD (@MusicChannelBState.GateCommand), A
                RET

                endmodule
                endmodule
