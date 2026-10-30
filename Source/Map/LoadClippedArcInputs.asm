                module Map
                module LoadClippedArcInputs
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [загрузка полей, точные крайние адреса и побочная запись LeftMask](../../Docs/ArcPreparation.md)
; -----------------------------------------
; Загрузка смещений и ненулевого начального состояния альтернативной пары C', E'
; исходная запись 7, файловые смещения #2299..#22AA
; In:
;   MapArcState.OffsetY, OffsetX, ReferenceX и StartY содержат текущие рабочие байты
; Out:
;   HL, DE сохранены, BC=OffsetX*256+OffsetY
;   AF - A=StartY, F соответствует NEG от (ReferenceX+OffsetX)&255
;   C'=(-(ReferenceX+OffsetX))&255, E'=StartY
;   HL', D', B', AF', IX, IY, I и IFF сохранены
;   входные поля не меняются, SP обычного возврата равен входному SP+2
; Corrupt:
;   BC, AF, C', E'
; Note:
;   первое ADD оборачивает сумму до NEG, флаги NEG сохраняются при последующем чтении StartY
;   StartY далее участвует в рекурсии растрового ядра, его геометрическое вычисление вызывающим кодом ещё разбирается
; -----------------------------------------
                ; загрузка двух рабочих смещений без изменения основных HL и DE
Entry:          LD BC, (@MapArcState.OffsetY)
                ; расчёт отрицательной суммы ReferenceX+OffsetX для начального альтернативного C
                LD A, (@MapArcState.ReferenceX)
                ADD A, B
                NEG
                ; обновление C' с сохранением остальных альтернативных байтов
                EXX
                LD C, A
                ; загрузка StartY в альтернативный E, флаги предшествующего NEG сохраняются
                LD A, (@MapArcState.StartY)
                LD E, A
                EXX
                RET

                endmodule
                endmodule
