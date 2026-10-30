                module Station
                module PrintPlayerRank
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [пороговые записи, строки и полный выбор ранга](../../Docs/PlayerRank.md)
; -----------------------------------------
; Печать подписи и ранга по шестнадцатибитному счётчику и шести порогам
; исходная запись 4, файловые смещения #4C74..#4CE2
; In:
;   RankState.Score содержит беззнаковый счётчик ранга, таблица RankThresholds имеет шесть исходных записей
;   TextWindow и рисователь удовлетворяют PrintText, подпись и семь LF-строк доступны в банке станции 0
; Out:
;   HL позиция продолжения последнего PrintText выбранного имени, DE прочитанный RankState.Score
;   BC - C число пропущенных порогов 0..6, B=6-C, при найденном пороге он включён в остаток
;   AF статус последнего PrintText, при полном достижении LF A=0A, F=4A
;   при счётчике меньше 30 выбирается исходная строка Rookie, иначе первый достигнутый убывающий порог
;   альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2
;   курсор, окно и bitmap содержат эффекты печати подписи и выбранного имени по PrintText
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   пороги 10000,3000,1000,300,100,30 хранятся старшим байтом вперёд, это не native DW Z80
;   сравнение беззнаковое, равенство выбирает найденный более высокий ранг
;   первая печать подписи выполняется через CALL, последний вывод имени через JP с исходным возвратом
;   отказ первого PrintText не отменяет дальнейший поиск ранга, его возвращённый AF не проверяется
;   изменение счётчика и игровые причины его роста этим рисователем не устанавливаются
;   процедура отделена от генератора AC14 по существующему независимому входу AC74, байты и адреса сохранены
; -----------------------------------------
                ; выбор подписи ранга перед поиском пороговой записи
Entry:          LD HL, @RankCaption.Entry
                CALL @Station.PrintText.Entry
                ; выбор шести убывающих порогов и нулевого числа пропущенных уровней
                LD B, @RankConst.ThresholdCount
                LD C, #00
                ; поиск начинается с физической записи наивысшего порога 10000
                LD HL, @RankThresholds.Score10000
                ; чтение рангового счётчика, младший байт в E, старший в D
                LD DE, (@RankState.Score)
                ; проверка старшего байта счётчика относительно старшего байта текущего порога
CompareHigh:    LD A, D
                CP (HL)
                JP Z, @Station.PrintPlayerRank.CompareLow                       ; переход, если старшие байты равны, сравнить младшие

                JP NC, @Station.PrintPlayerRank.SelectText                      ; переход, если старший байт счётчика больше старшего байта порога, уровень достигнут

                ; пропуск младшего байта недостигнутого порога перед следующей записью
                INC HL
                JP @Station.PrintPlayerRank.NextThreshold

                ; проверка младшего байта при равных старших байтах счётчика и порога
CompareLow:     LD A, E
                INC HL
                CP (HL)
                JP NC, @Station.PrintPlayerRank.SelectText                      ; переход, если младший байт счётчика не меньше младшего байта порога, уровень достигнут

                ; выбор следующего порога с увеличением числа пропущенных уровней
NextThreshold:  INC HL
                INC C
                DJNZ @Station.PrintPlayerRank.CompareHigh

                ; проверка номера выбранного уровня после поиска либо исчерпания шести порогов
SelectText:     LD A, C
                OR A
                JP Z, @Station.PrintPlayerRank.Show10000                        ; переход, если достигнут первый порог 10000, вывести высший ранг

                ; проверка уровня порога 3000
                CP #01
                JP Z, @Station.PrintPlayerRank.Show3000                         ; переход, если пропущен один порог, вывести ранг от 3000

                ; проверка уровня порога 1000
                CP #02
                JP Z, @Station.PrintPlayerRank.Show1000                         ; переход, если пропущены два порога, вывести ранг от 1000

                ; проверка уровня порога 300
                CP #03
                JP Z, @Station.PrintPlayerRank.Show300                          ; переход, если пропущены три порога, вывести ранг от 300

                ; проверка уровня порога 100
                CP #04
                JP Z, @Station.PrintPlayerRank.Show100                          ; переход, если пропущены четыре порога, вывести ранг от 100

                ; проверка уровня порога 30
                CP #05
                JP Z, @Station.PrintPlayerRank.Show30                           ; переход, если пропущены пять порогов, вывести ранг от 30

                ; выбор исходного низшего ранга при счётчике меньше 30
                LD HL, @RankTexts.Rookie
                JP @Station.PrintText.Entry

Show10000:      LD HL, @RankTexts.Score10000
                JP @Station.PrintText.Entry

Show3000:       LD HL, @RankTexts.Score3000
                JP @Station.PrintText.Entry

Show1000:       LD HL, @RankTexts.Score1000
                JP @Station.PrintText.Entry

Show300:        LD HL, @RankTexts.Score300
                JP @Station.PrintText.Entry

Show100:        LD HL, @RankTexts.Score100
                JP @Station.PrintText.Entry

Show30:         LD HL, @RankTexts.Score30
                JP @Station.PrintText.Entry

                endmodule
                endmodule
