                module Controls
                module ConsumeTextQueue
                ; Документация [вывод текстового окна](../../Docs/ControlsTextDisplay.md)
                ; -----------------------------------------
                ; Вывод очередного числа либо символа активной строки текстовой очереди
                ; исходная запись 23, банк 1, смещения #11C4..#1214
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают, состояние хранится в изменяемых операндах
                ;   выбран банк 1 с исходными CONTROL0 и CONTROL, код и экран доступны для записи
                ;   после InitializeTextWindow операнды прокрутки соответствуют окну x=160..255, y=144..189
                ;   на CPU-стеке лежит внешний возврат, вмешательство ISR в модель не включено
                ;   при прокрутке SP временно указывает на экран, обработчик прерываний не должен использовать этот SP
                ; Out:
                ;   активная строка имеет приоритет над поиском очередной записи
                ;   тип Free прекращает вызов, тип End переносит поиск на Slot00, занятый элемент сразу помечается Free
                ;   тип Number выводится целиком и увеличивает TextColumn ещё на один без рисования разделителя
                ;   обычный байт строки выводит один знак, LF завершает строку, CR прокручивает окно и продолжает этот же вызов
                ;   IX сохраняется
                ;   HL' и IY сохраняются, I, IM и IFF сохраняются, банковых переключений и портовых операций нет
                ;   внешний RET задаёт SP=входной SP+2, сама процедура DI не выполняет
                ; Corrupt:
                ;   HL, DE, BC, AF, DE', BC', AF', R, очередь, курсоры, экран и CPU-стек на путях вызовов
                ; Note:
                ;   нулевой байт строки является обычным кодом знака, завершителем служит 0A
                ;   поток из одних CR или некорректное кольцо могут не вернуть управление, встроенного лимита нет
                ; -----------------------------------------
                ; проверка изменяемого указателя активной строки перед чтением новой записи очереди
Entry:          LD HL, #0000
                LD A, H
                OR L
                JR NZ, @Controls.ConsumeTextQueue.ReadCharacter                 ; переход, если ActiveString не равен нулю, прочитать очередной символ

                ; выбор элемента после последней прочитанной записи, курсор хранится в операнде LD HL
                LD HL, #0000
                INC HL
                INC HL
ReadItem:       LD (@ControlsTextDisplayState.ReadCursor), HL
                LD A, (HL)
                ; проверка типа записи, 00 и 01 не содержат полезной нагрузки
                CP #02
                JR C, @Controls.ConsumeTextQueue.FreeOrEnd                      ; переход, если тип меньше Number, обработать свободную запись либо конец кольца

                ; освобождение занятой записи до вывода её числа либо строки
                LD (HL), #01
                LD D, A
                INC HL
                LD E, (HL)
                JR NZ, @Controls.ConsumeTextQueue.UseString                     ; переход, если тип больше Number, собрать указатель строки из D и E

                ; вывод числового байта с минимальной шириной два знака
                LD A, E
                CALL @Controls.PrintByteDecimal.Entry
                ; увеличение колонки на один для межчислового интервала без записи пустого знака
                LD A, (@ControlsTextDisplayState.TextColumn)
                INC A
                LD (@ControlsTextDisplayState.TextColumn), A
                RET

                ; проверка конечного маркера после исключения занятых типов
FreeOrEnd:      OR A
                RET NZ                                                          ; выход, если тип равен Free, следующая запись пока не готова

                ; возврат чтения к первому элементу после конечного маркера
                LD HL, @ControlsTextQueue.Slot00
                JP @Controls.ConsumeTextQueue.ReadItem

UseString:      EX DE, HL
                ; чтение символа и сохранение адреса следующего байта активной строки
ReadCharacter:  LD A, (HL)
                INC HL
                LD (@ControlsTextDisplayState.ActiveString), HL
                ; проверка LF как завершителя строки
                CP #0A
                JR Z, @Controls.ConsumeTextQueue.FinishString                   ; переход, если символ равен LF, сбросить ActiveString

                ; проверка CR как команды новой строки с прокруткой
                CP #0D
                JR Z, @Controls.ConsumeTextQueue.NewLine                        ; переход, если символ равен CR, прокрутить окно и продолжить чтение

                JP @Controls.PrintTextGlyph.Entry

                ; завершение активной строки, следующая запись будет выбрана при новом вызове
FinishString:   LD HL, #0000
                LD (@ControlsTextDisplayState.ActiveString), HL
                RET

                ; сброс колонки перед прокруткой и продолжением этого же вызова
NewLine:        XOR A
                LD (@ControlsTextDisplayState.TextColumn), A
                CALL @Controls.ScrollTextWindow.Entry
                JP @Controls.ConsumeTextQueue.Entry

                endmodule
                endmodule
