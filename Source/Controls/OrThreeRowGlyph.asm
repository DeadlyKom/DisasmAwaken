                module Controls
                module OrThreeRowGlyph
                ; Документация [алгоритм и проверка](../../Docs/ControlsThreeRowGlyph.md)
                ; -----------------------------------------
                ; Наложение трёхстрочного фазового знака операцией OR на два байта каждой строки экрана
                ; исходная запись 23, банк 1, смещения #0670..#06D2
                ; In:
                ;   HL входных аргументов не задаёт, DE задаёт начало восьми последовательных фаз по шесть байтов
                ;   BC задаёт B как верхнюю строку Y, C как левую координату X, AF входных аргументов не задаёт
                ;   банк 1 выбран, шесть байтов выбранной фазы доступны для чтения и не перекрываются с шестью целями записи
                ;   на CPU-стеке внешний возврат, рамка и исполняемый код не перекрываются с целями, IRQ не вмешиваются
                ; Out:
                ;   HL указывает правый байт нижней третьей строки, DE=(входной DE+6*(X AND 7)+5) AND FFFF
                ;   B=входной Y, C=2*(X AND 7), A содержит результат последнего OR, F соответствует этому OR, H, N, C сброшены
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   выполнены ровно шесть записей OR, никакие пиксели не очищаются и CPU-стек не записывается
                ;   R получает 69 M1 при (Y AND 7)<6, 73 при (Y AND 3F)>=3E, иначе 76
                ; Corrupt:
                ;   HL, DE, BC в части C, AF, шесть байтов растра, R
                ; Note:
                ;   B и C байтовые, отсечение по ширине и высоте не выполняется, игровые вызывающие ограничивают координаты отдельно
                ;   переход к правому байту использует INC L без переноса в H, столбец 31 сохраняет исходное нелинейное поведение
                ;   переходы строк учитывают чередование страниц Spectrum, при Y>=192 затрагиваются атрибуты и следующая RAM
                ;   адрес выбранной фазы и последовательные INC DE переходят через FFFF по модулю слова
                ;   четыре исходных знака имеют ширину три пикселя и высоту три строки, пиксельный центр находится на X+1, Y+1
                ;   общий алгоритм применим к шести масочным байтам выбранной фазы, перекрывающиеся ресурсы не входят в доказанный договор
                ; -----------------------------------------
                ; вычисление старшего адреса экранной строки из групп Y и её младших трёх разрядов
Entry:          LD A, B
                AND A
                RRA
                SCF
                RRA
                AND A
                RRA
                XOR B
                AND @ControlsThreeRowGlyphConst.HighMergeMask
                XOR B
                LD H, A
                ; вычисление младшего экранного адреса из группы строк Y и байтового столбца X DIV 8
                LD A, C
                RLCA
                RLCA
                RLCA
                XOR B
                AND @ControlsThreeRowGlyphConst.LowMergeMask
                XOR B
                RLCA
                RLCA
                LD L, A
                ; вычисление номера фазы X AND LowThreeMask и её смещения 6*фаза через сохранённые 2*фаза в C
                LD A, C
                AND @ControlsThreeRowGlyphConst.LowThreeMask
                ADD A, A
                LD C, A
                ADD A, A
                ADD A, C
                ; вычисление полного адреса выбранной шестибайтовой фазы с переносом в D
                ADD A, E
                LD E, A
                LD A, D
                ADC A, #00
                LD D, A
                ; наложение двух байтов верхней строки знака операцией OR без очистки старых пикселей
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                DEC L
                ; вычисление адреса средней строки, проверка границы восьмистрочной группы
                INC H
                LD A, H
                AND @ControlsThreeRowGlyphConst.LowThreeMask
                JP NZ, @Controls.OrThreeRowGlyph.DrawMiddle                     ; переход, если младшие три разряда новой H ненулевые, адрес средней строки уже готов

                ; вычисление следующей группы строк прибавлением CharRowStride к младшему адресу
                LD A, L
                ADD A, @ControlsThreeRowGlyphConst.CharRowStride
                LD L, A
                JR C, @Controls.OrThreeRowGlyph.DrawMiddle                      ; переход, если прибавление CharRowStride перенесло младший L, сохранить увеличенную H

                ; коррекция H на CharHeight страниц после перехода группы без переноса L
                LD A, H
                SUB @ControlsThreeRowGlyphConst.CharHeight
                LD H, A
                ; наложение двух байтов средней строки, младший L после пары возвращается к левому байту
DrawMiddle:     LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                DEC L
                ; вычисление адреса нижней строки, проверка следующей границы группы
                INC H
                LD A, H
                AND @ControlsThreeRowGlyphConst.LowThreeMask
                JP NZ, @Controls.OrThreeRowGlyph.DrawBottom                     ; переход, если младшие три разряда новой H ненулевые, адрес нижней строки уже готов

                ; вычисление младшего адреса следующей группы для нижней строки
                LD A, L
                ADD A, @ControlsThreeRowGlyphConst.CharRowStride
                LD L, A
                JR C, @Controls.OrThreeRowGlyph.DrawBottom                      ; переход, если прибавление CharRowStride перенесло младший L, сохранить увеличенную H

                ; коррекция H на CharHeight страниц при переходе группы без переноса L
                LD A, H
                SUB @ControlsThreeRowGlyphConst.CharHeight
                LD H, A
                ; наложение нижней пары, последний OR определяет выходные A и F
DrawBottom:     LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                RET

                endmodule
                endmodule
