                module Station
                module SetupGameSettingsText
                ; Документация [два CR-списка, общий хвост значений, полный индекс и счётчик обработанных полей](../../Docs/SettingsRowPanels.md)
                ; -----------------------------------------
                ; Запрет переноса установок игры и выбор колонки значений X=110
                ; исходная запись 4, файловые смещения #1918..#1921
                ; In:
                ;   нет регистровых параметров, существующие операнды Style и Column2X доступны для записи
                ; Out:
                ;   HL, DE, BC сохранены, AF содержит A=110, F=44
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2
                ;   TextWindow.Style=0, TextStreamState.Column2X=110, экран, курсор и страница не меняются
                ; Corrupt:
                ;   AF, TextWindow.Style, TextStreamState.Column2X
                ; Note:
                ;   нулевой Style выбирает пропуск остатка подписи при отказе ширины, значение X задано в пикселях относительно окна
                ;   проверены все 65536 AF и все прежние байты обоих операндов
                ; -----------------------------------------
                ; отключение переноса и выбор колонки игровых значений X=110
Entry:          XOR A
                LD (@TextWindow.Style), A
                LD A, @SettingsRowConst.GameColumn
                LD (@TextStreamState.Column2X), A
                RET

                endmodule
                endmodule
