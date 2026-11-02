                module Controls
                module DrawGlyphRows
                ; Документация [вывод текстового окна](../../Docs/ControlsTextDisplay.md)
                ; -----------------------------------------
                ; Слияние шести строк упакованного знака с выбранной тетрадой экрана
                ; исходная запись 23, банк 1, смещения #1513..#15B5
                ; In:
                ;   HL указывает верхний байт назначения, DE верхний байт шестистрочной пары знаков
                ;   BC задаёт чётность C, нечётный C выбирает старшую экранную тетраду, AF' задаёт чётность индекса в A'
                ;   пара знаков и шесть байтов назначения доступны, переноса из H в L между строками нет
                ; Out:
                ;   H увеличен на 5 по модулю 256, L сохранён, DE увеличен на 5 по модулю 65536
                ;   C=F0 для нечётного входного C либо 0F для чётного входного C
                ;   B сохраняет соседнюю тетраду последней строки, A содержит итоговый байт, F соответствует последнему OR
                ;   HL', DE', BC', IX и IY сохраняются, I, IM и IFF сохраняются, SP=входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', шесть байтов назначения, R
                ; Note:
                ;   две ветви различаются только перестановкой тетрад исходного байта
                ;   PrintTextGlyph входит последовательным исполнением, DrawCounterNibble вызывает этот же рисователь через CALL
                ;   положение окна и TextColumn здесь не проверяются, эта часть допускает другой экранный адрес
                ; -----------------------------------------
                ; выбор экранной маски по чётности уже увеличенной колонки
Entry:          BIT 0, C
                LD B, #F0
                JR NZ, @Controls.DrawGlyphRows.SelectFontHalf                   ; переход, если увеличенная колонка нечётна, рисовать в старшей тетраде

                LD B, #0F
                ; получение чётности исходного индекса знака из альтернативного A
SelectFontHalf: EX AF, AF'
                RRA
                JR NC, @Controls.DrawGlyphRows.SelectRotation                   ; переход, если индекс знака чётный, сохранить выбор экранной тетрады

                ; изменение выбора перестановки для младшей тетрады шрифтовой пары
                LD A, C
                XOR #01
                LD C, A
                ; проверка необходимости переставить тетрады шрифтового байта
SelectRotation: BIT 0, C
                LD C, B
                JR NZ, @Controls.DrawGlyphRows.DirectRows                       ; переход, если нужная тетрада уже совпадает с экранной маской, копировать без вращения

                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                RRCA
                RRCA
                RRCA
                RRCA
                AND C
                OR B
                LD (HL), A
                RET

DirectRows:     LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                INC H
                INC DE
                LD A, C
                CPL
                AND (HL)
                LD B, A
                LD A, (DE)
                AND C
                OR B
                LD (HL), A
                RET

                endmodule
                endmodule
