                module Map
                module SubtractClipPointY
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр](../../Docs/ClipTail.md)
; -----------------------------------------
; Знаковые флаги оборачиваемой разности Y2-Y1
; исходная запись 7, файловые смещения #1B37..#1B41
; In:
;   MapClipWork.FirstPoint.Y и SecondPoint.Y содержат исходные 16-битные координаты
; Out:
;   HL=SecondPoint.Y-FirstPoint.Y modulo 65536, DE=FirstPoint.Y
;   AF сохраняет A и получает точные флаги SBC HL,DE при исходном Carry=0
;   BC, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, F
; Note:
;   поля точек не меняются, S сам по себе не учитывает переполнение знаковой разности
; -----------------------------------------
                ; расчёт оборачиваемой разности второй и первой координат Y для условий обработчика
Entry:          LD HL, (@MapClipWork.SecondPoint.Y)
                LD DE, (@MapClipWork.FirstPoint.Y)
                OR A
                SBC HL, DE
                RET

                endmodule
                endmodule
