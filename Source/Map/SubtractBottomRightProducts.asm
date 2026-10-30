                module Map
                module SubtractBottomRightProducts
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр](../../Docs/ClipTail.md)
; -----------------------------------------
; Старшее слово и флаги 32-битной разности нижнего и правого произведений
; исходная запись 7, файловые смещения #1B18..#1B2B
; In:
;   MapClipWork.BottomProduct и RightProduct содержат два 32-битных произведения с младшим словом вперёд
; Out:
;   HL=high(BottomProduct)-high(RightProduct)-заём из low(BottomProduct)-low(RightProduct), modulo 65536
;   BC=high(RightProduct), AF сохраняет A и получает флаги последнего SBC HL,BC с этим заёмом
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
Entry:          LD HL, (@MapClipWork.BottomProduct.LowWord)
                LD BC, (@MapClipWork.RightProduct.LowWord)
                OR A
                SBC HL, BC
                ; подготовка старших слов с сохранением заёма от младшего SBC
                LD HL, (@MapClipWork.BottomProduct.HighWord)
                LD BC, (@MapClipWork.RightProduct.HighWord)
                SBC HL, BC
                RET

                endmodule
                endmodule
