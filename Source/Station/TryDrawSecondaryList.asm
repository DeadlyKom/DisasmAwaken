                module Station
                module TryDrawSecondaryList
                ; Документация [второй список, общая печать, выбор и события LANG](../../Docs/SecondaryEquipmentRows.md)
                ; -----------------------------------------
                ; Проверка текущего слова поиска рисователя второго списка
                ; исходная запись 4, перенос STATIONF с 05CE в 6322, адреса 73D7..73DD
                ; In:
                ;   HL, BC контекст, DrawListState.HeadOperand задаёт читаемый список
                ;   DrawPointer читается как слово из операнда LD DE, его байты совпадают с Row и RowCount
                ; Out:
                ;   HL и BC сохранены, DE содержит прочитанный DrawPointer, AF по результату TestDrawPointer
                ;   при Z=0 выполнен RET NZ, при Z=1 исполнение продолжается в DrawSecondaryList
                ; Corrupt:
                ;   DE, AF на отказе, на продолжении действуют договоры рисователя
                ; Note:
                ;   начальное слово 73DE совпадает с DrawSecondaryList.Entry, после изменения строки и счётчика это может быть другой адрес
                ;   проверяется точное слово, обратной нормализации после перерисовки нет
                ; -----------------------------------------
                ; проверка точного текущего слова рисователя, операнд также хранит строку и счётчик
Entry:          LD DE, @Station.DrawSecondaryList.Entry
                CALL @Station.TestDrawPointer.Entry
                RET NZ                                                          ; выход, если текущий указатель отсутствует в списке

                ; JP @Station.DrawSecondaryList.Entry, продолжение в DrawSecondaryList.asm
                endmodule
                endmodule
