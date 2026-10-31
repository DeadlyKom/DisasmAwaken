                module Station
                module GenerateMissionOffer
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [пересев RNG, чтение ROM и два произведения награды](../../Docs/MissionOffer.md)
; -----------------------------------------
; Генерация координат предложения, требуемого тоннажа и награды по расстоянию
; исходная запись 4, файловые смещения #4C14..#4C73
; In:
;   SignatureInput.Entry содержит текущие FirstWord и SecondWord, младший байт RandomStates.Seed1 доступен
;   банковая тень и аппаратная страница согласованы, выбраны банк 0 и ROM 1, bit5 порта снят
;   ROM[0..FF] читаема как данные и не меняется, выбранные страницы KARTA и Station доступны
;   для возврата требуется, чтобы последовательность RNG встретила ROM-байт не меньше 8
;   код и данные допускают запись полей предложения и трёх байтов Seed1, CPU-стек вне банкового окна
; Out:
;   HL старшее слово полного произведения distance*20*RequiredTonnage, DE младшее слово этого произведения
;   BC содержит выход MeasureCoordinateDistance при distance*20<256, иначе B сохранён от этого выхода, C=0
;   AF - A=(входная CurrentPage AND F8) OR 10, F от последнего OR банкового интерфейса
;   MissionOffer.Entry.FirstWord=current.FirstWord, SecondWord=слово последнего принятого NextRandom1
;   RequiredTonnage=ROM[lowT]>>3, значение 1..31, Reward=(distance*20*RequiredTonnage) AND FFFF
;   MessageIndex=0, четыре UnknownWord04..UnknownWord0A между ключом и наградой не меняются
;   HL'=адрес RandomStates.Seed1, DE'=current.FirstWord, BC'=current.SecondWord
;   AF' соответствует MeasureCoordinateDistance, при нулевом расстоянии либо раннем переполнении сохранён
;   IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
;   аппаратная страница и тень выбирают сначала KARTA 1, затем Station 0 с сохранением старших битов и ROM 1
;   Seed1 содержит последнее новое слово и HighByte, MapState.LastDistance результат вызванного измерителя
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF' по арифметическому пути
; Note:
;   перед каждой попыткой current.SecondWord записывается в Seed1.LowWord+1 и Seed1.HighByte, младший байт Seed1 сохраняется
;   после NextRandom1 альтернативный B равен нулю, C равен lowT, поэтому EXX и LD A,(BC) читают именно ROM[lowT]
;   нулевой результат после трёх SRL отвергается, повтор выполняется без ограничения числа попыток
;   оба ключа расстояния имеют одинаковый FirstWord, отличаются только словом текущего и случайного SecondWord
;   код FF от MeasureCoordinateDistance не отвергается и участвует в награде как число 255
;   старшее слово второго произведения не проверяется, максимальное 255*20*31 равно 158100 и может обернуть Reward
;   четыре промежуточных слова и смысл MessageIndex остаются неустановленными, физическая структура этого не скрывает
;   ROM из исследовательской модели не объявляется ROM эмулятора Unreal, нативный запуск генератора не подтверждён
; -----------------------------------------
                ; чтение текущего первого слова ключа, оно остаётся общим для текущего и предлагаемого пункта
Entry:          LD HL, (@SignatureInput.Entry.FirstWord)
                ; сохранение первого слова в физическом состоянии предложения
                LD (@MissionOffer.Entry.FirstWord), HL
                ; чтение текущего второго слова для частичного пересева независимого потока 1
                LD DE, (@SignatureInput.Entry.SecondWord)
                ; перезапись старших двух байтов Seed1, младший байт прежнего состояния не меняется
                LD (@RandomStates.Seed1.LowWord + 1), DE
                ; расчёт следующего слова RNG с рабочими альтернативными HL, DE и BC
                CALL @Station.NextRandom1.Entry
                ; сохранение нового второго слова предлагаемого пункта до проверки тоннажа
                LD (@MissionOffer.Entry.SecondWord), HL
                ; обнуление MessageIndex перед проверкой каждого нового кандидата
                XOR A
                LD (@MissionOffer.Entry.MessageIndex), A
                ; выбор рабочего BC генератора, B=0 и C=lowT дают адрес первого ROM-страничного блока
                EXX
                ; чтение ROM[lowT] как исходного байта для требуемого тоннажа
                LD A, (BC)
                ; расчёт пятибитного тоннажа тремя логическими сдвигами ROM-байта
                SRL A
                SRL A
                SRL A
                ; проверка ненулевого тоннажа перед принятием кандидата
                CP #00
                JP Z, @Station.GenerateMissionOffer.Retry                       ; переход, если ROM-байт дал нулевой тоннаж, повторить генерацию с новым младшим байтом Seed1

                ; сохранение принятого тоннажа 1..31 в физическом состоянии предложения
                LD (@MissionOffer.Entry.RequiredTonnage), A
                ; выбор KARTA в банке 1 для арифметики расстояния
                LD A, #11
                CALL @Station.SelectRamBank.Entry
                ; подготовка текущего ключа и перенос его в альтернативные DE и BC
                LD DE, (@SignatureInput.Entry.FirstWord)
                LD BC, (@SignatureInput.Entry.SecondWord)
                EXX
                ; подготовка предлагаемого ключа в основных DE и BC по договору MeasureCoordinateDistance
                LD DE, (@MissionOffer.Entry.FirstWord)
                LD BC, (@MissionOffer.Entry.SecondWord)
                ; расчёт масштабированного расстояния, FF переполнения здесь остаётся числовым множителем
                CALL @Map.MeasureCoordinateDistance.Entry
                ; расширение байтового расстояния в положительное слово для первого умножения
                LD H, #00
                LD L, A
                ; выбор исходного коэффициента награды 20 за единицу расстояния и тоннажа
                LD DE, @MissionOfferConst.RewardScale
                ; расчёт первого произведения distance*20 в младшем выходном слове DE
                CALL @Map.MultiplySigned16.Entry
                ; расширение принятого тоннажа в положительный множитель HL
                LD H, #00
                LD A, (@MissionOffer.Entry.RequiredTonnage)
                LD L, A
                ; расчёт полного произведения первого результата на требуемый тоннаж
                CALL @Map.MultiplySigned16.Entry
                ; сохранение только младшего слова награды, старшее HL не проверяется
                LD (@MissionOffer.Entry.Reward), DE
                ; возврат станционного банка 0, основной AF заменяется статусом выбора страницы
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET

                ; повтор с новым младшим байтом Seed1, число попыток исходником не ограничивается
Retry:          JP @Station.GenerateMissionOffer.Entry

                endmodule
                endmodule
