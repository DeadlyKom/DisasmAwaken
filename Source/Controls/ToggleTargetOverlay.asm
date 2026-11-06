                module Controls
                module ToggleTargetOverlay
                ; Документация [алгоритм и проверка](../../Docs/ControlsTargetOverlay.md)
                ; -----------------------------------------
                ; XOR рамки и спроецированных значков объектов в линейном буфере
                ; исходная запись 23, банк 1, смещения #0E9C..#102F
                ; In:
                ;   AF, A=1 ограничивает рисование двумя короткими рамками, остальные значения включают весь проход
                ;   банк 1 выбран, таблицы логарифмической проекции и конечный список объектов доступны
                ;   байты #9B1B..#9B1D задают индексы выделения, стек доступен для проекции, IRQ не вмешиваются
                ; Out:
                ;   короткие рамки инвертируются на всех путях, при A=1 следует немедленный возврат
                ;   полный путь инвертирует внешнюю рамку и XOR-выводит допущенные значки в буфер #8000
                ;   адрес шаблона зависит от подбайтовой фазы X и совпадения индекса, SP после RET увеличен на два
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, R, буфер, операнды делителя и временный стек
                ; Note:
                ;   значок занимает восемь строк по два байта, исходные таблицы используются как есть
                ;   полный растр и SP сверены в 288 сценариях, точные остальные регистры и все побочные записи отдельно не сверялись
                ; -----------------------------------------
                ; Сохранение режима и инверсия поперечных масок коротких рамок.
Entry:          EX AF, AF'
                LD A, (#8431)
                XOR #FE
                LD (#8431), A
                LD A, (#87F1)
                XOR #FE
                LD (#87F1), A
                LD A, (#842E)
                XOR #FE
                LD (#842E), A
                LD A, (#87EE)
                XOR #FE
                LD (#87EE), A
                LD HL, #844E
                LD DE, #8451
                LD BC, #0020
                EXX
                LD L, #07
                ; Инверсия боковых битов первой короткой рамки.
ToggleFirst:    EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #02
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.ToggleTargetOverlay.ToggleFirst                ; переход, если остались строки первой рамки

                EXX
                LD HL, #870E
                LD DE, #8711
                EXX
                LD L, #07
                ; Инверсия боковых битов второй короткой рамки.
ToggleSecond:   EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #02
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.ToggleTargetOverlay.ToggleSecond               ; переход, если остались строки второй рамки

                EX AF, AF'
                DEC A
                RET Z                                                           ; выход, если исходный режим равен 1

                LD HL, #8116
                LD B, #0E
                ; Инверсия верхней полосы полной рамки.
InvertTop:      LD A, (HL)
                CPL
                LD (HL), A
                DEC L
                DJNZ @Controls.ToggleTargetOverlay.InvertTop

                LD HL, #8129
                LD DE, #8136
                LD BC, #0020
                EXX
                LD L, #57
                ; Инверсия боковых битов полной рамки.
ToggleSides:    EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #01
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.ToggleTargetOverlay.ToggleSides                ; переход, если остались строки полной рамки

                LD DE, #0040
                LD IX, #A0C0
                JP @Controls.ToggleTargetOverlay.ResetStride

                ; Проверка младшего байта конечного маркера.
CheckEnd:       LD A, (IX + @FActionRecord.Components.Component0.Low)
                CP #80
                RET Z                                                           ; выход, если младший байт маркера равен #80

ResetStride:    LD DE, #0040
ReadNext:       ADD IX, DE
                LD A, (IX + @FActionRecord.Components.Component0.High)
                CP #80
                JR Z, @Controls.ToggleTargetOverlay.CheckEnd                    ; переход, если старший байт первой компоненты равен #80, проверить маркер

                LD A, (IX + @FActionRecord.ClassCode)
                CP #14
                JR Z, @Controls.ToggleTargetOverlay.CheckEnd                    ; переход, если класс равен #14, проверить маркер

                LD A, (IX + #1B)
                CP #80
                JR Z, @Controls.ToggleTargetOverlay.ReadNext                    ; переход, если выходная запись помечена байтом #80

                LD B, A
                LD C, (IX + #1A)
                LD D, (IX + #1F)
                BIT 7, D
                JR NZ, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если глубина отрицательна

                LD A, D
                CP #06
                JR C, @Controls.ToggleTargetOverlay.ResetStride                 ; переход, если старший байт глубины меньше #06

                LD E, (IX + #1E)
                LD A, (IX + #1D)
                LD H, A
                LD L, (IX + #1C)
                ; Вычисление экранных координат по двум отношениям к глубине.
                CALL #ADC5
                JR NZ, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если проекция вернула отказ

                LD A, H
                AND A
                JR NZ, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если X не помещается в младший байт

                LD A, D
                AND A
                JR NZ, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если Y не помещается в младший байт

                LD A, L
                SUB #50
                JR C, @Controls.ToggleTargetOverlay.ResetStride                 ; переход, если X левее области значков

                CP #5E
                JR NC, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если X на правой границе области или за ней

                LD A, E
                SUB #0E
                JR C, @Controls.ToggleTargetOverlay.ResetStride                 ; переход, если Y выше области значков

                CP #4C
                JR NC, @Controls.ToggleTargetOverlay.ResetStride                ; переход, если Y на нижней границе области или за ней

                LD B, E
                LD A, L
                SUB #04
                LD C, A
                AND #07
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, #0E
                LD E, A
                LD A, #EB
                ADC A, #00
                LD D, A
                LD A, IXL
                LD L, A
                LD A, IXH
                LD H, A
                PUSH DE
                LD DE, #5F00
                ADD HL, DE
                POP DE
                LD A, H
                SLA L
                RLA
                SLA L
                RLA
                LD L, A
                LD A, (#9B1B)
                CP L
                JR Z, @Controls.ToggleTargetOverlay.HighlightIcon               ; переход, если совпал первый индекс выделения

                LD A, (#9B1C)
                CP L
                JR Z, @Controls.ToggleTargetOverlay.HighlightIcon               ; переход, если совпал второй индекс выделения

                LD A, (#9B1D)
                CP L
                JR NZ, @Controls.ToggleTargetOverlay.DrawIcon                   ; переход, если третий индекс тоже отличается, оставить обычный значок

                ; Выбор второй половины таблицы для выделенного значка.
HighlightIcon:  LD A, E
                ADD A, #80
                LD E, A
                LD A, D
                ADC A, #00
                LD D, A
                ; Расчёт адреса в линейном буфере и XOR восьми строк значка.
DrawIcon:       LD A, C
                RRCA
                RRCA
                RRCA
                AND #1F
                LD C, A
                LD A, B
                SUB #04
                RLCA
                LD L, A
                LD H, #08
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD B, #00
                ADD HL, BC
                LD BC, #001F
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                JP @Controls.ToggleTargetOverlay.ResetStride

                endmodule
                endmodule
