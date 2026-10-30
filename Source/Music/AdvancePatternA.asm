                module Music
                module AdvancePatternA
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Обновление счётчика нот канала A, перехода позиции и трёх указателей паттернов
; исходная запись 10, файловые смещения #047F..#04E2
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   счётчик текущей ноты находится по #DE1E, нулевой байт потока A требует следующей позиции
;   список позиций заканчивается #FF, после него выбирается указатель петли из операнда #DF9F
;   значение позиции задаёт индекс тройки указателей A, B, C, относительные адреса складываются с началом модуля
;   указатель A сохраняется в #DF89, B и C в #E393 и #E3C4, общий размер тройки шесть байтов
; -----------------------------------------
                ; проверка истечения длительности текущей ноты перед разбором очередной команды канала A
Entry:          LD HL, #DE1E
                DEC (HL)
                LD H, E
                LD B, E
                EXX
                JR NZ, @Music.AdvancePatternA.PointDFCD                         ; переход, если счётчик длительности ноты канала A ещё не обнулился


                LD DE, #DC10
                LD A, (DE)
                OR A
                JR NZ, @Music.AdvancePatternA.PointDFBF                         ; переход, если поток канала A ещё не содержит признак конца паттерна


                LD (#DF67), A
                LD D, A
                LD (#DFBD), SP
                LD HL, #E7C9
                LD A, (HL)
                INC A
                JR NZ, @Music.AdvancePatternA.PointDFA1                         ; переход, если байт списка позиций не равен маркеру #FF


                LD HL, #E7C9
                ; чтение новой позиции и сохранение указателя на следующий байт списка
PointDFA1:      LD E, (HL)
                INC HL
                LD (#DF98), HL
                LD HL, #0000
                ; расчёт адреса тройки указателей паттернов, индекс позиции умножается на два
                ADD HL, DE
                ADD HL, DE
                LD SP, HL
                POP HL
                LD BC, #0000
                ADD HL, BC
                EX DE, HL
                POP HL
                ADD HL, BC
                LD (#E393), HL
                POP HL
                ADD HL, BC
                LD (#E3C4), HL
                LD SP, #0000
PointDFBF:      LD H, #DB
                CALL @Music.UnknownE439.Entry
                LD (#DF89), DE
                LD A, #00
                LD (#DE1E), A
PointDFCD:      LD A, #01
                DJNZ @Music.AdvancePatternA.PointDFD3

                LD A, #22
PointDFD3:      LD (#DE2E), A
                EXX
                LD A, B
                LD (#DE61), A
                LD A, H
                LD (#DE31), A
                LD A, E
                LD (#DE72), A
                ; JP @Music.RenderChannelA.Entry, продолжение в RenderChannelA.asm

                endmodule
                endmodule
