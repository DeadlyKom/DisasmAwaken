                module Controls
                module ScrollTextWindow
                ; Документация [вывод текстового окна](../../Docs/ControlsTextDisplay.md)
                ; -----------------------------------------
                ; Перенос пяти рядов текста вверх через SP и очистка нижнего ряда
                ; исходная запись 23, банк 1, смещения #124A..#14E5
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают
                ;   выбран банк 1 с исходными CONTROL0 и CONTROL, код и экран доступны для записи
                ;   после InitializeTextWindow операнды прокрутки соответствуют окну x=160..255, y=144..189
                ;   на CPU-стеке лежит внешний возврат, вмешательство ISR в модель не включено
                ;   при прокрутке SP временно указывает на экран, обработчик прерываний не должен использовать этот SP
                ; Out:
                ;   HL=0000, DE=0100, BC содержит исходное слово по 55F8
                ;   A содержит исходный байт 55FB, F исходный байт 55FA, это пиксельные данные последнего POP AF, а не логический статус
                ;   HL' сохраняется, DE' содержит исходное слово по 55FE, BC' исходное слово по 55FC
                ;   AF', IX, IY, I, IM и IFF сохраняются, банковых переключений и портовых операций нет
                ;   пять рядов высотой шесть растровых строк перенесены вверх на восемь пикселей, ширина 12 байтов
                ;   нижний ряд очищен, последний байт его строк имеет значения 00, 01, 00, 01, 00, 01
                ;   внешний RET задаёт SP=входной SP+2, сама процедура DI не выполняет
                ;   R получает 528 M1 с сохранением бита 7, исполняются 527 инструкций, RAM получает 432 записи экрана и два байта SavedScrollSP
                ; Corrupt:
                ;   HL, DE, BC, AF, DE', BC', R, 432 байта экрана и SavedScrollSP
                ; Note:
                ;   при настроенных операндах все 216 PUSH дают ровно 432 записи растра банка 5, ещё два байта пишутся в SavedScrollSP банка 1
                ;   адреса собственных записей не зависят от пикселей и входного SP, при этих условиях DB01 и DB02 банка 1 не записываются, IRQ и иные изменения операндов не исключены
                ;   между шестистрочными рядами остаются две нетронутые растровые строки, атрибуты не изменяются
                ;   SavedScrollSP сохраняет входной SP и восстанавливает его перед RET, динамическая рамка не создаётся
                ; -----------------------------------------
                ; сохранение настоящего SP перед переносом экрана через временные POP и PUSH
Entry:          LD (@ControlsTextDisplayState.SavedScrollSP), SP
                ; перенос растровой строки 1 из 30, чтение шести слов перед их записью на восемь пикселей выше
FirstSource:    LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
FirstTarget:    LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 2 из 30, чтение шести слов перед их записью на восемь пикселей выше
SecondSource:   LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 3 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 4 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 5 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 6 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 7 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 8 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 9 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 10 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 11 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 12 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 13 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 14 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 15 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 16 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 17 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 18 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 19 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 20 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 21 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 22 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 23 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 24 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 25 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 26 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 27 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 28 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 29 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; перенос растровой строки 30 из 30, чтение шести слов перед их записью на восемь пикселей выше
                LD SP, #5134
                POP HL
                POP DE
                POP BC
                POP AF
                EXX
                POP BC
                POP DE
                LD SP, #5120
                PUSH DE
                PUSH BC
                EXX
                PUSH AF
                PUSH BC
                PUSH DE
                PUSH HL
                ; очистка нижнего ряда, исходный узор 00 и 01 последнего байта сохраняется
                LD DE, #0100
                LD HL, #0000
                LD SP, #5100
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #5200
                PUSH DE
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #5300
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #5400
                PUSH DE
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #5500
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #5600
                PUSH DE
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                PUSH HL
                LD SP, #0000
                RET

                endmodule
                endmodule
