                module Station
                module SplitGlyphShift7
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; XOR префикса глифа до следующего знакоместа, сдвиг вправо на 7 пикселей, до двух соседних байтов
; исходная запись 4, файловые смещения #5AA9..#5B1F
; In:
;   HL - рабочий адрес экранной строки, DE - рабочий адрес строки глифа, Carry=0
;   CPU-стек содержит FGlyphFrame, подготовленный DrawGlyph, обычный CALL с одним адресом возврата недопустим
;   восемь строк либо RowsN должны соответствовать выбранному слову FGlyphRoute, правый край соответствует варианту процедуры
; Out:
;   выведенные пиксели объединены с bitmap через XOR, управление завершается общим ReturnGlyph
;   AF=#0045, обычные и альтернативные регистры восстановлены из FGlyphFrame, SP увеличен на размер этого кадра
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа заменяются сохранёнными значениями кадра
; Note:
;   сдвиг по X равен 7, в каждой строке первый вклад равен байту глифа SHR 7
;   второй вклад равен младшим восьми битам байта глифа SHL (8-сдвиг), при нулевом сдвиге второй байт не требуется
;   префикс завершает текущее знакоместо, корректирует HL и через второе слово FGlyphRoute передаёт управление остатку
;   индексные регистры, I и IFF сохраняются, атрибуты не записываются
;   контракт относится к исходным XOR-инструкциям и кадру DrawGlyph, отдельного самостоятельного интерфейса здесь нет
; -----------------------------------------
                ; вывод семи строк до границы знакоместа, сдвиг вправо на 7 пикселей, до двух соседних байтов, RowsN сокращают префикс до N строк
Entry:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows6:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows5:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows4:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows3:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows2:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
Rows1:          LD A, (DE)
                LD C, A
                XOR A
                RL C
                RLA
                XOR (HL)
                LD (HL), A
                INC L
                INC E
                LD A, C
                XOR (HL)
                LD (HL), A
                DEC L
                INC H
                ; расчёт адреса следующей строки знакомест после завершения текущей восьмистрочной группы
WrapRow:        LD A, L
                ADD A, @ScreenConst.ByteColumns
                LD L, A
                JR C, @Station.SplitGlyphShift7.NextPart                        ; переход, если младший байт переполнился, старшая часть уже соответствует следующей трети экрана

                LD A, H
                SUB @ScreenConst.PixelsPerChar
                LD H, A
                ; возврат к табличному указателю второго слова и выбор оставшихся строк глифа
NextPart:       EXX
                JP @Station.DrawGlyph.NextRoute

                endmodule
                endmodule
