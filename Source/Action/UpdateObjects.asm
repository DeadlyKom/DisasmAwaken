                module Action
                module UpdateObjects
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
                ; Документация [обход записей](../../Docs/ActionObjectWalk.md)
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний
; исходная запись 17, файловые смещения #9729..#9791
; In:
;   Entry не принимает числовых аргументов, доступен список FActionRecord от #A100 с маркером #80,#80
;   вход #F735 принимает IX предыдущей записи, в окне #C000 выбран банк 0, IRQ не вмешиваются
;   состояния активных записей выбирают допустимые входы таблицы обработчиков
;   каждый выбранный обработчик обязан вернуть управление по рамке DispatchObjectState либо выполнить свой выход из режима
; Out:
;   при маркере IX указывает на маркер, AF=#8042, DE=#0040, SP увеличен на 2 при RET
;   остальные регистры содержат результат последнего обработчика и PrepareRecordScale, при пустом списке сохраняют входные значения
;   на активной записи IX передаётся выбранному обработчику, поле #13 и поля ветки класса #12 обновляются до передачи
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R по выбранным обработчикам
;   поля активных записей, рабочие операнды, эффекты, очередь, paging и временный стек по дочерним договорам
; Note:
;   1024 полных прохода проверили списки до 25 записей с настоящими обработчиками трёх фаз
;   прочие обработчики имеют отдельные договоры, их произвольные совместные состояния и нативный игровой проход не исчерпаны
; -----------------------------------------
Entry:          LD IX, @ActionObjectRecords.Record00 - @FActionRecord
                JR @Action.UpdateObjects.NextRecord


                ; Проверка первого байта записи с кодом доступности во втором байте.
CheckEnd:       LD A, (IX + @FActionRecord.Components.Component0.Low)
                CP #80
                RET Z                                                           ; выход, если оба первых байта записи равны #80

                ; Продвижение к следующей записи и проверка её второго байта.
NextRecord:     LD DE, #0040
                ADD IX, DE
                LD A, (IX + @FActionRecord.Components.Component0.High)
                CP #80
                JP Z, @Action.UpdateObjects.CheckEnd                            ; переход, если второй байт равен #80, проверить конец списка


                LD A, (IX + @FActionRecord.ClassCode)
                CP #10
                JP NC, @Action.UpdateObjects.CheckLinks                         ; переход, если класс не меньше 16, поле #13 не изменять


                LD A, (IX + @FActionRecord.Unknown22)
                DEC A
                LD H, A
                LD A, (IX + @FActionRecord.Unknown13)
                CP H
                JR NC, @Action.UpdateObjects.CheckLinks                         ; переход, если поле #13 не меньше уменьшенного порога


                INC A
                LD (IX + @FActionRecord.Unknown13), A
                ; Выбор пути по байту LinkFlags и классу записи.
CheckLinks:     LD A, (IX + @FActionRecord.LinkFlags)
                AND A
                JP Z, @Action.DispatchObjectState.CallHandler                   ; переход, если LinkFlags равен нулю, вызвать текущий обработчик


                BIT 1, A
                JP NZ, @Action.DispatchObjectState.Entry                        ; переход, если бит 1 LinkFlags установлен, выбрать состояние


                LD A, (IX + @FActionRecord.ClassCode)
                CP #12
                JR NZ, @Action.CheckRecordEffectThreshold.Entry                 ; переход, если класс отличается от #12, проверить порог эффекта


                LD A, (IX + @FActionRecord.LinkedIndex)
                LD (IX + @FActionRecord.Unknown0D), A
                CALL @Action.CountClass3LinksUpToTwo.Entry
                ; Проверка числа совпадающих связей класса 3 после возврата из счётчика.
                JP NC, @Action.DispatchObjectState.CallHandler                  ; переход, если найдены две связи, сохранить текущее состояние

                ; Установка состояния и начальной фазы при числе связей меньше двух.
                LD (IX + @FActionRecord.StateCode), #0B
                LD A, R
                AND #01
                ADD A, #02
                LD (IX + @FActionRecord.SavedStateCode), A
                ; Применение прямой поправки 8 при сохранённом индексе #1A.
                LD A, (IX + @FActionRecord.Unknown0D)
                CP #1A
                LD C, #08
                CALL Z, @Action.ApplyIndexedDelta.AdjustMode                    ; вызов, если сохранённый индекс равен #1A, применить поправку

                JP @Action.DispatchObjectState.CallHandler

                endmodule
                endmodule
