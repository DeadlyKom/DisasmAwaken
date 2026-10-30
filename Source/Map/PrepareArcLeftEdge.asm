                module Map
                module PrepareArcLeftEdge
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [загрузка полей, точные крайние адреса и побочная запись LeftMask](../../Docs/ArcPreparation.md)
; -----------------------------------------
; Подготовка левого края дуги и изменяемой правой колонки
; исходная запись 7, файловые смещения #2248..#225F
; In:
;   LeftColumn и RightColumn обозначают изменяемые операнды OR, исходно 1 и 30
;   после D0C3 LeftColumn=ColumnByte[0], RightColumn=ColumnByte[MaxX]
;   MapArcState содержит рабочие байты, MapScreenTables построены для текущего окна
;   основные входные регистры не передают аргументов, действуют требования табличного помощника края
; Out:
;   X=(ReferenceX+OffsetX-Radius)&255, Y=RowY
;   адрес края вычисляется по RowHigh[Y], RowLow[Y]+ColumnByte[X] с оборачиванием младшей суммы
;   HL - H от адреса левого края, L=(младший адрес левого края&E0)|RightColumn
;   DE - D=Radius, E младший адрес левого края, BC - B=80 SHR(X&7), C=1
;   AF - A=L, F соответствует OR RightColumn, Carry=0
;   HL', D', B', AF', IX, IY, I и IFF сохранены, C'=(-Radius)&255, E'=0
;   MapState.LeftMask не меняется
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
                ; выбор исходной строки RowY для левого табличного края
                LD A, (@MapArcState.RowY)
                LD C, A
                ; расчёт байтового X левого края как ReferenceX+OffsetX-Radius
                LD A, (@MapArcState.ReferenceX)
                ADD A, B
                SUB D
                ; поиск адреса и одноразрядной маски левого края без изменения пикселей
                CALL @Map.PrepareLeftRasterPoint.Entry
                ; расчёт изменяемой правой колонки для другого края того же символьного ряда
                LD A, E
                AND #E0
                OR #1E
                LD L, A
                LD C, #01
                RET

                endmodule
                endmodule
