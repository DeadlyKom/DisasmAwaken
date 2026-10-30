                module Voxel
                module AllocateEffect
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; Подробный разбор [Effects.md](../../Docs/Effects.md)
; -----------------------------------------
; Поиск свободной записи #12 байт по знаку и нулевому признаку в поле +7
; исходная запись 21, файловые смещения #0033..#007E
; In:
;   HL - указатель ресурса, DE - параметр записи, HL', DE', BC' - три сохраняемых слова
;   AF' - A признак состояния, IY - запись перед началом поиска, операнды #EC5A, #EC6C, #EC79 и #EC7D настроены
; Out:
;   IY - свободная запись либо завершающая запись с установленным знаком поля +7
; Corrupt:
;   BC, AF, AF', IY
; Note:
;   шаг поиска #12 байт прибавляется до первой проверки, ноль поля +7 означает свободную запись
;   отрицательный признак завершает поиск без изменения записи, отдельного ограничения числа записей нет
;   при успехе записываются все 18 байтов, обмен AF и AF' обратно не выполняется
;   HL, DE и альтернативные HL, DE, BC сохраняются, главный BC получает #12
; -----------------------------------------
                ; поиск свободной записи с шагом исходной структуры FVisualEffect
Entry:          LD BC, FVisualEffect
                ; переход к следующей записи до проверки её состояния, исходная запись пропускается
FindFree:       ADD IY, BC
                LD A, (IY + FVisualEffect.State)
                AND A
                RET M                                                           ; выход, если поле State отрицательно и достигнут ограничитель списка


                JR NZ, @Voxel.AllocateEffect.FindFree                           ; переход, если запись занята и нужно проверить следующую


                ; сохранение альтернативных HL, DE и BC в SavedHL, SavedDE и SavedBC
                EXX
                LD (IY + FVisualEffect.SavedHL), L
                LD (IY + FVisualEffect.SavedHL + 1), H
                LD (IY + FVisualEffect.SavedDE), E
                LD (IY + FVisualEffect.SavedDE + 1), D
                LD (IY + FVisualEffect.SavedBC), C
                LD (IY + FVisualEffect.SavedBC + 1), B
                ; получение признака состояния из альтернативного A, обратный обмен AF не выполняется
                EX AF, AF'
                LD (IY + FVisualEffect.State), A
                EXX
                ; инициализация режима, ресурса, его текущего указателя и параметров выбранного варианта
                LD (IY + FVisualEffect.Mode), #00
                LD (IY + FVisualEffect.Source), L
                LD (IY + FVisualEffect.Source + 1), H
                LD (IY + FVisualEffect.Cursor), L
                LD (IY + FVisualEffect.Cursor + 1), H
                LD (IY + FVisualEffect.Unknown0C), #01
                LD A, #00
                LD (IY + FVisualEffect.Unknown0D), A
                LD (IY + FVisualEffect.Unknown0E), E
                LD (IY + FVisualEffect.Unknown0E + 1), D
                LD (IY + FVisualEffect.Unknown10), #00
                LD (IY + FVisualEffect.Unknown11), #00
                RET


                endmodule
                endmodule
