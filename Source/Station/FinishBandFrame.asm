                module Station
                module FinishBandFrame
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Продолжение верхней полосы, средние строки и замыкание нижнего края рамки
; исходная запись 4, файловые смещения #60C9..#6164
; In:
;   продолжение DrawBandFrame после подготовки таблиц, ширины и кодов краёв
;   HL - адрес после трёх верхних пиксельных строк либо начальный адрес при пропуске верхнего знакоместа
;   BC - B число средних знакомест, AF - Sign означает пропуск невидимого верхнего знакоместа
;   HL' - L' текущая знаковая строка, AF' содержит условия горизонтального отсечения
;   StationRaster.BandPattern указывает SetOutlinePattern либо SetCutoutPattern, SpanSkip и коды краёв уже настроены
;   шесть изменяемых слов рамки задают обычный либо заполненный режим из StationSpans.md
; Out:
;   завершены верхняя полоса и видимая часть остальной рамки, атрибуты не изменены
;   HL, DE, BC, AF и L' содержат рабочее состояние последнего участка
; Corrupt:
;   HL, DE, BC, AF, HL', AF'
; Note:
;   вход зависит от последовательного исполнения DrawBandFrame, не является самостоятельным рисователем с геометрическими параметрами
;   пять строк завершают верхнее знакоместо, затем восемь строк образуют полосу с разделителем
;   B средних знакомест рисуются по восемь строк, после них выводится нижнее знакоместо
;   после каждого AdvanceClipRow Carry=0 завершает рамку снизу, Sign=1 пропускает текущую строку знакомест сверху
;   H', DE', BC', IX, IY, I и IFF сохраняются, RET использует адрес возврата исходного вызова DrawBandFrame
;   выбранный установщик в первом CALL задаётся изменяемым словом BandPattern
;   шесть изменяемых операндов имеют обычный набор ResetBandMode либо заполненный набор SetBandFillMode
;   в заполненном режиме строки 3..10 всегда SetCutoutPattern, строки 12 и 13..15 и середина также заполнены
;   нижнее знакоместо заполненного режима содержит пять строк SetCutoutPattern, одну фиксированную SetOutlinePattern, SetSixBitPattern и ClearSpanPattern
;   строки 2,11 и третья снизу сохраняют обычный боковой узор, их фиксированные вызовы не подменяются
; -----------------------------------------
                ; выбор изменяемого узора, адрес первого CALL задаёт StationRaster.BandPattern
Entry:          CALL @Station.SetOutlinePattern.Entry
                JP M, @Station.FinishBandFrame.SeparatorRow                     ; переход, если верхнее знакоместо выше экрана, оставшиеся пять строк пропускаются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; коррекция адреса после восьми пиксельных строк верхнего знакоместа
                CALL @Station.NextCharRow.Entry
                ; проверка видимости второго знакоместа с горизонтальным разделителем
SeparatorRow:   CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если знакоместо разделителя достигло нижней границы экрана

                JP M, @Station.FinishBandFrame.SeparatorSides                   ; переход, если знакоместо разделителя выше экрана, первые пять его строк пропускаются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; выбор текущего установщика строки 11 через изменяемый операнд BandLine11
                CALL @Station.SetOutlinePattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; выбор разделителя строки 12 через BandLine12, обычный режим очищает его, заполненный рисует SetCutoutPattern
                CALL @Station.ClearSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; сброс Sign перед тремя видимыми строками после разделителя
                XOR A
                ; выбор бокового узора после разделителя через изменяемый операнд BandSides
SeparatorSides: CALL @Station.SetOutlinePattern.Entry
                JP M, @Station.FinishBandFrame.MiddleCount                      ; переход, если знакоместо разделителя выше экрана, последние три строки пропускаются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; коррекция адреса после восьми строк знакоместа разделителя
                CALL @Station.NextCharRow.Entry
                ; проверка наличия средних знакомест между полосой и нижним краем
MiddleCount:    LD A, B
                AND A
                JR Z, @Station.FinishBandFrame.BottomRow                        ; переход, если средних знакомест нет, остаётся нижний край

                ; проверка видимости очередного среднего знакоместа
MiddleRow:      CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если среднее знакоместо достигло нижней границы экрана

                JP M, @Station.FinishBandFrame.NextMiddle                       ; переход, если среднее знакоместо выше экрана, все восемь строк пропускаются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; коррекция адреса после восьми строк среднего знакоместа
                CALL @Station.NextCharRow.Entry
NextMiddle:     DJNZ @Station.FinishBandFrame.MiddleRow

                ; проверка видимости нижнего знакоместа рамки
BottomRow:      CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если нижнее знакоместо достигло нижней границы экрана

                RET M                                                           ; выход, если нижнее знакоместо ещё выше экрана, вся рамка пропущена

                ; выбор первой строки нижнего знакоместа через BandBottom0
                CALL @Station.ClearSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; выбор узора следующих четырёх строк нижнего знакоместа через BandBottom1
                CALL @Station.SetOutlinePattern.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; возврат к фиксированному обычному контуру перед нижней фаской, даже в заполненном режиме
                CALL @Station.SetOutlinePattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; рисование шести средних пикселей в предпоследней строке рамки
                CALL @Station.SetSixBitPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; обнуление последней пиксельной строки рамки
                CALL @Station.ClearSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                RET

                endmodule
                endmodule
