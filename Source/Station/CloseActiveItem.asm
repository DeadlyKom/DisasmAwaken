                module Station
                module CloseActiveItem
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [закрытие и callback активного элемента](../../Docs/ActiveItem.md)
; -----------------------------------------
; Закрытие активного элемента, перенос в конец списка и вызов завершающего callback
; исходная запись 4, файловые смещения #3E77..#3E96
; In:
;   ActiveItemState.Active=0 означает отсутствие активного элемента, ненулевой байт разрешает закрытие
;   при активности HL используется как новая обёртка только если MoveItemToTail не найдёт ActiveItemState.Index
;   активный индекс и таблицы удовлетворяют MoveItemToTail и ToggleItemFrame, HALT получает корректное пробуждение
;   ActiveItemState.Callback содержит возвращающийся по CPU-стеку callback, сохраняющий стек и доступность кода закрытия
; Out:
;   при отсутствии активности AF=#0054, все остальные основные, альтернативные и индексные регистры сохранены
;   при активности HL и DE восстановлены поверх результата callback, BC и прочие регистры остаются от callback
;   при активности A от callback, F=(F_callback AND #C4) OR (A_callback AND #28) OR 1
;   активность сброшена до callback, его адрес после возврата заменён EmptyCallback
; Corrupt:
;   при активности BC, AF, HL', DE', BC', AF', IX, IY согласно результату callback, без активности только AF
; Note:
;   перед callback MoveItemToTail возвращает выбранный HL, DE загружен активным индексом, BC сохранён
;   после ToggleItemFrame XOR A подготавливает AF=#0044 для callback, до него индекс уже перенесён в конец списка
;   FActiveCloseFrame содержит SavedHL, SavedDE, ReturnAddress, callback получает собственный адрес возврата поверх кадра
;   изменение активности самим callback не отменяется, после него сбрасывается только адрес Callback
;   сами инструкции закрытия не меняют I и IFF, итог зависит от callback и фактического ISR
;   SP восстанавливается при соблюдении договора callback, произвольные реальные callback этим разбором не признаны проверенными
; -----------------------------------------
                ; чтение целого байта активности из изменяемого операнда LD A
Entry:          LD A, #00
                ; проверка наличия активного элемента, ноль запрещает любые действия закрытия
                AND A
                RET Z                                                           ; выход, если активного элемента нет, вернуть AF=#0054

                ; сохранение входных DE и HL в динамическом FActiveCloseFrame
                PUSH DE
                PUSH HL
                ; чтение активного индекса из изменяемого операнда LD DE
                LD DE, #0000
                ; поиск активного индекса и перенос его обработчика в конец списка
                CALL @Station.MoveItemToTail.Entry
                ; переключение контура активного элемента, если бит 4 не запрещает действие
                CALL @Station.ToggleItemFrame.Entry
                ; сброс активности до вызова callback, его входной AF становится #0044
                XOR A
                LD (@ActiveItemState.Active), A
                ; вызов изменяемого ActiveItemState.Callback, исходная цель EmptyCallback
                CALL @Station.EmptyCallback.Entry
                ; сброс цели callback после его нормального возврата, повторное завершение не вызывает прежнюю цель
                LD HL, @Station.EmptyCallback.Entry
                LD (@ActiveItemState.Callback), HL
                ; восстановление входных HL и DE поверх произвольного результата callback
                POP HL
                POP DE
                ; установка Carry как признака выполненного закрытия, A и S,Z,P/V остаются от callback
                SCF
                RET

                endmodule
                endmodule
