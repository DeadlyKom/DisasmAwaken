                module Action
                module StartFlight
                ; Документация [вход и кадры](../../Docs/ActionFlightCycle.md)
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Вывод панели из страницы 6 и инициализация полётного режима
; исходная запись 17, файловые смещения #482D..#4858
                ; In:
                ;   загружены ACTION, CONTROL и распакованная панель в банке 6
                ;   доступны контекст параметров, очередь и экран, порт 7FFD разблокирован
                ;   SP находится в общей RAM и допускает рабочие рамки дочерних процедур
                ; Out:
                ;   скопировано #1B00 байтов панели, обновлены шкалы и счётчик, активированы параметры
                ;   созданы 35 точек, в очередь передан элемент #F1AB, после вызова восстановлен прежний DE
                ;   HL=#C546, AF=#1042, страница #10, прерывания выключены
                ;   SP равен входному, исполнение продолжается в MainLoop
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, R, IFF, экран, контекст параметров, точки, очередь, 7FFD и стек
                ; Note:
                ;   DE на выходе берётся из состояния после активации параметров, а не из входа StartFlight
                ;   исходный JP из InitializeFlight не создаёт возврата, MainLoop начинается последовательно
                ;   модель проверяет копирование и страницы с подменённым чтением TR-DOS
; -----------------------------------------
Entry:          DI
                LD A, #1E
                CALL @Action.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #4000
                LD BC, #1B00
                LDIR
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.RefreshFlightPanel.Entry
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.BuildAndActivateParameters.Entry
                CALL @Action.InitializeBankedBufferPoints.Entry
                PUSH DE
                LD DE, #F1AB
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; JP @Action.MainLoop.Entry, продолжение в MainLoop.asm

                endmodule
                endmodule
