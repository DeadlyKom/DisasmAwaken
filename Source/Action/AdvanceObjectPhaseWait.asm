                module Action
                module AdvanceObjectPhaseWait
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectPhaseWait.md)
                ; -----------------------------------------
                ; Обновление фазового счётчика и завершение ожидания по классу и компонентам
                ; исходная запись 17, адреса EFB5..F002
                ; In:
                ;   IX указывает FActionRecord, банк 0 выбран, PhaseGate содержит текущую фазу
                ; Out:
                ;   класс от 8 восстанавливает состояние из байта 16 и обнуляет счётчик 24 без вращения фазы
                ;   класс ниже 8 вращает PhaseGate вправо, единичный исходный бит 0 допускает инкремент счётчика ниже 15
                ;   B и C получают свёрнутые старшие байты Y и X при вычислении максимума, отрицательные байты инвертируются
                ;   максимум меньше 20 восстанавливает состояние и обнуляет счётчик, PC=F0F8, SP сохраняется
                ; Corrupt:
                ;   BC, AF, R, PhaseGate и условные поля записи
                ; Note:
                ;   69632 сценария проверяют реальные регистры, R и записи до общего продолжения F0F8
                ; -----------------------------------------
                ; Проверка класса перед фазовым ожиданием.
Entry:          LD A, (IX + @FActionRecord.ClassCode)
                CP #08
                JR NC, @Action.AdvanceObjectPhaseWait.ResumeState               ; переход, если класс не меньше 8, восстановить сохранённое состояние

                ; Вращение фазового операнда и проверка его исходного младшего бита.
                LD A, #11
                RRCA
                LD (@ActionObjectPhaseWaitState.PhaseGate), A
                JR NC, @Action.AdvanceObjectPhaseWait.FoldX                     ; переход, если младший бит фазы был нулём, пропустить инкремент

                ; Проверка насыщения счётчика перед инкрементом.
                LD A, (IX + @FActionRecord.Unknown24)
                CP #0F
                JR NC, @Action.AdvanceObjectPhaseWait.FoldX                     ; переход, если счётчик не меньше 15, сохранить его

                INC A
                LD (IX + @FActionRecord.Unknown24), A
                ; Свёртка старших байтов трёх компонент, отрицательные значения инвертируются.
FoldX:          LD A, (IX + @FActionRecord.Components.Component0.High)
                OR A
                JP P, @Action.AdvanceObjectPhaseWait.SaveX                      ; переход, если старший байт X неотрицателен, сохранить его

                CPL
SaveX:          LD C, A
                LD A, (IX + @FActionRecord.Components.Component1.High)
                OR A
                JP P, @Action.AdvanceObjectPhaseWait.SaveY                      ; переход, если старший байт Y неотрицателен, сохранить его

                CPL
SaveY:          LD B, A
                LD A, (IX + @FActionRecord.Components.Component2.High)
                OR A
                JP P, @Action.AdvanceObjectPhaseWait.CompareY                   ; переход, если старший байт глубины неотрицателен, сравнить его с Y

                CPL
                ; Поиск максимума свёрнутых компонент.
CompareY:       CP B
                JR NC, @Action.AdvanceObjectPhaseWait.CompareX                  ; переход, если глубина не меньше Y, сохранить текущий максимум

                LD A, B
CompareX:       CP C
                JR NC, @Action.AdvanceObjectPhaseWait.CheckLimit                ; переход, если текущий максимум не меньше X, проверить порог ожидания

                LD A, C
                ; Проверка порога удержания состояния.
CheckLimit:     CP #14
                JP NC, @Action.PrepareObjectOffsetTransform.Entry               ; переход, если максимум не меньше 20, сохранить состояние ожидания

                ; Восстановление сохранённого состояния и сброс фазового счётчика записи.
ResumeState:    LD A, (IX + @FActionRecord.SavedStateCode)
                LD (IX + @FActionRecord.StateCode), A
                LD (IX + @FActionRecord.Unknown24), #00
                JP @Action.PrepareObjectOffsetTransform.Entry

                endmodule
                endmodule
