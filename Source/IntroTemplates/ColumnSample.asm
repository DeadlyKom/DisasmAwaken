                module IntroTemplates
                module ColumnSample
; Документация [IntroTemplates](../../Docs/FunctionDetails/IntroTemplates.md)
; -----------------------------------------
; 25-байтовый образец выборки и семи вертикальных записей, 64 копии по адресу #D000
; исходная запись 3, файловые смещения #085A..#0872
; In:
;   HL - накопитель координаты, DE - D задаёт таблицу, BC - шаг координаты
;   HL', DE', BC' - таблицы косвенной адресации, назначения и добавки фаз
; Out:
;   выбранный байт записан в семь адресов с одним E и последовательными D
; Corrupt:
;   HL, DE, AF, HL', DE'
; Note:
;   основной HL увеличивается на BC, его старший байт выбирает значение из таблицы D
;   два добавления в A и две косвенные выборки задают байт и начальную страницу назначения
;   второй EXX возвращает исходное расположение регистров, перехода или RET в образце нет
; -----------------------------------------
Entry:          ADD HL, BC
                LD E, H
                LD A, (DE)
                EXX
                ADD A, B
                LD L, A
                LD D, (HL)
                ADD A, C
                LD L, A
                LD A, (HL)
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC E
                EXX
                endmodule
                endmodule
