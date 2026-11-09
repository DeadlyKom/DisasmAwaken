                module Station
                module ScrollSecondaryRows
                ; Документация [второй список, общая печать, выбор и события LANG](../../Docs/SecondaryEquipmentRows.md)
                ; -----------------------------------------
                ; Подготовка прокрутки второго списка и сохранение начального индекса
                ; исходная запись 4, перенос STATIONF с 05CE в 6322, адреса 735F..7385
                ; In:
                ;   HL и BC контекст, IX выбранный элемент, окно и ввод по договорам XorRowIfSelected и ScrollWindowRows
                ;   SecondaryEquipmentState.Row и RowCount задают исходное слово полосы, TopRow содержит полный индекс
                ; Out:
                ;   HL, DE, BC, AF и альтернативные пары по результату ScrollWindowRows
                ;   Row=FF, RenderCall указывает на DrawSecondaryList.RenderRows, EndLimit=13, TopOffset=24
                ;   TopRow обновлён полным возвращённым HL, обычный возврат увеличивает SP на два
                ; Corrupt:
                ;   HL, DE, BC, AF, BC', AF', экран, прокрутка, указатель и контекст детей
                ; Note:
                ;   E исходной инверсии берётся из Row, а D из RowCount, подмена E значением 24 меняет оригинал
                ;   входы с недостаточной высотой проверены до полного возврата, штатный вызов не установлен
                ; -----------------------------------------
                ; чтение слова полосы из изменяемого операнда проверки рисователя
Entry:          LD DE, (@SecondaryEquipmentState.Row)
                LD A, (@SecondaryEquipmentState.Row)
                ; снятие прежней XOR-полосы при существующей строке
                CALL @Station.XorRowIfSelected.Entry
                ; обновление выбора на FF перед прокруткой
                LD A, #FF
                LD (@SecondaryEquipmentState.Row), A
                ; настройка внутреннего рисователя принятого индекса
                LD HL, @Station.DrawSecondaryList.RenderRows
                LD (@ScrollState.RenderCall), HL
                ; выбор верхнего индекса 13 для дополнительного набора
                LD HL, #000D
                LD (@ScrollState.EndLimit), HL
                ; выбор отступа 24 и исходного полного индекса
                LD A, #18
ReadTop:        LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                ; обновление начальной строки полным результатом прокрутки
                LD (@SecondaryEquipmentState.TopRow), HL
                RET

                endmodule
                endmodule
