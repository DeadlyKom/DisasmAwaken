                module Station
                module DrawGlyphEdge6
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; XOR строк глифа, сдвиг вправо на 6 пикселей, только крайний байт экрана
; исходная запись 4, файловые смещения #5999..#59E2
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
;   сдвиг по X равен 6, в каждой строке первый вклад равен байту глифа SHR 6
;   второй байт экрана не записывается, пиксели правее 255 отсекаются
;   Entry выводит восемь строк, вход RowsN начинает с нужного места развёрнутого блока и выводит N строк
;   индексные регистры, I и IFF сохраняются, атрибуты не записываются
;   контракт относится к исходным XOR-инструкциям и кадру DrawGlyph, отдельного самостоятельного интерфейса здесь нет
; -----------------------------------------
                ; вывод восьми строк глифа, сдвиг вправо на 6 пикселей, только крайний байт экрана, дополнительные входы RowsN выводят последние N строк
Entry:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows7:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows6:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows5:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows4:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows3:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows2:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                INC E
                INC H
Rows1:          LD A, (DE)
                RLCA
                RLCA
                AND #03
                XOR (HL)
                LD (HL), A
                EXX
                JP @Station.ReturnGlyph.Entry

                endmodule
                endmodule
