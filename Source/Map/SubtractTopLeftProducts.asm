                module Map
                module SubtractTopLeftProducts
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр](../../Docs/ClipTail.md)
; -----------------------------------------
; Старшее слово и флаги 32-битной разности верхнего и левого произведений
; исходная запись 7, файловые смещения #1ADC..#1AEF
; In:
;   MapClipWork.TopProduct и LeftProduct содержат два 32-битных произведения с младшим словом вперёд
; Out:
;   HL=high(TopProduct)-high(LeftProduct)-заём из low(TopProduct)-low(LeftProduct), modulo 65536
;   BC=high(LeftProduct), AF сохраняет A и получает флаги последнего SBC HL,BC с этим заёмом
;   S отражает бит 31 оборачиваемой разности, Carry полный 32-битный беззнаковый заём
;   Z проверяет только старшее слово разности после заёма, младшее слово в результат Z не входит
;   DE, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, BC, F
; Note:
;   произведения не меняются, входной Carry очищается OR A перед младшим словом
;   S без учёта P/V не заменяет математическое знаковое сравнение при переполнении
; -----------------------------------------
                ; подготовка младших слов для получения заёма в старшее слово разности
Entry:          LD HL, (@MapClipWork.TopProduct.LowWord)
                LD BC, (@MapClipWork.LeftProduct.LowWord)
                OR A
                SBC HL, BC
                ; подготовка старших слов с сохранением заёма от младшего SBC
                LD HL, (@MapClipWork.TopProduct.HighWord)
                LD BC, (@MapClipWork.LeftProduct.HighWord)
                SBC HL, BC
                RET

                endmodule
                endmodule
