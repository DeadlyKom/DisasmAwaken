                module Action
                module StartSmallRecordEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionSmallEffectState.md)
                ; -----------------------------------------
                ; Создание малого эффекта по заголовку модели и переход текущей записи к состоянию затухания 7
                ; исходная запись 17, адреса F6EC..F728
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, F альтернативного AF учитывается результатом банкового выделения
                ;   IX указывает Components и ModelOffset текущей FActionRecord, StateCode и Unknown11 доступны для записи
                ;   действуют договоры ReadObjectHeaderWord, DispatchBank3Callback, Voxel.CreateSmallEffect и RestoreRuntimePage
                ;   OBJECT3D загружен в банк 4, VOXAL0 и VOXAL в банк 3, список эффектов от A795 имеет отрицательный маркер State
                ;   изначально выбран ACTION банка 0, 7FFD разблокирован, шесть дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   HL=D800, DE=00C0 и BC=0012 после полного возврата малого эффекта
                ;   A=max(исходные Frames,26), F соответствует CP исходных Frames с 26 и не пересчитывается после возможной загрузки 26
                ;   HL', DE' и BC' содержат Components0, 1 и 2 текущей записи, исходные альтернативные пары не сохраняются
                ;   при выделении AF'=0054, при достижении отрицательного маркера A'=1A и F' равен входному альтернативному F
                ;   IY указывает выбранную запись эффекта либо отрицательный маркер, IX и I/IM/IFF сохраняются, SP после RET увеличен на два
                ;   старший байт заголовка модели задаёт Mode малого эффекта, его State=1A передаётся отдельно через альтернативный A
                ;   при свободном слоте создана полная FVisualEffect с сохранёнными Components и ресурсом D800, при полном списке запись не создаётся
                ;   в обоих случаях Enabled=1, Frames=max(прежние Frames,26), родитель получает StateCode=07 и Unknown11=12
                ;   OUT 7FFD последовательно получает 14, 10, 13 и 10, итоговая полная конфигурация равна 10
                ;   R получает 142+7*n M1 при выделении после n занятых записей либо 100+7*n при отрицательном маркере, ещё 2 M1 при прежних Frames<26
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, StateCode и Unknown11 родителя, условно запись эффекта, четыре операнда банка 3, Enabled, условно Frames, шесть временных байтов CPU-стека, 7FFD, SP внешним RET
                ; Note:
                ;   это исходная цель State06, при неудаче выделения переход к затуханию и включение обхода не отменяются
                ;   Unknown11=12 означает 18 последующих вызовов State07 до освобождения при обычном проходе без иных писателей, это не универсальная длительность всех объектов
                ;   32256 сценариев исполнили реальные чтение OBJECT3D, банковый создатель, выделение и оба возвратных хвоста до полного RET
                ;   проверены исходные чётные ModelOffset, все Frames, все принудительные Mode и альтернативные F, тестовые подмены заголовка отмечены отдельно
                ;   точные регистры, флаги, R, восемь банков, кратность записей и четыре настоящих OUT проверены, полное произведение входов не исчерпано
                ;   неизвестный хвост банка 4 в модели заполнен A4, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Чтение полного слова заголовка модели из OBJECT3D, для режима малого эффекта используется его старший байт.
Entry:          LD A, (IX + @FActionRecord.ModelOffset)
                CALL @Action.ReadObjectHeaderWord.Entry
                ; Сохранение режима в альтернативном A для последующего обмена внутри банкового диспетчера.
                LD A, H
                EX AF, AF'
                ; Подготовка трёх Components родителя, EXX передаёт их в сохраняемый набор для заполнения FVisualEffect.
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD E, (IX + @FActionRecord.Components.Component1.Low)
                LD D, (IX + @FActionRecord.Components.Component1.High)
                LD C, (IX + @FActionRecord.Components.Component2.Low)
                LD B, (IX + @FActionRecord.Components.Component2.High)
                ; Подготовка отдельного State=26 для эффекта, это не режим и не новое состояние родителя.
                LD A, @ActionSmallEffectConst.EffectState
                EXX
                ; Выбор настоящего CreateSmallEffect банка 3 и вызов через возвратный диспетчер общей RAM.
                LD HL, @Voxel.CreateSmallEffect.Entry
                CALL @Action.DispatchBank3Callback.Entry
                ; Обновление допуска кадрового обхода независимо от наличия свободной записи эффекта.
                LD A, #01
                LD (@ActionVisualEffectListState.Enabled), A
                ; Проверка минимальной оставшейся длительности обхода перед возможным увеличением.
                LD A, (@ActionVisualEffectListState.Frames)
                CP @ActionSmallEffectConst.MinimumFrames
                JR NC, @Action.StartSmallRecordEffect.SetDecay                  ; переход, если прежние Frames не меньше 26, сохранить их и установить затухание родителя

                ; Обновление Frames до 26, флаги предыдущего CP сохраняются.
                LD A, @ActionSmallEffectConst.EffectState
                LD (@ActionVisualEffectListState.Frames), A
                ; Обновление состояния родителя до State07 и исходного счётчика затухания 18.
SetDecay:       LD (IX + @FActionRecord.StateCode), @ActionSmallEffectConst.DecayState
                LD (IX + @FActionRecord.Unknown11), @ActionSmallEffectConst.DecayCount
                RET

                endmodule
                endmodule
