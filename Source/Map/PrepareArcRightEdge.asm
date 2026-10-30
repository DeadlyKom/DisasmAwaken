                module Map
                module PrepareArcRightEdge
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [загрузка полей, точные крайние адреса и побочная запись LeftMask](../../Docs/ArcPreparation.md)
; -----------------------------------------
; Подготовка правого края дуги и изменяемой левой колонки
; исходная запись 7, файловые смещения #2260..#2277
; In:
;   LeftColumn и RightColumn обозначают изменяемые операнды OR, исходно 1 и 30
;   после D0C3 LeftColumn=ColumnByte[0], RightColumn=ColumnByte[MaxX]
;   MapArcState содержит рабочие байты, MapScreenTables построены для текущего окна
;   основные входные регистры не передают аргументов, действуют требования табличного помощника края
; Out:
;   X=(ReferenceX+Radius-OffsetX)&255, Y=RowY
;   адрес края вычисляется по RowHigh[Y], RowLow[Y]+ColumnByte[X] с оборачиванием младшей суммы
;   HL - полный адрес правого края
;   DE - D=Radius, E=(L&E0)|LeftColumn, BC - B=80, C=80 SHR(X&7)
;   AF - A=E, F соответствует OR LeftColumn, Carry=0
;   HL', D', B', AF', IX, IY, I и IFF сохранены, C'=(-Radius)&255, E'=0
;   MapState.LeftMask получает исходный OffsetX через PrepareRightRasterPoint, даже после замены B на 80
;   пиксели и рабочие входные поля не меняются, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, C', E'
; Note:
;   все суммы и разности X байтовые, переполнение намеренно не проверяется
;   колонки задаются через OR младшего адреса, [фазы исполнения](../../Docs/MapRuntimeProfiles.md) проверены отдельно
;   растровый проход и шесть направляющих входов описаны отдельно, диспетчер DFC3 ещё разбирается
; -----------------------------------------
                ; загрузка общих смещений и альтернативной начальной пары через LoadArcRasterInputs
Entry:          CALL @Map.LoadArcRasterInputs.Entry
                ; выбор исходной строки RowY для правого табличного края
                LD A, (@MapArcState.RowY)
                LD C, A
                ; расчёт байтового X правого края как ReferenceX+Radius-OffsetX
                LD A, (@MapArcState.ReferenceX)
                ADD A, D
                SUB B
                ; поиск адреса и маски правого края, помощник дополнительно сохраняет OffsetX в LeftMask
                CALL @Map.PrepareRightRasterPoint.Entry
                ; расчёт изменяемой левой колонки для другого края того же символьного ряда
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD B, #80
                RET

                endmodule
                endmodule
