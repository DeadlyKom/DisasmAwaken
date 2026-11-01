                module Station
                module SetupEnvironmentText
                ; Документация [два CR-списка, общий хвост значений, полный индекс и счётчик обработанных полей](../../Docs/SettingsRowPanels.md)
                ; -----------------------------------------
                ; Запрет переноса установок среды и выбор колонки значений X=66
                ; исходная запись 4, файловые смещения #0EAC..#0EB5
                ; In:
                ;   нет регистровых параметров, существующие операнды Style и Column2X доступны для записи
                ; Out:
                ;   HL, DE, BC сохранены, AF содержит A=66, F=44
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2
                ;   TextWindow.Style=0, TextStreamState.Column2X=66, экран, курсор и страница не меняются
                ; Corrupt:
                ;   AF, TextWindow.Style, TextStreamState.Column2X
                ; Note:
                ;   нулевой Style выбирает пропуск остатка подписи при отказе ширины, значение X задано в пикселях относительно окна
                ;   проверены все 65536 AF и все прежние байты обоих операндов
                ; -----------------------------------------
                ; отключение переноса подписей и выбор колонки значений среды X=66
Entry:          XOR A
                LD (@TextWindow.Style), A
                LD A, @SettingsRowConst.EnvColumn
                LD (@TextStreamState.Column2X), A
                RET

                endmodule
                endmodule
