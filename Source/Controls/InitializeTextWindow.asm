                module Controls
                module InitializeTextWindow
                ; Документация [вывод текстового окна](../../Docs/ControlsTextDisplay.md)
                ; -----------------------------------------
                ; Сброс курсоров очереди и настройка тридцати строк стековой прокрутки
                ; исходная запись 23, банк 1, смещения #1130..#1177
                ; In:
                ;   HL, DE, BC, AF, IX входных аргументов не задают
                ;   банк 1 выбран, исходные операнды копирования доступны для записи
                ; Out:
                ;   ActiveString=0, ReadCursor=Slot00-2, WriteCursor=Slot00, содержимое очереди не очищается
                ;   в 30 парах операндов установлены источники 152..189 и назначения 144..181 с шагом ряда 8 и высотой 6
                ;   HL', DE', BC' и IY сохраняются, I, IM и IFF сохраняются, SP=входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, три курсора и 120 байтов операндов прокрутки, R
                ; Note:
                ;   TextColumn не сбрасывается, очередь повторно не заполняется значением Free
                ;   исполнение исходного ScrollTextWindow до этой настройки копирует один и тот же ряд 30 раз
                ; -----------------------------------------
                ; сброс активной строки без очистки физических записей очереди
Entry:          LD HL, #0000
                LD (@ControlsTextDisplayState.ActiveString), HL
                ; установка курсора перед первым элементом, потребитель сначала прибавляет два
                LD HL, #EC7E
                LD (@ControlsTextDisplayState.ReadCursor), HL
                INC HL
                INC HL
                LD (@ControlsTextQueueState.WriteCursor), HL
                ; подготовка обхода операндов 30 развёрнутых копирований по 20 байтов кода
                LD IX, @ControlsScrollPatchConst.CursorSeed
                LD BC, @ControlsScrollPatchConst.Stride
                LD HL, #5074
                LD DE, #5060
                LD A, #1E
                ; обновление пары адресов источника и вершины стека назначения текущей растровой строки
PatchRow:       ADD IX, BC
                LD (IX + @ControlsScrollPatchConst.SourceLow), L
                LD (IX + @ControlsScrollPatchConst.SourceHigh), H
                LD (IX + @ControlsScrollPatchConst.TargetLow), E
                LD (IX + @ControlsScrollPatchConst.TargetHigh), D
                EX AF, AF'
                ; вычисление следующей растровой строки в пределах шестипиксельного ряда
                INC H
                INC D
                LD A, H
                AND #07
                CP #06
                JR NZ, @Controls.InitializeTextWindow.NextScan                  ; переход, если шестая строка ещё не пройдена, сохранить текущую символьную строку

                ; вычисление следующего текстового ряда с шагом 32 байта и двумя пустыми растровыми строками
                LD A, L
                ADD A, #20
                LD L, A
                LD A, E
                ADD A, #20
                LD E, A
                LD H, #50
                LD D, H
NextScan:       EX AF, AF'
                DEC A
                JR NZ, @Controls.InitializeTextWindow.PatchRow                  ; переход, если остались ненастроенные растровые строки

                RET

                endmodule
                endmodule
