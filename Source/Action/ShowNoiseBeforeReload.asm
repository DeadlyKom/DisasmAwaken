                module Action
                module ShowNoiseBeforeReload
                ; Документация [алгоритм и проверка](../../Docs/ActionNoiseExit.md)
                ; -----------------------------------------
                ; Вывод шумовых кадров и ожидание клавиши перед загрузкой станции
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0291..#02EA
                ; In:
                ;   банк 0 выбран, банк 1 содержит CONTROL и запись очереди #F2A5, ROM 1 доступен
                ;   стек в общей RAM, для каждого HALT требуется пробуждение, клавиатура читается через порт #00FE
                ; Out:
                ;   в очередь передан элемент #F2A5, курсор AY установлен на #EE4D
                ;   после не менее ста кадров любой нулевой бит из младших пяти ведёт к AAC4 при восстановленном SP
                ;   I получает #3F, IY инициализируется #5C3A, перед передачей выбрана страница 0
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF, R, буфер, экран, очередь, AY и временные слова стека
                ; Note:
                ;   начало чтения ROM равно #0500 плюс байт R, на кадр копируются 3072 байта
                ;   модель проверяет реальное копирование, вывод, AY и ввод клавиши, HALT пробуждается явно, IRQ не исполняются
                ; -----------------------------------------
                ; Постановка элемента текста в очередь CONTROL.
Entry:          PUSH DE
                LD DE, #F2A5
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Выбор звукового потока и подготовка режима ожидания.
                LD HL, #EE4D
                LD (#ECF6), HL
                LD A, #3F
                LD I, A
                LD IY, #5C3A
                LD B, #64
                ; Копирование очередного фрагмента ROM в линейный буфер.
DrawFrame:      PUSH BC
                LD DE, #8000
                LD A, R
                LD L, A
                LD H, #05
                LD BC, #0C00
                LDIR
                ; Ожидание пробуждения перед выводом готового кадра.
                EI
                HALT
                DI
                ; Вывод буфера и шага текста в CONTROL, затем обновление AY в ACTION.
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL #C870
                CALL @Controls.ConsumeTextQueue.Entry
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UpdateAyEffects.Entry
                POP BC
                ; Проверка окончания обязательной задержки.
                DEC B
                JP NZ, @Action.ShowNoiseBeforeReload.PollDuringDelay            ; переход, если обязательные кадры ещё не закончились

                ; Проверка клавиши после обязательной задержки.
                LD B, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR Z, @Action.ShowNoiseBeforeReload.DrawFrame                   ; переход, если младшие пять битов равны единице, ждать ещё кадр

                JP @Action.UpdateFrame.PointAAC4

                ; Опрос клавиатуры во время задержки, результат не выбирает следующий путь.
PollDuringDelay:LD A, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR @Action.ShowNoiseBeforeReload.DrawFrame

                endmodule
                endmodule
