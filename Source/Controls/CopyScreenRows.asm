                module Controls
                module CopyScreenRows
                ; Документация [алгоритм и проверка](../../Docs/ControlsBufferCopy.md)
                ; -----------------------------------------
                ; Стековый перенос страниц линейного растра в символьные строки экрана
                ; исходная запись 22, банк 1, смещения #0882..#0A8C
                ; In:
                ;   HL задаёт источник X, выровненный на 256 байтов, DE и BC входных аргументов не задают, AF задаёт A=n страниц
                ;   HL' задаёт адрес D последнего байта первой половины начальной экранной строки, DE', BC', AF', IX и IY аргументов не задают
                ;   n=1..8, начало приходится на символьную строку, все n строк помещаются в одну треть экрана
                ;   все 256*n байтов источника доступны, H источника не переполняется за доступную RAM
                ;   банк 1 выбран, CONTROL0 и его изменяемые операнды доступны для записи
                ;   источник, экран и CPU-стек не перекрываются, источник не перекрывает код копировщика
                ;   на CPU-стеке находится внешний возврат, обработчик IRQ не должен использовать временный экранный SP
                ; Out:
                ;   скопированы 256*n байтов, каждый экранный адрес записан ровно один раз
                ;   HL=X+256*n, DE и BC содержат слова по адресам P+4 и P+2, где P=X+256*n-16
                ;   A=00, F=42 OR (байт P AND 01), эти флаги получены DEC 1 в 0 с пиксельным Carry
                ;   HL'=D+32*n, DE'=F910, BC' содержит слово P+10, A' содержит байт P+9
                ;   F' получен последним ADD HL,F910, S,Z,PV сохранены из байта P+8, N=0, H,C и биты 5,3 отражают сложение
                ;   IX содержит слово P+6, IY слово P+14, I, IM и IFF сохраняются
                ;   SavedStack содержит входной SP, RemainingPages=01, RET даёт SP=входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, 256*n экранных байтов, SavedStack, RemainingPages, R
                ; Note:
                ;   дополнительных PUSH на CPU-стеке нет, PUSH и POP работают по временным экранным и исходным адресам
                ;   нулевой A не означает пустую операцию, уменьшение происходит после первого копирования, такой вход не входит в договор
                ;   переход через границу трети экрана и перекрытие источника с назначением не входят в договор
                ;   RemainingPages является операндом LD A,nn, SavedStack операндом LD SP,nn
                ; -----------------------------------------
                ; сохранение настоящего SP до назначения временных стеков источника и экрана
Entry:          LD (@ControlsBufferCopyState.SavedStack), SP
                ; сохранение числа оставшихся страниц до загрузки пикселей в AF и альтернативный AF
CopyPage:       LD (@ControlsBufferCopyState.RemainingPages), A
                ; чтение 16 пиксельных байтов левой половины растровой строки 1 в основные и альтернативные регистры
                LD SP, HL
                LD L, #10
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 1 в основные и альтернативные регистры
                LD SP, HL
                LD L, #20
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 2 в основные и альтернативные регистры
                LD SP, HL
                LD L, #30
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 2 в основные и альтернативные регистры
                LD SP, HL
                LD L, #40
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 3 в основные и альтернативные регистры
                LD SP, HL
                LD L, #50
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 3 в основные и альтернативные регистры
                LD SP, HL
                LD L, #60
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 4 в основные и альтернативные регистры
                LD SP, HL
                LD L, #70
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 4 в основные и альтернативные регистры
                LD SP, HL
                LD L, #80
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 5 в основные и альтернативные регистры
                LD SP, HL
                LD L, #90
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 5 в основные и альтернативные регистры
                LD SP, HL
                LD L, #A0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 6 в основные и альтернативные регистры
                LD SP, HL
                LD L, #B0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 6 в основные и альтернативные регистры
                LD SP, HL
                LD L, #C0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 7 в основные и альтернативные регистры
                LD SP, HL
                LD L, #D0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 7 в основные и альтернативные регистры
                LD SP, HL
                LD L, #E0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                RES 4, L
                INC H
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов левой половины растровой строки 8 в основные и альтернативные регистры
                LD SP, HL
                LD L, #F0
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись левой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                SET 4, L
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; чтение 16 пиксельных байтов правой половины растровой строки 8 в основные и альтернативные регистры
                LD SP, HL
                LD L, #00
                POP AF
                POP BC
                POP DE
                POP IX
                EX AF, AF'
                EXX
                POP AF
                POP BC
                POP DE
                POP IY
                ; запись правой половины строки обратным порядком PUSH с сохранением исходного порядка байтов
                LD SP, HL
                INC SP
                PUSH IY
                PUSH DE
                PUSH BC
                PUSH AF
                ; вычисление следующей символьной строки после восьми растровых строк Spectrum
                LD DE, #F910
                ADD HL, DE
                EX AF, AF'
                EXX
                PUSH IX
                PUSH DE
                PUSH BC
                PUSH AF
                ; вычисление следующей 256-байтовой страницы источника, младший байт уже равен нулю
                INC H
                ; восстановление счётчика страниц, пиксельные флаги пока остаются в F
                LD A, #00
                DEC A
                JP NZ, @Controls.CopyScreenRows.CopyPage                        ; переход, если после копирования остались страницы, сохранить новый счётчик и повторить

                ; восстановление настоящего CPU-стека перед внешним возвратом
                LD SP, #0000
                RET

                endmodule
                endmodule
