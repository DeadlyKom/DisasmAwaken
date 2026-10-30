                module Station
                module DrawInsetFrame
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Рисование рамки с заполненными верхней и нижней строками, внутренними скосами и пустой серединой
; исходная запись 4, файловые смещения #6436..#64BD
; In:
;   DE - D высота рамки в знакоместах 2..24, E полная ширина в байтах 2..32
;   BC - B знаковая строка знакомест, C знаковая байтовая колонка, рамка имеет горизонтальное пересечение с экраном
;   таблицы #82..#84 подготовлены загрузчиком, код писателя и CPU-стек доступны для записи и не перекрывают экран
; Out:
;   видимая часть рамки записана в bitmap #4000..#57FF, атрибуты не изменены
;   HL, DE, BC, AF и младший L' являются рабочим состоянием последнего выполненного участка, не возвращаемыми параметрами
; Corrupt:
;   HL, DE, BC, AF, HL', AF'
; Note:
;   верхнее знакоместо содержит одну сплошную строку, одну строку SetInsetPattern и шесть строк SetOutlineCopy
;   средние D-2 знакомест содержат по восемь строк SetOutlineCopy, нижнее шесть таких строк, затем SetInsetPattern и сплошную строку
;   отсечение выполняется по целым байтовым колонкам и строкам знакомест, внеэкранные строки не записываются
;   H', DE', BC', IX, IY, I и IFF сохраняются, SP восстанавливается обычным RET
;   меняются LeftCode, RightCode и SpanSkip, функция не реентерабельна
;   содержимое выходных рабочих регистров зависит от раннего выхода, их значения не являются отдельным результатом функции
;   недопустимые размеры, полное отсутствие горизонтального пересечения и вмешательство IRQ моделью не подтверждены
; -----------------------------------------
                ; расчёт внутренней ширины, два крайних байта остаются для боков рамки
Entry:          DEC E
                DEC E
                ; расчёт числа знакомест до нижней полосы рамки
                DEC D
                CALL @Station.PrepareFrameRaster.Entry
                ; расчёт смещения JR, пропускающего неиспользуемые пары записи средних байтов
                LD A, #1E
                SUB E
                ADD A, A
                ; настройка пропуска лишних средних байтов развёрнутого писателя строки
                LD (@StationRaster.SpanSkip), A
                ; сохранение счётчика высоты перед заменой DE байтовыми узорами
                LD B, D
                ; проверка видимости верхнего знакоместа рамки
                CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если строка рамки достигла нижней границы экрана

                JP M, @Station.DrawInsetFrame.Outline                           ; переход, если верхнее знакоместо находится выше экрана, его пиксели пропускаются

                ; рисование сплошной верхней пиксельной строки рамки
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; рисование следующей строки со скошенными внешними краями
                CALL @Station.SetInsetPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; сброс признака пропуска верхнего знакоместа перед рисованием его боков
                XOR A
                ; выбор боковых пикселей и пустой середины с учётом горизонтального отсечения
Outline:        CALL @Station.SetOutlineCopy.Entry
                JP M, @Station.DrawInsetFrame.MiddleCount                       ; переход, если верхнее знакоместо выше экрана, оставшиеся шесть строк не записываются

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; коррекция экранного адреса после восьми пиксельных строк верхнего знакоместа
                CALL @Station.NextCharRow.Entry
                ; расчёт числа средних знакомест без верхнего и нижнего
MiddleCount:    DEC B
                JR Z, @Station.DrawInsetFrame.BottomRow                         ; переход, если средних знакомест нет, остаётся нижняя полоса

                ; проверка видимости очередного среднего знакоместа рамки
MiddleRow:      CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если среднее знакоместо достигло нижней границы экрана

                JP M, @Station.DrawInsetFrame.NextMiddle                        ; переход, если среднее знакоместо выше экрана, его восемь строк пропускаются

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
NextMiddle:     DJNZ @Station.DrawInsetFrame.MiddleRow

                ; проверка видимости нижнего знакоместа рамки
BottomRow:      CALL @Station.AdvanceClipRow.Entry
                RET NC                                                          ; выход, если нижнее знакоместо достигло нижней границы экрана

                RET M                                                           ; выход, если нижнее знакоместо ещё выше экрана, вся рамка пропущена

                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                CALL @Station.DrawSpanRow.Entry
                ; завершение рамки скошенной предпоследней пиксельной строкой
                CALL @Station.SetInsetPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                ; замыкание рамки сплошной нижней пиксельной строкой
                CALL @Station.FillSpanPattern.Entry
                CALL @Station.DrawSpanRow.Entry
                RET

                endmodule
                endmodule
