                module Station
                module XorOutlineRow
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [временный XOR-контур](../../Docs/XorOutline.md)
; -----------------------------------------
; Инверсия видимой горизонтальной грани через изменяемый JR в развёртку 32 байтов
; исходная запись 4, файловые смещения #6566..#65F1
; In:
;   HL - адрес первого байта пиксельной строки, DE - E длина 1..32, D сохраняется
;   длина не пересекает правый край строки, BC сохраняется, код развёртки доступен для записи
; Out:
;   HL, DE и BC сохранены, A - последний инвертированный экранный байт
;   F=#12 OR (A AND #28), при длине больше одного S равен биту 7 младшего адреса последнего байта
;   HorizontalSkip=4*(32-E), только E байтов строки инвертированы
; Corrupt:
;   AF
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   JR выбирает один из 32 входов Bytes32..Bytes01, шаг одного блока четыре байта, последний блок без INC L
;   при E=1 последнего INC L нет, S берётся из расчёта пропуска #7C и равен нулю
;   Z,P/V,Carry нулевые на указанном диапазоне, H=N=1 от CPL
;   входы BytesNN являются внутренними продолжениями с уже сохранённым HL на стеке, обычный CALL к ним недопустим
; -----------------------------------------
                ; сохранение начала строки на CPU-стеке
Entry:          PUSH HL
                ; расчёт пропуска 4*(32-E) в развёртке горизонтальной грани
                LD A, #20
                SUB E
                ADD A, A
                ADD A, A
                ; самоподмена смещения JR, выбирающего ровно E завершающих блоков
                LD (@XorOutlineState.HorizontalSkip), A
                ; переход в один из внутренних Bytes32..Bytes01, сохранённый HL уже находится на стеке
                JR @Station.XorOutlineRow.Bytes32

                ; развёртка инвертирует байты через CPL, INC L задаёт S,Z,P/V следующего блока
Bytes32:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes31:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes30:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes29:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes28:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes27:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes26:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes25:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes24:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes23:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes22:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes21:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes20:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes19:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes18:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes17:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes16:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes15:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes14:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes13:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes12:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes11:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes10:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes09:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes08:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes07:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes06:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes05:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes04:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes03:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
Bytes02:        LD A, (HL)
                CPL
                LD (HL), A
                INC L
                ; последний байт строки без INC L, X/Y итогового F берутся из инвертированного байта
Bytes01:        LD A, (HL)
                CPL
                LD (HL), A
                ; возврат сохранённого начала строки без изменения итогового AF
                POP HL
                RET

                endmodule
                endmodule
