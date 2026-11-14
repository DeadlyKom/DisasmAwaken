                module Action
                module UpdateVisualEffects
                ; Документация [алгоритм и проверка](../../Docs/ActionVisualEffectWalk.md)
                ; -----------------------------------------
                ; Обход эффектов, продвижение ресурсов и растеризация допущенных записей
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #0F75..#100D
                ; In:
                ;   Enabled и Frames задают разрешение и счётчик, список FVisualEffect завершается отрицательным State
                ;   доступны три слова смещения, матрица ACTION и ресурсы VOXAL, банк 0 выбран, IRQ не вмешиваются
                ; Out:
                ;   при выключенном обходе запись и растровый буфер сохраняются
                ;   иначе уменьшаются общий счётчик и времена жизни активных записей, обновляются координаты, курсоры и фазы
                ;   положительная глубина без переполнения допускает рисователя страницы 3, после него возвращается страница 0
                ;   после конечного маркера SP восстанавливается и выполняется внешний RET
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, список, растровый буфер, операнды и рабочий стек
                ; Note:
                ;   сквозная модель проверяет восемь позиций, переходы времени, курсоры, растр и переключения
                ;   побочные записи вне списка и буфера и точный полный набор регистров отдельно не сверялись
                ; -----------------------------------------
                ; Проверка разрешения кадрового обхода.
Entry:          LD A, #00
                AND A
                RET Z                                                           ; выход, если обход выключен

                ; Расчёт оставшегося числа кадров с байтовым оборачиванием.
                LD A, #00
                DEC A
                JR NZ, @Action.UpdateVisualEffects.StoreTime                    ; переход, если после уменьшения ещё остались кадры

                ; Снятие разрешения на следующий кадр, текущий обход продолжается.
                XOR A
                LD (@ActionVisualEffectListState.Enabled), A
StoreTime:      LD (@ActionVisualEffectListState.Frames), A
                LD IX, @ActionBankedCallbackState.ContextBase
                ; Восстановление шага между записями после вызова рисователя.
SetStride:      LD DE, FVisualEffect
NextEffect:     ADD IX, DE
                ; Проверка состояния текущей записи.
                LD A, (IX + @FVisualEffect.State)
                AND A
                RET M                                                           ; выход, если отрицательное состояние отмечает конец списка

                JR Z, @Action.UpdateVisualEffects.NextEffect                    ; переход, если запись свободна

                ; Уменьшение времени жизни и сдвиг координат с передачей прежних слов в преобразователь.
                DEC (IX + @FVisualEffect.State)
                LD L, (IX + @FVisualEffect.SavedBC)
                LD H, (IX + @FVisualEffect.SavedBC + 1)
                LD (@ActionPatchedVectorState.Input2), HL
                LD BC, (@ActionScaledVectorState.Component2)
                OR A
                SBC HL, BC
                LD (IX + @FVisualEffect.SavedBC), L
                LD (IX + @FVisualEffect.SavedBC + 1), H
                LD L, (IX + @FVisualEffect.SavedHL)
                LD H, (IX + @FVisualEffect.SavedHL + 1)
                LD (@ActionPatchedVectorState.Input0), HL
                LD BC, (@ActionScaledVectorState.Component0)
                OR A
                SBC HL, BC
                LD (IX + @FVisualEffect.SavedHL), L
                LD (IX + @FVisualEffect.SavedHL + 1), H
                LD L, (IX + @FVisualEffect.SavedDE)
                LD H, (IX + @FVisualEffect.SavedDE + 1)
                LD (@ActionPatchedVectorState.Input1), HL
                LD BC, (@ActionScaledVectorState.Component1)
                OR A
                SBC HL, BC
                LD (IX + @FVisualEffect.SavedDE), L
                LD (IX + @FVisualEffect.SavedDE + 1), H
                EXX
                LD E, (IX + @FVisualEffect.FramePointer)
                LD D, (IX + @FVisualEffect.FramePointer + 1)
                DEC (IX + @FVisualEffect.FrameCount)
                JR NZ, @Action.UpdateVisualEffects.AdvanceCursor                ; переход, если счётчик ресурса ещё ненулевой, прибавить шаг

                LD A, (IX + @FVisualEffect.FrameReload)
                LD (IX + @FVisualEffect.FrameCount), A
                LD L, (IX + @FVisualEffect.FirstFrame)
                LD H, (IX + @FVisualEffect.FirstFrame + 1)
                JP @Action.UpdateVisualEffects.StoreCursor

                ; Прибавление шага к текущему адресу ресурса по модулю слова.
AdvanceCursor:  LD L, (IX + @FVisualEffect.FrameStride)
                LD H, (IX + @FVisualEffect.FrameStride + 1)
                ADD HL, DE
StoreCursor:    LD (IX + @FVisualEffect.FramePointer), L
                LD (IX + @FVisualEffect.FramePointer + 1), H
                EXX
                ; Сохранение настоящего SP перед вычислителем.
                LD (@ActionVisualEffectListState.SavedSP), SP
                LD IY, @Action.ResumeVisualEffect.Entry
                JP @Action.ComputePatchedVector.Entry

                endmodule
                endmodule
