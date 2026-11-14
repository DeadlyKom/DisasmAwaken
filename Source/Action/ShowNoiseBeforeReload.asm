                module Action
                module ShowNoiseBeforeReload
                ; Документация [алгоритм и проверка](../../Docs/ActionNoiseExit.md)
                ; -----------------------------------------
                ; Вывод шумовых кадров и ожидание клавиши перед загрузкой станции
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0291..#02EA
                ; In:
                ;   банк 0 выбран, банк 1 содержит CONTROL и запись очереди #F2A5, ROM 1 доступен
                ;   стек в общей RAM, проверенный путь использует ROM-обработчик IM 1, клавиатура читается через порт #00FE
                ; Out:
                ;   в очередь передан элемент #F2A5, курсор AY установлен на #EE4D
                ;   после не менее ста кадров любой нулевой бит из младших пяти ведёт к AAC4 при восстановленном SP
                ;   I получает #3F, IY получает #5C3A перед первым HALT и последние два байта буфера после каждого вывода
                ;   перед передачей выбрана страница 0 и IFF сброшен
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF, R, буфер, экран, очередь, AY и временные слова стека
                ;   системные байты ROM и память по IY + #40 при переполнении младшего слова FRAMES
                ; Note:
                ;   начало чтения ROM равно #0500 плюс байт R, на кадр копируются 3072 байта
                ;   после первого вывода ROM принимает IY из растра, при переполнении FRAMES INC (IY + #40) может записать в банк 0
                ;   ROM 128K дополнительно читает бит 4 из (IY + #01), фактические адреса зависят от предыдущего растра
                ;   при установленном бите 4 ROM 128K входит в #3A42, на чётном FRAMES эта ветвь опрашивает регистр 14 AY
                ;   при декодировании клавиши обе ROM читают (IY + #07) и ставят бит 5 в (IY + #01)
                ;   при переполнении ROM может увеличить байт переходника #5CC2, байт #5F3D или младший байт самого FRAMES
                ;   если при переполнении IY=#ED3F, ROM меняет выбор регистра AY 10, следующий тик записывает уровень C в регистр 6
                ; -----------------------------------------
                ; Постановка элемента текста в очередь CONTROL.
Entry:          PUSH DE
                LD DE, @ControlsFlightText.ShipDestroyed
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Выбор звукового потока и подготовка режима ожидания.
                LD HL, @ActionAyStreams.WaitLoopRow00
                LD (@ActionAyEffectsState.CursorB), HL
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
                CALL @Controls.CopyViewportToScreen.Entry
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

                JP @Action.UpdateFrame.ReloadStation

                ; Опрос клавиатуры во время задержки, результат не выбирает следующий путь.
PollDuringDelay:LD A, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR @Action.ShowNoiseBeforeReload.DrawFrame

                endmodule
                endmodule
