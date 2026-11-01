                module Music
                module ReadGateTimingB
                ; Документация [музыкальные эффекты](../../Docs/MusicEffects.md)
                ; -----------------------------------------
                ; Чтение двух длительностей чередования канала B
                ; исходная запись 10, файловые смещения #02EA..#02ED
                ; In:
                ;   DE указывает на две длительности, входной F сохраняется
                ; Out:
                ;   HL и BC сохранены, DE=входной DE+2, A=06, F сохранён, альтернативные пары сохранены
                ;   EnabledTicks и DisabledTicks обновлены, GateCommand=06
                ; Corrupt:
                ;   DE, AF только A, EnabledTicks, DisabledTicks, GateCommand, R
                ; Note:
                ;   первый байт читается здесь, JR передаёт управление в SetGateTimingB по DDF2
                ;   индексные регистры, I, IM и IFF сохранены, SP увеличен на два обычным RET
                ; -----------------------------------------
                ; Чтение двух длительностей чередования канала B
Entry:          LD A, (DE)
                INC DE
                JR @Music.SetGateTimingB.Entry

                endmodule
                endmodule
