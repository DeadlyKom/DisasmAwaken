                module Station
                module CenterItemLine
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [рамка и центрирование текста элемента](../../Docs/CenteredItem.md)
; -----------------------------------------
; Внутреннее продолжение центрирования строки и общий выход стекового кадра элемента
; исходная запись 4, файловые смещения #6325..#634A
; In:
;   HL - начало текущей CR-строки, BC - C измеренная ширина строки
;   на вершине CPU-стека находится Workspace уже созданного FCenteredItemFrame
;   TextWindow и регистрация подготовлены DrawCenteredItem, Style=1 и LineEndCode содержит RET
; Out:
;   HL, DE и BC восстановлены из полей FCenteredItemFrame при общем выходе
;   AF - A=#C3, F последнего PrintText либо PrintJustified, LineEndCode восстановлен в JP
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   Entry является продолжением предыдущего файла, обычный CALL без кадра недопустим
;   FinalWords снимает временное сохранение начала строки, Finish снимает весь FCenteredItemFrame
;   альтернативные и индексные регистры, I и IFF внутри этого продолжения сохраняются
;   косвенное продолжение NextLine может снова пройти в эту точку, порядок включений обязателен
; -----------------------------------------
                ; расчёт свободной ширины относительно измеренной строки
Entry:          LD A, (@TextWindow.Width)
                SUB C
                JR NC, @Station.CenterItemLine.Position                         ; переход, если строка не шире окна, свободная ширина уже рассчитана

                ; обнуление свободного места для строки шире окна
                XOR A
                ; расчёт X как целой половины свободного места, округление вниз
Position:       SRL A
                LD (@TextWindow.CursorX), A
                CALL @Station.PrintText.Entry
                JR C, @Station.CenterItemLine.Finish                            ; переход, если текстовый проход вернул Carry, завершить элемент и восстановить JP

                JP @Station.DrawCenteredItem.NextLine

                ; восстановление начала последнего абзаца, временный указатель строки снят со стека
FinalWords:     POP HL
                ; обнуление X перед выравниванием последнего абзаца
                XOR A
                LD (@TextWindow.CursorX), A
                CALL @Station.PrintJustified.Entry
                ; восстановление исходного JP после CR с сохранением F текстового прохода
Finish:         LD A, @TextFlowOpcode.Continue
                LD (@TextStreamState.LineEndCode), A
                ; удаление рабочего слова FCenteredItemFrame.Workspace
                POP HL
                ; восстановление FCenteredItemFrame.SavedBC, SavedDE и SavedHL
                POP BC
                POP DE
                POP HL
                ; возврат по FCenteredItemFrame.ReturnAddress, кадр полностью снят
                RET

                endmodule
                endmodule
