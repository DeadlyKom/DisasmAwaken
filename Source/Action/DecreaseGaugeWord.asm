                module Action
                module DecreaseGaugeWord
                ; Документация [алгоритм и проверка](../../Docs/ActionKeyGaugeDecrease.md)
                ; -----------------------------------------
                ; Уменьшение слова шестой шкалы с исходными клавиатурными ограничениями
                ; исходная запись 17, адреса 76A3..76C6
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают
                ;   SkipDetail, MotionOpcode и SignedWord доступны, старшее и младшее слова SignedWord не меняются параллельно
                ;   перенесённый код доступен в фиксированном банке 5, CPU-стек содержит внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   при MotionOpcode не 3A A=MotionOpcode, F соответствует CP 3A, HL, DE и BC сохраняются
                ;   иначе при SkipDetail не ноль A=SkipDetail, F соответствует AND A, HL, DE и BC сохраняются
                ;   иначе HL=SignedWord, DE=8, BC сохранён, отрицательное слово с нулевым битом 4 младшего байта не записывается
                ;   при этом отказе A=0, F=54 OR (L AND 28), в остальных случаях HL=(SignedWord-8) AND FFFF
                ;   при записи SignedWord=HL, SixthRequest=1, A=1, F соответствует 16-битному вычитанию с Carry=0
                ;   R получает 3, 6, 14, 18 либо 21 M1 в зависимости от пути, бит 7 R сохраняется
                ;   HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и 7FFD сохраняются, CPU-стек не записывается
                ; Corrupt:
                ;   HL, DE, AF, R, при записи SignedWord и SixthRequest
                ; Note:
                ;   все пары SkipDetail и MotionOpcode проверены для обоих входов, все 65536 слов проверены для уменьшения и семи границ увеличения
                ;   все 65536 ограничений проверены отдельно, точные регистры включая R, записи и восемь банков RAM сопоставлены
                ;   исходное знаковое условие не заменяется общим насыщением, переполнения слова сохраняются
                ;   полное произведение слова и ограничения, игровые единицы, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Проверка опкода координатной цепочки до чтения общего запроса.
Entry:          LD A, (@ActionGaugeWordKeysState.MotionOpcode)
                CP @ActionGaugeKeyConst.MotionOpcode
                RET NZ                                                          ; выход, если MotionOpcode отличается от 3A, сохранить слово

                ; Проверка общего запроса SkipDetail через AND A, флаг H отличается от OR увеличивающего входа.
                LD A, (@ActionProjectionClipState.SkipDetail)
                AND A
                RET NZ                                                          ; выход, если SkipDetail ненулевой, сохранить слово и запрос шкалы

                ; Чтение слова и проверка знака, отрицательная половина имеет дополнительное условие допуска.
                LD HL, (@ActionPanelGaugesState.SignedWord)
                BIT @ActionAbs32Const.SignBit, H
                LD DE, @ActionGaugeKeyConst.StepWord
                JR Z, @Action.DecreaseGaugeWord.SubtractStep                    ; переход, если слово неотрицательное, уменьшить его без проверки младшего бита 4

                ; Проверка бита 4 младшего байта отрицательного слова, это исходное побитовое условие.
                BIT @ActionGaugeKeyConst.NegAllowBit, L
                RET Z                                                           ; выход, если у отрицательного слова бит 4 младшего байта нулевой, сохранить SignedWord

                ; Расчёт SignedWord-8 с предварительно очищенным Carry.
SubtractStep:   OR A
                SBC HL, DE
                ; Обновление SignedWord результатом вычитания по модулю 65536.
                LD (@ActionPanelGaugesState.SignedWord), HL
                ; Создание запроса перерисовки шестой шкалы после изменения слова.
                LD A, @ActionControlDecayConst.RequestOn
                LD (@ActionPanelGaugesState.SixthRequest), A
                RET

                endmodule
                endmodule
