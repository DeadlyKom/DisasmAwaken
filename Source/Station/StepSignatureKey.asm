                module Station
                module StepSignatureKey
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [точная формула ключа и банковый договор](../../Docs/WorldSignature.md)
; -----------------------------------------
; Обновление двух слов рабочего ключа с байтовым смешиванием и XOR-свёрткой
; исходная запись 4, файловые смещения #49F3..#4A1C
; In:
;   SignatureState.WorkKey содержит доступный для записи FSignatureKey из двух слов
;   BC - сохраняемый контекст, повторный вход с изменением того же ключа отсутствует
; Out:
;   HL - прежнее SecondWord, DE новое смешанное SecondWord, BC сохранён
;   AF - A XOR четырёх байтов обновлённого ключа, F от последнего XOR L
;   FirstWord заменено прежним SecondWord, SecondWord обновлено по формуле WorldSignature.md
;   альтернативные и индексные регистры, I и IFF сохранены, SP восстановлен
; Corrupt:
;   HL, DE, AF
; Note:
;   обмен слов не использует EXX, альтернативные пары не являются рабочим состоянием
;   сложение FirstWord+#0101 оборачивается до прибавления SecondWord, лишний перенос этого первого шага теряется
;   в ADC A,L участвует перенос последнего ADD HL,DE, перенос последующего ADD HL,BC в XOR не используется
;   состояние #631C является повторным использованием существующей памяти загрузчика, новая память не выделяется
;   период и статистическое качество шага не доказаны
; -----------------------------------------
                ; сохранение BC, временная пара станет смешанной перестановкой байтов
Entry:          PUSH BC
                ; чтение двух исходных слов рабочего FSignatureKey
                LD HL, (@SignatureState.WorkKey + FSignatureKey.FirstWord)
                LD DE, (@SignatureState.WorkKey + FSignatureKey.SecondWord)
                ; перестановка байтов FirstWord во временный BC
                LD C, H
                LD B, L
                ; расчёт FirstWord+#0101 по модулю 65536
                INC HL
                INC H
                ; расчёт суммы с SecondWord, этот перенос участвует в следующем ADC
                ADD HL, DE
                ; расчёт нового младшего смешивающего байта из SecondWord.low и младшей суммы
                LD A, E
                ADC A, L
                ; обновление C смешивающим байтом при сохранении B=FirstWord.low
                LD C, A
                ; расчёт второй шестнадцатибитной суммы с переставленным старшим байтом
                ADD HL, BC
                ; расчёт нового SecondWord.low через XOR суммы, C и #75
                LD A, L
                XOR C
                XOR #75
                ; передача прежнего SecondWord.low в новое FirstWord.low
                LD L, E
                LD E, A
                ; расчёт нового SecondWord.high через XOR старшей суммы, FirstWord.low и #A7
                LD A, H
                XOR B
                XOR #A7
                ; передача прежнего SecondWord.high в новое FirstWord.high
                LD H, D
                LD D, A
                ; обновление двух физических слов рабочего ключа
                LD (@SignatureState.WorkKey + FSignatureKey.FirstWord), HL
                LD (@SignatureState.WorkKey + FSignatureKey.SecondWord), DE
                ; расчёт возвращаемой XOR-свёртки четырёх обновлённых байтов
                LD A, D
                XOR E
                XOR H
                XOR L
                POP BC
                RET

                endmodule
                endmodule
