                module ActionSpawnTemplates
                ; Документация [физические таблицы создания](../../../Docs/ActionSpawnPhysicalRows.md)
                assert $ == #7799
                ; Блок станции ST9k, Template00, адрес #7809.
Seed00:         FSpawnDataPointer {
                    #7809                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST14k, Template01, адрес #783B.
Seed01:         FSpawnDataPointer {
                    #783B                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST13k, Template02, адрес #7831.
Seed02:         FSpawnDataPointer {
                    #7831                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST4k, Template03, адрес #77D7.
Seed03:         FSpawnDataPointer {
                    #77D7                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST2k, Template04, адрес #77C3.
Seed04:         FSpawnDataPointer {
                    #77C3                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST1k, Template05, адрес #77B9.
Seed05:         FSpawnDataPointer {
                    #77B9                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST6k, Template06, адрес #77EB.
Seed06:         FSpawnDataPointer {
                    #77EB                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST5k, Template07, адрес #77E1.
Seed07:         FSpawnDataPointer {
                    #77E1                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST11k, Template08, адрес #781D.
Seed08:         FSpawnDataPointer {
                    #781D                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST7k, Template09, адрес #77F5.
Seed09:         FSpawnDataPointer {
                    #77F5                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST8k, Template10, адрес #77FF.
Seed10:         FSpawnDataPointer {
                    #77FF                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST16k, Template11, адрес #784F.
Seed11:         FSpawnDataPointer {
                    #784F                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST12k, Template12, адрес #7827.
Seed12:         FSpawnDataPointer {
                    #7827                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST3k, Template13, адрес #77CD.
Seed13:         FSpawnDataPointer {
                    #77CD                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST15k, Template14, адрес #7845.
Seed14:         FSpawnDataPointer {
                    #7845                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Блок станции ST10k, Template15, адрес #7813.
Seed15:         FSpawnDataPointer {
                    #7813                                                       ; FSpawnDataPointer.Address, исходное значение
                }
                ; Авторский блок станции ST1k, три поправки и параметры записи.
Template05:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #C4,                                                        ; смещение 9E00, модель St1, авторский IST1
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End05:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST2k, три поправки и параметры записи.
Template04:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #C8,                                                        ; смещение 9E00, модель St2, авторский IST2
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End04:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST3k, три поправки и параметры записи.
Template13:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #CC,                                                        ; смещение 9E00, модель St3, авторский IST3
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End13:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST4k, три поправки и параметры записи.
Template03:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #D0,                                                        ; смещение 9E00, модель St4, авторский IST4
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End03:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST5k, три поправки и параметры записи.
Template07:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #D4,                                                        ; смещение 9E00, модель St5, авторский IST5
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End07:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST6k, три поправки и параметры записи.
Template06:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #D8,                                                        ; смещение 9E00, модель St6, авторский IST6
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End06:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST7k, три поправки и параметры записи.
Template09:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #DC,                                                        ; смещение 9E00, модель St7, авторский IST7
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End09:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST8k, три поправки и параметры записи.
Template10:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #E0,                                                        ; смещение 9E00, модель St8, авторский IST8
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End10:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST9k, три поправки и параметры записи.
Template00:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #E4,                                                        ; смещение 9E00, модель St9, авторский IST9
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End00:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST10k, три поправки и параметры записи.
Template15:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #E8,                                                        ; смещение 9E00, модель St10, авторский IST10
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End15:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST11k, три поправки и параметры записи.
Template08:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #EC,                                                        ; смещение 9E00, модель St11, авторский IST11
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End08:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST12k, три поправки и параметры записи.
Template12:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #F0,                                                        ; смещение 9E00, модель St12, авторский IST12
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End12:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST13k, три поправки и параметры записи.
Template02:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #F4,                                                        ; смещение 9E00, модель St13, авторский IST13
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End02:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST14k, три поправки и параметры записи.
Template01:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #F8,                                                        ; смещение 9E00, модель St14, авторский IST14
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End01:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST15k, три поправки и параметры записи.
Template14:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #FC,                                                        ; смещение 9E00, модель St15, авторский IST15
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End14:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                ; Авторский блок станции ST16k, три поправки и параметры записи.
Template11:     FSpawnTemplateRow {
                    #0000,                                                      ; FSpawnTemplateRow.Delta0, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta1, исходное значение
                    #0000,                                                      ; FSpawnTemplateRow.Delta2, исходное значение
                    #00,                                                        ; смещение 9E00, модель KN01pol1, авторский IST16
                    #00                                                         ; FSpawnTemplateRow.OffsetPhase1, исходное значение
                }
                ; Авторское DW #80FF, EndCode=80 завершает обход, роль младшего FF не установлена.
End11:          FSpawnTemplateEnd {
                    #FF,                                                        ; младший FF авторского слова 80FF, отдельная роль не установлена
                    #80                                                         ; код 80 завершает обход, это числовой код
                }
                assert $ == #7859
                endmodule
