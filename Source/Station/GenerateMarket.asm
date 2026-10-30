                module Station
                module GenerateMarket
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [формулы запасов и цен, два режима маркера и проверка исходного кода](../../Docs/MarketGeneration.md)
; -----------------------------------------
; Генерация запасов, маркеров и цен тридцати двухбайтовых строк рынка
; исходная запись 4, файловые смещения #491B..#49F2
; In:
;   SignatureInput.Entry содержит текущие FirstWord, SecondWord и Variant
;   MarketState.MarkMode равен #80 для нового маркера либо 0 для сохранения прежнего bit7
;   байт #983D участвует в Seed1.HighByte после AND #FC, его игровые единицы не установлены
;   таблицы #94DC и #9518 исходные, массив #9555..#9590 доступен для записи
;   действует банковый договор DescribeCurrentKey, прерывания не меняют рабочие состояния
; Out:
;   HL=#9590, DE и BC зависят от выбранного пути, точные варианты приведены в MarketGeneration.md
;   AF - при генерации A=#FA, F=#43, при очистке A=0 либо 4, F=#40
;   при генерации IX=#954E, HL'= #94F7, D'=старший байт последнего случайного слова, E'=0 либо 8
;   при очистке IX и альтернативные HL, DE, BC сохранены, Seed1 не изменяется
;   IY, I и IFF сохранены, SP восстановлен, рабочий ключ изменяется во всех случаях
;   AF' содержит банковый результат DescribeCurrentKey, #7FFD и его тень возвращают банк 0 с ROM 1
;   при генерации изменяются Seed1 и два операнда MinorCode и MajorCode, маркер #9591 сохранён
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX
; Note:
;   27 обычных записей рассчитываются, три последние получают нулевой запас и фиксированные цены
;   цены 1..4 допустимы, 5 является запасным значением при неположительном результате, а не нижней границей
;   игровое значение bit7 запаса не доказано, это маркер с наблюдаемым влиянием на вывод и текстовый запрос
;   режимы кроме 0 и #80 не подтверждены вызывающим кодом, исходные байты не изменены
; -----------------------------------------
                ; получение числовых признаков текущего ключа через настоящий банк MAP
