                module Music
                module SetOrnamentPositionA
                ; Документация [музыкальные эффекты](../../Docs/MusicEffects.md)
                ; -----------------------------------------
                ; Чтение позиции орнамента канала A
                ; исходная запись 10, файловые смещения #0B52..#0B5C
                ; In:
                ;   DE указывает на байт позиции, входной F сохраняется
                ; Out:
                ;   HL сохранён, DE=входной DE+1, BC сохранён
                ;   AF содержит A=06 и входной F
                ;   HL', DE', BC', AF' сохранены
                ;   позиция записана в ожидающий операнд, код отложенной команды=06
                ;   R получает 6 M1, внешний CALL не включён
                ; Corrupt:
                ;   DE, AF только A, позиция и код отложенной команды, R
                ; Note:
                ;   байт позиции копируется без проверки длины сэмпла либо орнамента
                ;   индексные регистры, I, IM и IFF сохранены, SP увеличен на два обычным RET
                ; -----------------------------------------
                ; Чтение позиции орнамента канала A
Entry:          LD A, (DE)
                INC DE
                LD (@MusicChannelAState.OrnamentPos), A
                LD A, @MusicCommandConst.EnableDeferred
                LD (@MusicChannelAState.OrnamentCommand), A
                RET

                endmodule
                endmodule
