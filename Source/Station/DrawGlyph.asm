                module Station
                module DrawGlyph
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [GlyphRendering.md](../../Docs/GlyphRendering.md)
; -----------------------------------------
; Вывод восьмистрочного глифа через таблицу сдвигов и двухчастных переходов экранной раскладки
; исходная запись 4, файловые смещения #4E8D..#4F0B
; In:
;   AF - A восьмибитный код глифа, TextWindow задаёт относительный курсор, размеры и знаковое начало
;   подготовлены исходные таблицы адресации и FGlyphRoute, стек имеет место для FGlyphFrame
;   код по GlyphState.KernelPrefix содержит исходные #68,#48,#26 либо временный JP ReturnGlyph.Entry
; Out:
;   HL, DE, BC, альтернативные и индексные регистры сохраняются, AF содержит статус выбранного выхода
;   при успехе A=0,F=#45, принятая ширина прибавлена к CursorX, CursorY сохранён
;   отказы по высоте и ширине возвращают A=2 и A=3 без изменения курсора, флаги от AND проверенного значения
;   отказы координат и нижней границы, отрицательное невидимое начало и режим без рисования описаны в Font.md
; Corrupt:
;   AF
; Note:
;   ширина сравнивается строго, равенство следующего CursorX и Width является отказом
;   CursorX обновляется до проверки физического начала, отрицательный старший байт начала пропускает глиф с успешным статусом
;   неотрицательный ненулевой старший X возвращает A=0,F=#44, старший Y возвращает A=1,F=#00
;   физический верхний Y не меньше 185 возвращает A=1 с флагами CP(Y,185), курсор уже продвинут
;   при исходном коде пиксели объединяются XOR, крайняя колонка не записывает соседний байт, атрибуты сохраняются
;   JP в KernelPrefix обходит только пиксельную часть, проверки и продвижение остаются, изменяемый DispatchTarget в этом режиме не записывается
;   I и IFF сохраняются, SP восстанавливается, изменяемые операнды делают вход не реентерабельным
; -----------------------------------------
                ; создание FGlyphFrame, сохраняются оба набора общих регистров и альтернативный AF
Entry:          PUSH DE
                PUSH BC
                PUSH HL
                EXX
                PUSH DE
                PUSH BC
                PUSH HL
                EX AF, AF'
                PUSH AF
                EX AF, AF'
                LD L, A
                ; подготовка адреса восьми строк глифа по восьмибитному коду символа
                LD E, A
                LD D, @FontConst.WidthPage
                LD H, #00
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD BC, @FontConst.GlyphBase
                ADD HL, BC
                EX DE, HL
                ; чтение относительных X и Y текстового курсора
                LD BC, (@TextWindow.CursorX)
                LD A, B
                ; проверка относительной строки до изменения курсора
CheckHeight:    CP #00
                JR NC, @Station.GlyphHeightError.Entry                          ; переход, если относительный Y не меньше высоты окна, возвращается код 2

                ; выбор ширины символа и расчёт следующей относительной позиции X
                LD A, (HL)
                ADD A, C
                JR C, @Station.GlyphWidthError.Entry                            ; переход, если сумма ширины и CursorX переполнила байт, возвращается код 3

                ; проверка строгой правой границы текстового окна
CheckWidth:     CP #00
                JP NC, @Station.GlyphWidthError.Entry                           ; переход, если следующая позиция X не меньше ширины окна, возвращается код 3

                ; обновление относительного курсора до проверки физического начала
                LD (@TextWindow.CursorX), A
                ; расчёт физического X из исходного курсора и знакового начала окна
OriginX:        LD A, #00
                ADD A, C
                LD C, A
OriginXHigh:    LD A, #00
                ADC A, #00
                JR NZ, @Station.GlyphOriginXError.Entry                         ; переход, если физический X не представим без ненулевого старшего байта

                LD A, C
                EX AF, AF'
                ; расчёт физического Y из относительной строки и знакового начала окна
OriginY:        LD A, #00
                ADD A, B
                LD B, A
OriginYHigh:    LD A, #00
                ADC A, #00
                JR NZ, @Station.GlyphOriginYError.Entry                         ; переход, если физический Y имеет ненулевой старший байт

                LD A, B
                ; проверка, что все восемь строк глифа помещаются в видимые 192 строки
CheckBottom:    CP @FontConst.GlyphTopLimit
                JR NC, @Station.GlyphBottomError.Entry                          ; переход, если верхняя физическая строка не меньше 185, возвращается код 1

                ; начало пиксельной части, временный JP ReturnGlyph.Entry позволяет только продвижение курсора
KernelPrefix:   LD L, B
                LD C, B
                LD H, @StationTables.RowHighPage
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                EX AF, AF'
                LD L, A
                EX AF, AF'
                OR (HL)
                LD L, A
                LD H, B
                EX AF, AF'
                AND @ScreenConst.PixelOffsetMask
                ADD A, A
                LD B, A
                LD A, L
                INC A
                AND @ScreenConst.ColumnMask
                JP NZ, @Station.DrawGlyph.PointAEF0                             ; переход, если флаг Z сброшен

                INC B
PointAEF0:      LD A, B
                ADD A, A
                ADD A, A
                ADD A, A
                LD B, A
                LD A, C
                AND @ScreenConst.PixelOffsetMask
                ADD A, B
                EXX
                ADD A, A
                LD L, A
                LD H, @FontConst.RouteHalfPage
                ADD HL, HL
                ; выбор очередного слова FGlyphRoute и запись цели общего изменяемого JP
NextRoute:      LD C, (HL)
                INC L
                LD B, (HL)
                INC L
                AND A
                LD (@GlyphState.DispatchTarget), BC
                EXX
                ; передача управления выбранному числу строк ядра сдвига
Dispatch:       JP #0000

                endmodule
                endmodule
