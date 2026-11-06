                module Controls
                module ResumeCirclePushSpan
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleKernels.md)
                ; -----------------------------------------
                ; Восстановление CPU-стека после обычной PUSH-заливки и продолжение горизонтальной фазы
                ; исходная запись 22, банк 1, смещения #1727..#173A
                ; In:
                ;   HL задаёт правую границу после PUSH-заливки, DE задаёт правый младший адрес D и левый E, BC содержит маски
                ;   AF содержит два байта рисунка, альтернативные пары содержат состояние горизонтальной фазы
                ;   IX задаёт рисунок и чередование, SavedSP указывает SavedAF и внешний возврат, Direction определяет шаг строки
                ;   SP пока направлен в растр, банк 1 выбран, IRQ не вмешиваются
                ; Out:
                ;   HL и E перенесены на следующую строку либо за её вертикальный край, D и BC сохраняются до продолжения ядра
                ;   на обычном продолжении AF и IXL соответствуют AdvanceRasterUp либо AdvanceRasterDown, SP=SavedSP
                ;   при достижении края AF восстановлен из SavedAF, SP=SavedSP+4 и исполнен внешний RET
                ;   HL', DE', BC', AF', IXH, IY, I, IM, IFF и страница сохраняются до продолжения ядра
                ; Corrupt:
                ;   HL, E, AF, IXL, SP, R, два байта CPU-стека непосредственного CALL помощника
                ; Note:
                ;   вход не является отдельной возвращающейся процедурой, жёсткий порядок после CircleRasterCore.asm сохраняется
                ;   обычное продолжение переходит к CircleRasterCore.FastX, состояние альтернативной ошибки не сбрасывается
                ;   отдельная модель PUSH-цепочек проверяет реальные помощники, R и все записи до FastX либо внешнего возврата
                ;   полный последующий проход относится к моделям сечения, IRQ и нативный запуск не выполнены
                ; -----------------------------------------
                ; Чтение Direction, нулевое значение выбирает движение вверх, единица движение вниз.
Entry:          LD A, (@ControlsCircleWork.Value.Direction)
                AND A
                ; Восстановление CPU-стека перед настоящим CALL шага строки, помощник может завершить весь рисователь.
                LD SP, (@ControlsRasterStepState.SavedSP)
                JR NZ, @Controls.ResumeCirclePushSpan.NextDown                  ; переход, если Direction ненулевой, вызвать шаг вниз вместо шага вверх

                CALL @Controls.AdvanceRasterUp.Entry
                JR @Controls.CircleRasterCore.FastX

NextDown:       CALL @Controls.AdvanceRasterDown.Entry
                JR @Controls.CircleRasterCore.FastX

                endmodule
                endmodule
