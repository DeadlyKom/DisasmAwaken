                module Map
                module SubtractClipPointX
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр](../../Docs/ClipTail.md)
; -----------------------------------------
; Знаковые флаги оборачиваемой разности X2-X1
; исходная запись 7, файловые смещения #1B2C..#1B36
; In:
;   MapClipWork.FirstPoint.X и SecondPoint.X содержат исходные 16-битные координаты
; Out:
;   HL=SecondPoint.X-FirstPoint.X modulo 65536, DE=FirstPoint.X
;   AF сохраняет A и получает точные флаги SBC HL,DE при исходном Carry=0
;   BC, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, F
; Note:
;   поля точек не меняются, S сам по себе не учитывает переполнение знаковой разности
; -----------------------------------------
                ; расчёт оборачиваемой разности второй и первой координат X для условий обработчика
Entry:          LD HL, (@MapClipWork.SecondPoint.X)
                LD DE, (@MapClipWork.FirstPoint.X)
                OR A
                SBC HL, DE
                RET

                endmodule
                endmodule
