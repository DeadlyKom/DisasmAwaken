                module Action
                module RenderSceneFrame
                ; Документация [алгоритм и проверка](../../Docs/ActionRenderFrameSetup.md)
                ; -----------------------------------------
                ; Подготовка кадра, проекция объектов и передача в очередь отрисовки
                ; исходная запись 17, код ACTION банка 0, смещения #8020..#81B8
                ; In:
                ;   CompanionMask, Position, тройка углов и FirstMode задают подготовку кадра
                ;   доступны широкий список, объектные записи с конечным маркером, таблицы ACTION и ресурс OBJECT3D
                ;   банк 0 выбран, страницы 1, 3 и 4 загружены, SP в общей RAM, IRQ не вмешиваются
                ; Out:
                ;   базис и девять коэффициентов обновляются, выполняются проекция тела по режиму и обход широких векторов
                ;   объекты перебираются с шагом #40, выходные слова сохраняются в допущенных записях
                ;   при конечном маркере ReadRenderQueue восстанавливает настоящий SP и читает очередь
                ;   при допуске очередной записи управление продолжается в PrepareProjectionScale после чтения заголовка
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP на участке чтения и записи, R
                ;   состояние базиса, матрицы, проекции, записей, очереди, временные слова и регистр 7FFD
                ; Note:
                ;   точные условия отдельных путей приведены в документации, байты очереди проверяются независимо от графического вывода
                ;   модель покрывает полный возврат с пустой и непустой очередью на исходных ресурсах
                ;   точные все регистры и записи всего кадра, игровые IRQ и нативный вывод не заявляются
                ; -----------------------------------------
                ; Проверка допуска приближения точки к центру.
Entry:          LD A, #00
                AND A
                JR NZ, @Action.RenderSceneFrame.ResetFrame                      ; переход, если CompanionMask ненулевая, сохранить положение

                ; Расчёт шага X к #77 по знаку байтовой разности.
                LD HL, (@ActionAimFollowState.Position)
                LD A, L
                SUB #77
                NEG
                JR Z, @Action.RenderSceneFrame.ApproachY                        ; переход, если X уже равен #77

                INC L
                OR A
                JP P, @Action.RenderSceneFrame.ApproachY                        ; переход, если разность положительна и шаг X уже выполнен

                DEC L
                DEC L
                ; Расчёт шага Y к #2B по тому же правилу.
ApproachY:      LD A, H
                SUB #2B
                NEG
                JR Z, @Action.RenderSceneFrame.SavePosition                     ; переход, если Y уже равен #2B

                INC H
                OR A
                JP P, @Action.RenderSceneFrame.SavePosition                     ; переход, если разность положительна и шаг Y уже выполнен

                DEC H
                DEC H
SavePosition:   LD (@ActionAimFollowState.Position), HL
                ; Сброс допуска и уровня AY, подготовка углов поворота базиса.
