                module Station
                module DrawFrameType
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [внутренний контур рамки](../../Docs/StationSpans.md)
; -----------------------------------------
; Выбор скосов либо внутреннего контура рамки по биту 0 типа
; исходная запись 4, файловые смещения #63A4..#6435
; In:
;   DE - D высота в знакоместах 2..24, E полная ширина 2..32 байта
;   BC - B знаковая строка знакомест, C знаковая байтовая колонка с горизонтальным пересечением экрана
;   AF - бит 0 A выбирает контур, таблицы адресации #82..#84 подготовлены, писатель и стек доступны для записи
; Out:
;   видимый bitmap рамки записан без изменения атрибутов
;   HL, DE, BC, AF и младший L' являются рабочим состоянием последнего выполненного участка
; Corrupt:
;   HL, DE, BC, AF, HL', AF'
; Note:
;   схема байта типа 7..0 равна xxxxxxxT, только T выбирает алгоритм, остальные биты здесь не проверяются
;   T=0 передаёт управление DrawInsetFrame, T=1 выбирает внутренний контур
;   внутренний контур имеет две заполненные верхние строки, SetDeepInset и пять строк SetInnerOutline
;   середина состоит из полных знакомест SetInnerOutline, низ содержит пять таких строк, SetDeepInset и две заполненные строки
;   H', DE', BC', IX, IY, I и IFF сохраняются, SP восстанавливается
;   меняются LeftCode, RightCode и SpanSkip, реентерабельность не обеспечивается
;   нет подтверждения недопустимых размеров, отсутствия горизонтального пересечения и вмешательства IRQ
; -----------------------------------------
                ; выбор контура по исходному биту 0 A через Carry после RRA
Entry:          RRA
                JP NC, @Station.DrawInsetFrame.Entry                            ; переход, если бит 0 типа сброшен, используется исходная рамка со скосами

                ; расчёт внутренней ширины без двух крайних байтов
                DEC E
                DEC E
                ; расчёт числа знакомест до нижней полосы
                DEC D
                CALL @Station.PrepareFrameRaster.Entry
                ; расчёт смещения пропуска неиспользуемых средних байтов писателя
                LD A, #1E
                SUB E
                ADD A, A
                ; изменение операнда SpanSkip под отсечённую внутреннюю ширину
                LD (@StationRaster.SpanSkip), A
                LD B, D
                ; проверка видимости верхнего знакоместа внутреннего контура
                CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если верхнее знакоместо уже ниже экрана

                JP M, @Station.DrawFrameType.TopSide                            ; переход, если верхнее знакоместо выше экрана, первые три строки не записываются

                ; начало двух сплошных верхних пиксельных строк
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; выбор заполненных краёв с тремя внешними пропусками для третьей строки
                CALL @Station.SetDeepInset.Entry
                CALL @Station.DrawSpanRow.Entry
                ; сброс Sign перед оставшимися строками видимого верхнего знакоместа
                XOR A
                ; выбор боковых пикселей внутреннего контура для остальных строк
TopSide:        CALL @Station.SetInnerOutline.Entry
                JP M, @Station.DrawFrameType.AfterTop                           ; переход, если верхнее знакоместо выше экрана, оставшиеся пять строк пропускаются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; коррекция экранного адреса после верхнего знакоместа
                CALL @Station.NextCharRow.Entry
                ; проверка числа средних знакомест перед нижней полосой
AfterTop:       DEC B
                JR Z, @Station.DrawFrameType.Bottom                             ; переход, если средних знакомест нет, начать нижнюю полосу

                ; проверка видимости очередного среднего знакоместа
Middle:         CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если среднее знакоместо достигло нижней границы экрана

                JP M, @Station.DrawFrameType.AfterMiddle                        ; переход, если среднее знакоместо выше экрана, его восемь строк пропускаются

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
AfterMiddle:    DJNZ @Station.DrawFrameType.Middle

                ; проверка видимости нижнего знакоместа рамки
Bottom:         CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если нижнее знакоместо ниже экрана

                RET M                                                           ; выход, если нижнее знакоместо ещё выше экрана

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; замыкание внутреннего контура заполненной строкой с тремя внешними пропусками
                CALL @Station.SetDeepInset.Entry
                CALL @Station.DrawSpanRow.Entry
                ; две сплошные нижние строки рамки
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                RET

                endmodule
                endmodule
