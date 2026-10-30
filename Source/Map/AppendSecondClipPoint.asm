                module Map
                module AppendSecondClipPoint
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр](../../Docs/ClipTail.md)
; -----------------------------------------
; Добавление младших байтов второй точки либо пары из DE
; исходная запись 7, файловые смещения #1B42..#1B58
; In:
;   Entry читает младшие X,Y из MapClipWork.SecondPoint, старшие координат и ClipCodes игнорируются
;   FromDE принимает E=X, D=Y, MapClipWork.OutputSize задаёт байтовое смещение в странице MapClipState.Output
; Out:
;   Output[старый Size]=E, Output[(старый Size+1)&255]=D, OutputSize=(старый Size+2)&255
;   HL=F900|новый OutputSize, DE содержит записанную пару, BC сохранён
;   A=новый OutputSize, F соответствует последнему INC L, входной Carry сохраняется
;   альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE у Entry, AF
; Note:
;   проверки ёмкости и кодов отсечения нет, переход L=FF к 00 остаётся в той же странице F9
;   FromDE является самостоятельным публичным входом, углы используют именно его
; -----------------------------------------
                ; чтение младшего X второй точки для выхода без масштабирования
Entry:          LD A, (@MapClipWork.SecondPoint.X)
                LD E, A
                ; чтение младшего Y второй точки, старший байт намеренно не учитывается
                LD A, (@MapClipWork.SecondPoint.Y)
                LD D, A
                ; поиск адреса следующей двухбайтовой выходной записи по байтовому OutputSize
FromDE:         LD A, (@MapClipWork.OutputSize)
                LD L, A
                LD H, @MapClipConst.OutputPage
                ; запись X и Y с отдельным оборачиванием L внутри страницы F9
                LD (HL), E
                INC L
                LD (HL), D
                INC L
                ; расчёт следующего байтового размера после записи пары
                LD A, L
                ; обновление физического OutputSize, Carry не изменяется
                LD (@MapClipWork.OutputSize), A
                RET

                endmodule
                endmodule
