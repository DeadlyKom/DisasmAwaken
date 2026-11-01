                module Music
                module SetSamplePositionA
                ; Документация [музыкальные эффекты](../../Docs/MusicEffects.md)
                ; -----------------------------------------
                ; Чтение позиции сэмпла канала A
                ; исходная запись 10, файловые смещения #0B47..#0B51
                ; In:
                ;   DE указывает на байт позиции, входной F сохраняется
                ; Out:
                ;   HL и BC сохранены, DE=входной DE+1, F сохранён, альтернативные пары сохранены
                ;   A=06, позиция записана в ожидающий операнд, код отложенной команды=06
                ; Corrupt:
                ;   DE, AF только A, позиция и код отложенной команды, R
                ; Note:
                ;   байт позиции копируется без проверки длины сэмпла либо орнамента
                ;   индексные регистры, I, IM и IFF сохранены, SP увеличен на два обычным RET
                ; -----------------------------------------
                ; Чтение позиции сэмпла канала A
Entry:          LD A, (DE)
                INC DE
                LD (@MusicChannelAState.SamplePosition), A
                LD A, @MusicCommandConst.EnableDeferred
                LD (@MusicChannelAState.SampleCommand), A
                RET

                endmodule
                endmodule
