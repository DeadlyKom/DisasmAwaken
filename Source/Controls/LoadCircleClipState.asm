                module Controls
                module LoadCircleClipState
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleSetup.md)
                ; -----------------------------------------
                ; Загрузка рабочего X и состояния сечения для отсечённого контура
                ; исходная запись 22, банк 1, смещения #156C..#157A
                ; In:
                ;   HL, DE сохраняются, BC и AF входных аргументов не задают
                ;   банк 1 выбран, WorkY, WorkX и SectionRadius доступны для чтения, на стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL, DE сохраняются, B=WorkX, C=WorkY, A=SectionRadius
                ;   C'=(136-WorkX) AND FF, E'=SectionRadius, F соответствует SUB между 136 и WorkX
                ;   HL', DE', BC' сохраняются кроме C' и E', AF', IX, IY, I, IM и IFF сохраняются
                ;   SP=входной SP+2, R получает 10 M1
                ; Corrupt:
                ;   BC, AF, E', C', R
                ; Note:
                ;   136 равно 256-120, арифметика выполняется по модулю байта, знак результата отдельно не расширяется
                ;   RAM не записывается, полная геометрическая область вызывающего отсечённого контура здесь не доказана
                ; -----------------------------------------
                ; загрузка рабочей пары Y и X для отсечённой ветви
Entry:          LD BC, (@ControlsCircleSetupState.WorkY)
                ; вычисление байтового состояния сечения как 256-120-WorkX
                LD A, #88
                SUB B
                ; загрузка C' и E' без изменения основных HL и DE
                EXX
                LD C, A
                LD A, (@ControlsCircleSetupState.SectionRadius)
                LD E, A
                EXX
                RET

                endmodule
                endmodule
