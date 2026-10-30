                module Station
                module FillRectangle
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Заполнение прямоугольника знакомест нулевыми или единичными пикселями без отсечения
; исходная запись 4, файловые смещения #6626..#66AF
; In:
;   DE - D высота в знакоместах 1..24, E ширина в байтах 1..32, BC - B строка 0..23, C колонка 0..31
;   B+D не больше 24, C+E не больше 32, таблицы #82..#84 подготовлены загрузчиком
;   StationRaster.FillMode - бит 0, ноль выбирает #FF, единица выбирает #00, биты 7..1 не используются этим входом
; Out:
;   HL сохранён, DE - D равен нулю, E сохранён, BC сохранён
;   AF - если B+D исходных параметров кратно восьми, A равен исходному C и F=#43, иначе A старший байт адреса следующей строки знакомест и F=#42
;   прямоугольник записан в bitmap #4000..#57FF, атрибуты не изменены
; Corrupt:
;   DE, AF
; Note:
;   каждое знакоместо состоит из восьми пиксельных строк, ширина задаётся пропуском 2*(32-E) байтов развёрнутого блока
;   в отличие от PrepareFrameRaster индексы здесь умножаются на восемь через SLA с отбрасыванием старших битов
;   RectangleByte и RectangleSkip меняются на каждом входе, функция не реентерабельна
;   все альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   отсечения нет, нулевая ширина или высота и выход за экран не входят в подтверждённый контракт
; -----------------------------------------
Entry:          PUSH HL
                PUSH BC
                ; расчёт байтового индекса строки знакомест умножением B на восемь
                LD L, B
                SLA L
                SLA L
                SLA L
                ; выбор старшего и младшего байтов адреса из соседних страниц таблицы строк
                LD H, @StationTables.RowHighPage
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                ; расчёт горизонтального табличного индекса умножением C на восемь
                LD L, C
                SLA L
                SLA L
                SLA L
                ; объединение младших вкладов экранной строки и колонки
                OR (HL)
                LD L, A
                LD H, B
                ; расчёт пропуска лишних пар записи, остаётся ровно E байтов в каждой строке
                LD A, @ScreenConst.ByteColumns
                SUB E
                ADD A, A
                LD (@StationRaster.RectangleSkip), A
                ; проверка бита 0 режима заполнения, остальные разряды на этот вход не влияют
                LD A, (@StationRaster.FillMode)
                RRA
                LD A, #FF
                JR NC, @Station.FillRectangle.SetFill                           ; переход, если бит 0 режима сброшен, сохраняется заполнение #FF

                ; выбор нулевого байта при установленном бите 0 режима
                INC A
                ; запись выбранного байта в изменяемый операнд внутреннего цикла
SetFill:        LD (@StationRaster.RectangleByte), A
                ; начало восьми пиксельных строк очередного знакоместа по высоте
CharRow:        LD C, @ScreenConst.PixelsPerChar
                ; сохранение исходной байтовой колонки перед развёрнутой записью
PixelRow:       LD B, L
                ; загрузка байта, выбранного через RectangleByte до начала рисования
                LD A, #00
                ; пропуск лишних пар записи через подготовленный RectangleSkip
                JR @Station.FillRectangle.SpanBody

                ; запись выбранного числа байтов одной пиксельной строки
SpanBody:       LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                ; восстановление исходной колонки перед следующей пиксельной строкой
                LD L, B
                INC H
                DEC C
                JP NZ, @Station.FillRectangle.PixelRow                          ; переход, если остаются пиксельные строки текущего знакоместа

                ; расчёт младшего байта адреса следующей строки знакомест
                LD A, L
                ADD A, @ScreenConst.ByteColumns
                LD L, A
                JR C, @Station.FillRectangle.NextChar                           ; переход, если младший байт переполнился, старшая часть уже соответствует следующей трети экрана

                ; компенсация восьми увеличений H внутри текущей трети экрана
                LD A, H
                SUB @ScreenConst.PixelsPerChar
                LD H, A
                ; проверка оставшейся высоты после полного знакоместа
NextChar:       DEC D
                JP NZ, @Station.FillRectangle.CharRow                           ; переход, если остаются строки знакомест прямоугольника

                POP BC
                POP HL
                RET

                endmodule
                endmodule
