                module Map
                module LoadClippedArcInputs
                ; Документация [Map](../../Docs/FunctionDetails/Map.md)
                ; Подробный разбор [загрузка полей, точные крайние адреса и побочная запись LeftMask](../../Docs/ArcPreparation.md)
                ; Геометрия StartY [диспетчер границ](../../Docs/ArcDispatcher.md)
                ; -----------------------------------------
                ; Загрузка смещений и начального состояния отсечённого прохода
                ; исходная запись 7, файловые смещения #2299..#22AA
                ; In:
                ;   MapArcState.OffsetY, OffsetX, ReferenceX и StartY содержат текущие рабочие байты
                ;   IRQ не вмешиваются, обычный возврат доступен на CPU-стеке
                ; Out:
                ;   HL, DE сохранены, BC=OffsetX*256+OffsetY
                ;   AF - A=StartY, F соответствует NEG от (ReferenceX+OffsetX)&255
                ;   HL' и D' сохранены, E'=StartY, B' сохранён, C'=(-(ReferenceX+OffsetX))&255
                ;   AF', IX, IY, I, IM и IFF сохранены
                ;   входные поля не меняются, SP обычного возврата равен входному SP+2
                ; Corrupt:
                ;   BC, AF, E', C', R
                ; Note:
                ;   R меняется за 12 M1, младшие семь битов увеличены на 12 по модулю 128, бит 7 сохраняется
                ;   первое ADD оборачивает сумму до NEG, флаги NEG сохраняются при последующем чтении StartY
                ;   DrawClippedMapArc вычисляет StartY через SqrtSquareDiff, выбор оси и входной заём описаны в ArcDispatcher.md
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
