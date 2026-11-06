                module Intro
                module RunAttributeWriter
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Документация [алгоритм и проверка](../../Docs/IntroPresentAttributes.md)
; -----------------------------------------
; Выполнение 32 генерируемых пар POP HL и LD (nn),HL с восстановлением SP
; исходная запись 3, файловые смещения #05A4..#062C
                ; In:
                ;   HL - адрес 32 последовательных little-endian слов, DE, BC и AF сохраняемый контекст
                ;   128 байтов 68A9..6928 уже заменены на 32 пары POP HL и LD (nn),HL
                ;   SP указывает внешний возврат, SavedSP доступен для записи, назначения не повреждают код, источники и CPU-стек
                ;   IRQ не вмешивается во временный SP, это обеспечивается DI либо проверенным вызовом сразу после кадрового IRQ
                ; Out:
                ;   HL - последнее прочитанное слово, DE, BC и AF сохранены
                ;   HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются собственным кодом
                ;   64 байта источника перенесены по адресам созданного кода, SavedSP содержит входной SP
                ;   SP восстановлен перед RET, после RET равен входному SP+2, CPU-стек не записывается
                ; Corrupt:
                ;   HL, R, SavedSP и 64 байта назначений
                ; Note:
                ;   NOP в исходном файле является исходным содержимым будущего исполняемого писателя, эти NOP не являются рабочим вариантом переноса
                ;   LD SP,HL превращает источник в поток POP, последний LD SP,nn восстанавливает исходный CPU-стек
                ;   все POP HL и LD (nn),HL сохраняют AF, специальный запрет IRQ сам код не выполняет
                ;   PresentAttributes проверен с IFF=1 после реального IM 1, поэтому обязательный DI не является точным описанием всех штатных вызовов
                ;   условие отсутствия IRQ во временный SP остаётся обязательным, произвольный несинхронизированный вызов с IFF=1 не доказан
                ; -----------------------------------------
                ; Сохранение исходного CPU SP перед чтением 32 слов через POP.
Entry:          LD (@IntroAttrState.SavedSP), SP
                LD SP, HL
                ; 128 байтов места для 32 генерируемых пар POP HL и LD (nn),HL
                ; Исходные 128 NOP заменяются BuildAttributeWriter на 32 пары POP HL и LD (nn),HL.
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                NOP
                ; Восстановление исходного CPU SP из SavedSP перед внешним RET.
                LD SP, #3131
                RET


                endmodule
                endmodule
