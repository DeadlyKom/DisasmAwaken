                module Action
                module AppendBottomLeftClipCorner
                ; Документация [алгоритм и проверка](../../Docs/ActionClipPointWriters.md)
                ; -----------------------------------------
                ; Добавление угла окна при нулевом CornerBlock
                ; исходная запись 17, банковое окно ACTION банка 0, смещения #6657..#6661
                ; In:
                ;   CornerBlock по CF03 задаёт запрет вывода углов, любой ненулевой байт подавляет запись
                ;   OutputSize задаёт байтовое смещение в странице 90, на CPU-стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   при CornerBlock!=0 HL, DE и BC сохраняются, A=CornerBlock, F от AND A, RAM не записывается
                ;   при CornerBlock=0 DE=5F00, через AppendSecondClipPoint.StorePair добавлены два байта фиксированного угла
                ;   на пути записи HL=9000 OR новый OutputSize, A=новый OutputSize, F от последнего INC L с Carry=0
                ;   BC, весь альтернативный набор, IX, IY, I, IM, IFF и paging сохраняются, SP после RET равен входному SP+2
                ;   R увеличивается на 3 при запрете либо на 15 при записи, дополнительный CPU-стек не используется
                ; Corrupt:
                ;   AF и R, при разрешённой записи также HL, DE, два байта пары и OutputSize
                ; Note:
                ;   общий вход использует JP, внешний возврат остаётся для общего RET
                ;   65536 сценариев проверяют все сочетания CornerBlock и OutputSize, точные регистры, флаги, R, всю RAM и кратность записей
                ;   IRQ, сборка и нативный вывод не проверены
                ; -----------------------------------------
                ; -----------------------------------------
                ; Проверка запрета углов
                ; Чтение полного CornerBlock, проверяется весь байт, а не отдельный бит.
Entry:          LD A, (@ActionClipPointWritersState.CornerBlock)
                AND A
                RET NZ                                                          ; выход, если CornerBlock ненулевой, угловую точку не записывать

                ; Подготовка исходной фиксированной пары угла в DE и переход к общей записи без CALL.
                LD DE, @ActionClipCornerConst.BottomLeft
                JP @Action.AppendSecondClipPoint.StorePair

                endmodule
                endmodule
