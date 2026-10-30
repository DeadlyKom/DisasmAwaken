                module Station
                module ToggleItemFrame
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [смена контура элемента](../../Docs/ItemToggle.md)
; -----------------------------------------
; Переключение бита контура элемента и полная перерисовка с защитой указателя
; исходная запись 4, файловые смещения #3EA5..#3EC3
; In:
;   HL - произвольное сохраняемое значение, DE - индекс существующей FInterfaceItem, BC сохраняется
;   при сброшенном Flags.bit4 действуют предусловия DrawCenteredItem, SuspendPointer и ResumePointer
;   HALT обязан получить пробуждение, ISR должен сохранить состояние в точке ожидания
; Out:
;   HL, DE и BC восстановлены, IX и IY сохранены
;   при установленном бите 4 A=Flags, F=(Flags AND #28) OR #10, записи и экран не меняются
;   иначе Flags.bit0 инвертирован, элемент зарегистрирован и перерисован, указатель возобновлён
;   при перерисовке AF от DrawCenteredItem, A=#C3, F от последнего текстового прохода
; Corrupt:
;   AF, HL', AF' при перерисовке, при запрете только AF
; Note:
;   H', DE', BC', I, IFF сохраняются самими процедурами, вмешательство ISR моделью не подтверждено
;   SP восстанавливается, FToggleItemFrame состоит из SavedDE, SavedBC, SavedHL, ReturnAddress
;   бит 4 запрещает только этот путь смены контура, его смысл у других потребителей требует отдельного разбора
;   POP HL перед HALT читает исходный DE-индекс и сразу возвращает его в кадр через PUSH HL
;   при допустимом переключении флаг запрета периодического обновления не восстанавливается, ResumePointer оставляет ноль
;   изменение Flags записывается до SuspendPointer и не отменяется при последующем отказе текста
; -----------------------------------------
                ; сохранение HL, BC и DE в динамическом FToggleItemFrame
Entry:          PUSH HL
                PUSH BC
                PUSH DE
                ; передача входного индекса DE в GetItemFlags без потери сохранённого HL
                EX DE, HL
                CALL @Station.GetItemFlags.Entry
                ; чтение Flags и проверка запрета переключения контура в бите 4
                LD A, (HL)
                BIT @InterfaceFlags.ToggleLockBit, A
                JR NZ, @Station.ToggleItemFrame.Finish                          ; переход, если бит запрета 4 установлен, снять кадр без перерисовки

                ; инверсия только бита 0, выбирающего один из двух контуров
                XOR @InterfaceFlags.FrameBitMask
                LD (HL), A
                ; восстановление фона указателя перед изменением пикселей элемента
                CALL @Station.SuspendPointer.Entry
                ; чтение исходного индекса из SavedDE в HL с немедленным возвратом слова на стек
                POP HL
                PUSH HL
                ; ожидание пробуждения HALT перед полной перерисовкой, IRQ обязан сохранить контекст
                HALT
                ; регистрация элемента, вывод рамки и текста с новым битом контура
                CALL @Station.DrawCenteredItem.Entry
                ; повторный захват фона и наложение указателя, разрешение его периодического обновления
                CALL @Station.ResumePointer.Entry
                ; снятие FToggleItemFrame с восстановлением исходных DE, BC и HL
Finish:         POP DE
                POP BC
                POP HL
                RET

                endmodule
                endmodule
