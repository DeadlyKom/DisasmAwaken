                module Station
                module DrawItem01
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [четыре пары, десять глифов и физическая сверка bitmap](../../Docs/CounterDraw.md)
; -----------------------------------------
; Заполнение элемента 1 и вывод восьми разрядов станционного BCD-счётчика
; исходная запись 4, файловые смещения #46EE..#476F
; In:
;   DrawItemState.Opcode01 равен 21 для исполнения либо C9 для отключения, Index01 содержит индекс записи
;   для активной обёртки действуют FillItemBitmap и DrawGlyph, выбран станционный банк 0
;   StationTimer.Counter доступен, для числового прочтения каждая пара должна содержать допустимые BCD-разряды
;   рабочие операнды рисователей доступны для записи, при вмешательстве ISR действует его договор сохранения
; Out:
;   активная обёртка устанавливает TextWindow.Style=1, временно FillMode=80 и заполняет видимый bitmap единицами
;   исходный FillMode восстановлен перед первым глифом, геометрия окна по FillItemBitmap, CursorX установлен в 3
;   выводятся High, MidHigh, двоеточие, MidLow, двоеточие, Low, по два полубайта на поле
;   HL сохранённый индекс обёртки, DE видимая ширина с D=0 по FillItemBitmap
;   BC - B прочитанный High, C прочитанный Low, AF статус последнего DrawGlyph
;   при успехе всех глифов CursorX=3+сумма десяти ширин, CursorY=0, A=0, F=45
;   альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2
;   при Opcode01=C9 все регистры и операнды сохраняются, выполняется немедленный RET
; Corrupt:
;   HL, DE, BC, AF только при активной обёртке
; Note:
;   каждый символ получается прибавлением кода 0 к полубайту, значения A..F дают коды 3A..3F, а не латинские A..F
;   Style=1 после вывода не восстанавливается, атрибуты экрана собственные заполнение и XOR-глифы не меняют
;   четыре байта не копируются в единый снимок, High/MidHigh читаются одним LD BC, MidLow и Low позже отдельно
;   при работающем ISR отображение может сочетать разные состояния счётчика, блокировки прерываний нет
;   ширина и отказ каждого глифа соответствуют DrawGlyph, отказ не прекращает последующие вызовы
;   индекс записывается загрузчиком в A6EF, начальное дисковое слово равно нулю
; -----------------------------------------
                ; чтение Index01 из изменяемого операнда, временный RET в Opcode01 отключает весь рисователь
Entry:          LD HL, #0000
                ; выбор исходного стиля последующего текстового вывода
                LD A, #01
                LD (@TextWindow.Style), A
                ; сохранение полного байта режима заполнения на CPU-стеке
                LD A, (@StationRaster.FillMode)
                PUSH AF
                ; выбор режима с нулевым bit0 для заполнения bitmap единицами
                LD A, #80
                LD (@StationRaster.FillMode), A
                CALL @Station.FillItemBitmap.Entry
                ; восстановление прежнего режима сразу после заполнения, до вывода глифов
                POP AF
                LD (@StationRaster.FillMode), A
                ; установка трёхпиксельного отступа счётчика в настроенном окне
                LD A, #03
                LD (@TextWindow.CursorX), A
                ; чтение High и MidHigh одним словом с физически младшим MidHigh
                LD BC, (@StationTimer.Counter.MidHigh)
                ; расчёт старшего разряда High через выделение и поворот полубайта
                LD A, B
                AND @CounterDrawConst.HighNibble
                RRCA
                RRCA
                RRCA
                RRCA
                ; расчёт кода символа прибавлением ASCII-нуля, допустимость BCD не проверяется
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; расчёт младшего разряда High из сохранённого B
                LD A, B
                AND @CounterDrawConst.LowNibble
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; расчёт старшего разряда MidHigh из сохранённого C
                LD A, C
                AND @CounterDrawConst.HighNibble
                RRCA
                RRCA
                RRCA
                RRCA
                ; расчёт кода старшего разряда MidHigh
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; расчёт младшего разряда MidHigh
                LD A, C
                AND @CounterDrawConst.LowNibble
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; вывод первого разделителя после четырёх старших разрядов
                LD A, @CounterDrawConst.Separator
                CALL @Station.DrawGlyph.Entry
                ; чтение MidLow отдельно от уже выведенных старших пар
                LD A, (@StationTimer.Counter.MidLow)
                LD C, A
                ; расчёт старшего разряда MidLow с переводом полубайта вниз
                AND @CounterDrawConst.HighNibble
                RRCA
                RRCA
                RRCA
                RRCA
                ; расчёт кода старшего разряда MidLow
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; расчёт младшего разряда MidLow из сохранённой пары
                LD A, C
                AND @CounterDrawConst.LowNibble
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; вывод второго разделителя перед Low
                LD A, @CounterDrawConst.Separator
                CALL @Station.DrawGlyph.Entry
                ; чтение Low после вывода остальных частей счётчика
                LD A, (@StationTimer.Counter.Low)
                LD C, A
                ; расчёт старшего разряда Low с переводом полубайта вниз
                AND @CounterDrawConst.HighNibble
                RRCA
                RRCA
                RRCA
                RRCA
                ; расчёт кода старшего разряда Low
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                ; расчёт младшего разряда Low перед последним глифом
                LD A, C
                AND @CounterDrawConst.LowNibble
                ADD A, @NumberConst.DigitZero
                CALL @Station.DrawGlyph.Entry
                RET

                endmodule
                endmodule
