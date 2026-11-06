                module Action
                module IncreaseGaugeWord
                ; Документация [алгоритм и проверка](../../Docs/ActionKeyGaugeIncrease.md)
                ; -----------------------------------------
                ; Увеличение слова шестой шкалы с исходными клавиатурными ограничениями
                ; исходная запись 17, адреса 7680..76A2
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают
                ;   SkipDetail, MotionOpcode и SignedWord доступны, LimitWord является стабильным изменяемым операндом этого входа
                ;   перенесённый код доступен в фиксированном банке 5, CPU-стек содержит внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   при SkipDetail не ноль A=SkipDetail, F соответствует OR A, HL, DE и BC сохраняются
                ;   иначе при MotionOpcode не 3A A=MotionOpcode, F соответствует CP 3A, HL, DE и BC сохраняются
                ;   иначе HL=(SignedWord+8) AND FFFF, DE=LimitWord, BC сохранён
                ;   если знак обёрнутой разности HL-LimitWord отрицателен, SignedWord=HL, SixthRequest=1 и A=1, иначе память сохранена и A=3A
                ;   F сохраняет S/Z/PV от SBC и получает остальные биты от обратного ADD, точная формула приведена в документации
                ;   R получает 3, 6, 15 либо 19 M1 в зависимости от пути, бит 7 R сохраняется
                ;   HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и 7FFD сохраняются, CPU-стек не записывается
                ; Corrupt:
                ;   HL, DE, AF, R, при записи SignedWord и SixthRequest
                ; Note:
                ;   все пары SkipDetail и MotionOpcode проверены для обоих входов, все 65536 слов проверены для уменьшения и семи границ увеличения
                ;   все 65536 ограничений проверены отдельно, точные регистры включая R, записи и восемь банков RAM сопоставлены
                ;   исходное знаковое условие не заменяется общим насыщением, переполнения слова сохраняются
                ;   полное произведение слова и ограничения, игровые единицы, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Проверка общего запроса SkipDetail, ненулевой байт запрещает увеличение слова.
Entry:          LD A, (@ActionProjectionClipState.SkipDetail)
                OR A
                RET NZ                                                          ; выход, если SkipDetail ненулевой, сохранить слово и запрос шкалы

                ; Проверка исходного опкода 3A координатной цепочки, остальные байты не допускают изменение.
                LD A, (@ActionGaugeWordKeysState.MotionOpcode)
                CP @ActionGaugeKeyConst.MotionOpcode
                RET NZ                                                          ; выход, если MotionOpcode отличается от 3A, сохранить слово

                ; Расчёт кандидата SignedWord+8 по модулю 65536.
                LD HL, (@ActionPanelGaugesState.SignedWord)
                LD DE, @ActionGaugeKeyConst.StepWord
                ADD HL, DE
                ; Чтение изменяемого LimitWord, исходное значение 0088 может восстанавливаться падающим фронтом запроса.
                LD DE, @ActionControlDecayConst.ResetWord
                ; Проверка знака обёрнутой разности кандидата и ограничения, Carry предварительно очищается.
                OR A
                SBC HL, DE
                ; Восстановление кандидата обратным сложением, флаг Sign остаётся от SBC.
                ADD HL, DE
                RET P                                                           ; выход, если разность кандидата и ограничения неотрицательна по биту 15, сохранить SignedWord

                ; Обновление SignedWord только после исходной знаковой проверки.
                LD (@ActionPanelGaugesState.SignedWord), HL
                ; Создание запроса перерисовки шестой шкалы после изменения слова.
                LD A, @ActionControlDecayConst.RequestOn
                LD (@ActionPanelGaugesState.SixthRequest), A
                RET

                endmodule
                endmodule