ResetFrame:     XOR A
                LD (@ActionProjectedBoundsState.CompanionMask), A
                LD (@ActionAyEffectsState.ChannelCLevel), A
                LD HL, (#9B95)
                LD (@ActionRenderPhases.Value.Phase0), HL
                LD A, (#9B97)
                LD (@ActionRenderPhases.Value.Phase2), A
                CALL @Action.RotateBankedBasis.Entry
                LD A, (@ActionRenderBasis.C00.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC00                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC00:       LD (@ActionPatchedVectorCoeffs.C00), A
                LD A, (@ActionRenderBasis.C10.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC10                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC10:       LD (@ActionPatchedVectorCoeffs.C10), A
                LD A, (@ActionRenderBasis.C20.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC20                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC20:       LD (@ActionPatchedVectorCoeffs.C20), A
                LD A, (@ActionRenderBasis.C01.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC01                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC01:       LD (@ActionPatchedVectorCoeffs.C01), A
                LD A, (@ActionRenderBasis.C11.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC11                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC11:       LD (@ActionPatchedVectorCoeffs.C11), A
                LD A, (@ActionRenderBasis.C21.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC21                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC21:       LD (@ActionPatchedVectorCoeffs.C21), A
                LD A, (@ActionRenderBasis.C02.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC02                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC02:       LD (@ActionPatchedVectorCoeffs.C02), A
                LD A, (@ActionRenderBasis.C12.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC12                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC12:       LD (@ActionPatchedVectorCoeffs.C12), A
                LD A, (@ActionRenderBasis.C22.High)
                CP #80
                JR NZ, @Action.RenderSceneFrame.StoreC22                        ; переход, если коэффициент отличается от #80, сохранить его

                INC A
StoreC22:       LD (@ActionPatchedVectorCoeffs.C22), A
                ; Проверка режима перед проекцией тела.
                LD A, (@ActionGlyphIndicatorState.Control.FirstMode)
                CP #01
                CALL NZ, @Action.PrepareBodyTransform.Entry                     ; вызов, если FirstMode отличается от 1
                CALL @Action.ProjectWideVectors.Entry
                ; Инициализация пустой очереди и сохранение настоящего SP.
                LD HL, #0001
                LD (#9BA1), HL
                LD BC, #0040
                LD HL, #A100
                LD (#E4A7), SP
                JR @Action.RenderSceneFrame.ReadRecord

                ; Проверка признака конца в младшем байте маркера.
CheckMarker:    LD A, L
                AND A
                JP M, @Action.ReadRenderQueue.Entry                             ; переход, если бит 7 младшего байта маркера установлен

AdvanceRecord:  EXX
                ADD HL, BC
                ; Чтение текущей записи через SP после установки маркера по смещению #1B.
ReadRecord:     LD SP, HL
                EX DE, HL
                LD HL, #001B
                ADD HL, DE
                LD A, #80
                LD (HL), A
                EX DE, HL
                EXX
                POP HL
                CP H
                JR Z, @Action.RenderSceneFrame.CheckMarker                      ; переход, если старший байт первого слова равен #80

                LD (#9B8F), HL
                LD A, H
                AND A
                JP P, @Action.RenderSceneFrame.CheckX                           ; переход, если старший байт X неотрицателен

                NEG
CheckX:         CP #70
                JR NC, @Action.RenderSceneFrame.AdvanceRecord                   ; переход, если модуль старшего байта X не меньше #70

                LD (@ActionPatchedVectorState.Input0), HL
                POP HL
                LD (#9B91), HL
                LD A, H
                AND A
                JP P, @Action.RenderSceneFrame.CheckY                           ; переход, если старший байт Y неотрицателен

                NEG
CheckY:         CP #70
                JR NC, @Action.RenderSceneFrame.AdvanceRecord                   ; переход, если модуль старшего байта Y не меньше #70

                LD (@ActionPatchedVectorState.Input1), HL
                POP HL
                LD (#9B93), HL
                LD A, H
                AND A
                JP P, @Action.RenderSceneFrame.CheckDepth                       ; переход, если старший байт глубины неотрицателен

                NEG
CheckDepth:     CP #70
                JR NC, @Action.RenderSceneFrame.AdvanceRecord                   ; переход, если модуль старшего байта глубины не меньше #70

                LD (@ActionPatchedVectorState.Input2), HL
                POP HL
                LD A, L
                LD (@ActionObjectVerticesState.ModelByteOffset), A
                LD A, H
                LD (@ActionRenderPhases.Value.Phase0), A
                POP HL
                LD (@ActionRenderPhases.Value.Phase1), HL
                LD A, (@ActionRenderPhases.Value.Phase2)
                LD B, A
                LD A, (@ActionRenderPhases.Value.Phase0)
                OR B
                LD A, #01
                JR Z, @Action.RenderSceneFrame.StorePhaseFlag                   ; переход, если первый и третий углы равны нулю

                XOR A
StorePhaseFlag: LD (#9B8D), A
                LD IY, @Action.RenderSceneFrame.ResumeTransform
                JP @Action.ComputePatchedVector.Entry

                ; Проверка результата арифметического преобразования.
ResumeTransform:JP PE, @Action.RenderSceneFrame.AdvanceRecord                   ; переход, если преобразование переполнилось

                EXX
                LD A, L
                EXX
                LD L, A
                EXX
                LD A, H
                EXX
                LD H, A
                ; Подготовка SP для записи трёх выходных слов в запись.
                LD DE, #0020
                ADD HL, DE
                LD SP, HL
                LD DE, (@ActionPatchedVectorState.Output2)
                PUSH DE
                LD HL, (@ActionPatchedVectorState.Output1)
                PUSH HL
                LD B, H
                LD HL, (@ActionPatchedVectorState.Output0)
                PUSH HL
                LD A, H
                AND A
                JP P, @Action.RenderSceneFrame.SaveAbsX                         ; переход, если старший байт результата X неотрицателен

                NEG
SaveAbsX:       LD C, A
                LD A, D
                AND A
                JP P, @Action.RenderSceneFrame.SaveAbsDepth                     ; переход, если старший байт результата глубины неотрицателен

                NEG
SaveAbsDepth:   LD E, A
                LD A, B
                AND A
                JP P, @Action.RenderSceneFrame.CompareDepth                     ; переход, если старший байт результата Y неотрицателен

                NEG
CompareDepth:   CP E
                JR NC, @Action.RenderSceneFrame.CompareX                        ; переход, если модуль Y не меньше модуля глубины

                LD A, E
CompareX:       CP C
                JR NC, @Action.RenderSceneFrame.ScaleLevel                      ; переход, если накопленный максимум не меньше модуля X

                LD A, C
                ; Расчёт уровня из максимального модуля.
ScaleLevel:     SRL A
                SUB #0F
                JR NC, @Action.RenderSceneFrame.ClearLevel                      ; переход, если половина максимума не меньше #0F, обнулить кандидат

                NEG
                JP @Action.RenderSceneFrame.CompareLevel

ClearLevel:     XOR A
CompareLevel:   LD C, A
                LD A, (@ActionAyEffectsState.ChannelCLevel)
                CP C
                JR NC, @Action.RenderSceneFrame.SaveLevel                       ; переход, если прежний уровень не меньше кандидата

                LD A, C
SaveLevel:      LD (@ActionAyEffectsState.ChannelCLevel), A
                LD A, D
                AND A
                JP M, @Action.RenderSceneFrame.AdvanceRecord                    ; переход, если глубина отрицательна, пропустить запись

                CP #1F
                LD A, (@ActionObjectVerticesState.ModelByteOffset)
                JP P, @Action.RenderSceneFrame.ReadModelHeader                  ; переход, если старший байт глубины не меньше #1F

                ADD A, #02
                LD (@ActionObjectVerticesState.ModelByteOffset), A
                ; Восстановление настоящего SP перед чтением заголовка модели.
ReadModelHeader:LD SP, (#E4A7)
                CALL @Action.ReadObjectHeaderWord.Entry
                ; JP @Action.PrepareProjectionScale.Entry, продолжение в PrepareProjectionScale.asm

                endmodule
                endmodule