Entry:          CALL @Station.DescribeCurrentKey.Entry
                JR Z, @Station.ClearMarketRows.Entry                            ; переход, если исходная свёртка ключа не допускает генерацию, очистить все строки

                LD A, H
                ; проверка внешней геометрической области, для неё H принудительно равен 4
                CP #04
                JR Z, @Station.ClearMarketRows.Entry                            ; переход, если ключ находится вне трёх областей, очистить все строки

                ; обновление операнда MajorCode числовым признаком H
                LD (@MarketState.MajorCode), A
                LD A, E
                ; обновление операнда MinorCode младшим двухбитовым признаком E
                LD (@MarketState.MinorCode), A
                ; создание начального младшего слова Seed1 из текущего SecondWord
                LD HL, (@SignatureInput.Entry.SecondWord)
                LD (@RandomStates.Seed1.LowWord), HL
                ; расчёт HighByte потока как (#983D AND #FC) XOR Variant, единицы #983D ещё не установлены
                LD A, (#983D)
                AND #FC
                LD C, A
                LD A, (@SignatureInput.Entry.Variant)
                XOR C
                LD (@RandomStates.Seed1.HighByte), A
                ; выбор 27 категорий, указатель сохраняется в альтернативном HL между случайными шагами
                LD HL, @MarketCategories.Category00
                EXX
                ; выбор двухбайтовых правил и первого поля Price выходного массива
                LD IX, @MarketRules.Rule00
                LD HL, @MarketRows.Row00.Price
                ; выбор числа рассчитываемых строк, ещё три строки заполняются отдельно
                LD B, #1B
                ; сохранение адреса цены и указателя категории перед NextRandom1, изменяющим альтернативные пары
NextRow:        PUSH HL
                EXX
                PUSH HL
                EXX
                ; получение нового слова Seed1, младший байт задаёт колебание цены, старший запас и маркер
                CALL @Station.NextRandom1.Entry
                EXX
                POP HL
                EXX
                ; расчёт амплитуды колебания 0..7 из младшего случайного байта
                LD A, L
                AND #07
                ; проверка знака колебания по bit7 того же случайного байта
                BIT 7, L
                JR Z, @Station.GenerateMarket.AddBasePrice                      ; переход, если bit7 случайного байта снят, прибавить положительное колебание

                ; расчёт отрицательного колебания, ноль остаётся нулём
                NEG
                ; расчёт промежуточной цены по модулю 256 из BasePrice и знакового колебания
AddBasePrice:   ADD A, (IX + @FMarketRule.BasePrice)
                LD E, H
                POP HL
                LD D, A
                EXX
                ; чтение самомодифицированного MinorCode и сравнение с категорией текущей строки
                LD A, #00
                CP (HL)
                INC HL
                ; выбор нулевой поправки для несовпадающей категории
                LD E, #00
                JR NZ, @Station.GenerateMarket.ApplyBonus                       ; переход, если категория отличается от MinorCode, оставить поправку нулевой

                ; выбор поправки 8 одновременно для цены и количества совпавшей категории
                LD E, #08
                ; расчёт цены после вычета категорийной поправки в альтернативном E
ApplyBonus:     EXX
                LD A, D
                EXX
                SUB E
                EXX
                JR Z, @Station.GenerateMarket.UsePriceFive                      ; переход, если цена после поправки равна нулю, подставить 5

                JR NC, @Station.GenerateMarket.StoreBasePrice                   ; переход, если цена строго больше поправки, сохранить положительный результат

                ; выбор запасной цены 5 при нуле либо заёме, меньшие положительные цены не отбрасываются
UsePriceFive:   LD A, #05
                ; сохранение промежуточной цены перед расчётом запаса
StoreBasePrice: LD (HL), A
                DEC HL
                ; чтение числового правила StockRule, это код выбора маски, а не независимые флаги
                LD A, (IX + @FMarketRule.StockRule)
                ; проверка правила 0, выбирающего маску #3F
                AND A
                LD D, #3F
                JR Z, @Station.GenerateMarket.MaskRandom                        ; переход, если StockRule равен 0, применить маску #3F

                ; проверка правила 1, условно допускающего старший маркер
                DEC A
                JR NZ, @Station.GenerateMarket.RuleAtLeastTwo                   ; переход, если StockRule отличается от 1, проверить правила 2 и выше

                LD A, E
                ; проверка двух старших разрядов случайного байта для правила 1
                AND #C0
                LD D, #BF
                JR Z, @Station.GenerateMarket.MaskRandom                        ; переход, если оба старших разряда сняты, использовать маску #BF

                ; выбор маски #3F при ненулевых старших разрядах и правиле 1
                LD D, #3F
                JR @Station.GenerateMarket.MaskRandom

                ; проверка правила 2, для него всегда выбирается маска #BF
RuleAtLeastTwo: DEC A
                LD D, #BF
                JR Z, @Station.GenerateMarket.MaskRandom                        ; переход, если StockRule равен 2, применить маску #BF

                ; проверка самомодифицированного MajorCode для правил 3 и выше
                LD A, #00
                AND A
                JR NZ, @Station.GenerateMarket.MaskRandom                       ; переход, если MajorCode ненулевой, оставить случайный байт без принудительного маркера

                ; обновление случайного байта для MajorCode=0, установить bit7 и снять bits5..4
                SET 7, E
                RES 5, E
                RES 4, E
                ; расчёт сырого запаса и отдельного маркера через выбранную маску
MaskRandom:     LD A, E
                AND D
                LD C, A
                RES 7, C
                ; выбор нового маркера через операнд MarkMode, 0 сохраняет старый маркер, #80 заменяет
                AND #80
                LD D, A
                ; расчёт количества max(сырой запас + категорийная поправка - 10, 0)
                LD A, C
                EXX
                ADD A, E
                SUB #0A
                JR NC, @Station.GenerateMarket.MergeMark                        ; переход, если сумма запаса и поправки не меньше 10, использовать разность

                ; обнуление количества при нехватке до порога 10
                XOR A
                ; объединение нового количества и разрешённого новым режимом маркера
MergeMark:      EXX
                OR D
                LD D, A
                ; расчёт маски сохранения старого bit7 как MarkMode XOR #80
                LD A, (@MarketState.MarkMode)
                XOR #80
                AND (HL)
                OR D
                ; обновление StockAndMark, прочие прежние разряды в двух поддержанных режимах не сохраняются
                LD (HL), A
                INC HL
                ; расчёт скидки min((StockAndMark >> 1) AND #3F, 8), Carry после RRA удаляется маской
                RRA
                AND #3F
                ; проверка верхней границы скидки 8
                CP #08
                JR C, @Station.GenerateMarket.SubtractPrice                     ; переход, если половина количества меньше 8, оставить вычисленную скидку

                LD A, #08
                ; расчёт обратной разности скидка - цена, затем NEG восстанавливает положительную цену
SubtractPrice:  SUB (HL)
                JR C, @Station.GenerateMarket.StorePrice                        ; переход, если цена больше скидки, сохранить положительную разность

                ; выбор #FB, после NEG дающий запасную цену 5
                LD A, #FB
                ; расчёт окончательной цены и запись поля Price
StorePrice:     NEG
                LD (HL), A
                ; переход к Price следующей двухбайтовой записи, предыдущее DEC HL уже учтено
                INC HL
                INC HL
                ; обновление указателя следующего двухбайтового правила
                INC IX
                INC IX
                ; проверка числа оставшихся обычных строк
                DEC B
                JP NZ, @Station.GenerateMarket.NextRow                          ; переход, если обработаны не все 27 рассчитываемых строк

                ; создание трёх последних строк, запас нулевой, цены только из BasePrice правил 27..29
                DEC HL
                LD (HL), #00
                INC HL
                LD A, (IX + @FMarketRule.BasePrice)
                LD (HL), A
                INC HL
                LD (HL), #00
                INC HL
                LD A, (IX + #02)
                LD (HL), A
                INC HL
                LD (HL), #00
                INC HL
                LD A, (IX + #04)
                LD (HL), A
                RET

                endmodule
                endmodule
