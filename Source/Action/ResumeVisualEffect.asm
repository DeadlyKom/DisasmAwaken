                module Action
                module ResumeVisualEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionVisualEffectWalk.md)
                ; -----------------------------------------
                ; Восстановление стека и банковый вызов рисователя эффекта при положительной глубине
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #100E..#1067
                ; In:
                ;   AF задаёт P/V вычислителя, IX указывает текущий эффект, SavedSP заполнен обходчиком
                ;   три слова результата доступны в странице 0
                ; Out:
                ;   настоящий SP восстановлен, при переполнении либо неположительной глубине управление передаётся SetStride
                ;   на пути рисования выбирается страница 3, после возврата восстановлены IX и страница 0, затем переход в SetStride
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, буфер и побочные записи рисователя на пути вызова
                ; Note:
                ;   в сквозных моделях сверены все выходы ветвления, рамка, страницы и 3072 байта растрового буфера
                ; -----------------------------------------
                ; Восстановление настоящего SP из операнда, заполненного обходчиком.
Entry:          LD SP, #0000
                ; Проверка переполнения преобразования.
                JP PE, @Action.UpdateVisualEffects.SetStride                    ; переход, если преобразование переполнилось, пропустить рисование

                ; Проверка знака глубины.
                LD BC, (@ActionPatchedVectorState.Output2)
                BIT 7, B
                JP NZ, @Action.UpdateVisualEffects.SetStride                    ; переход, если глубина отрицательна, пропустить рисование

                ; Проверка нулевой глубины перед использованием логарифмического делителя.
                LD A, B
                OR C
                JP Z, @Action.UpdateVisualEffects.SetStride                     ; переход, если глубина равна нулю, пропустить рисование

                ; Подготовка двух координат, режима эффекта, адреса и размеров ресурса.
                LD HL, (@ActionPatchedVectorState.Output0)
                LD DE, (@ActionPatchedVectorState.Output1)
                LD A, (IX + @FVisualEffect.Mode)
                EX AF, AF'
                EXX
                LD L, (IX + @FVisualEffect.Unknown10)
                LD H, (IX + @FVisualEffect.Unknown11)
                LD E, (IX + @FVisualEffect.Source)
                LD D, (IX + @FVisualEffect.Source + 1)
                LD A, L
                EXX
                ; Вычисление начальной координаты X с вычитанием половины ширины ресурса.
                PUSH BC
                SRL A
                LD C, A
                LD B, #00
                OR A
                SBC HL, BC
                PUSH HL
                ; Вычисление начальной координаты Y с вычитанием половины высоты ресурса.
                EXX
                LD A, H
                EXX
                SRL A
                LD C, A
                EX DE, HL
                OR A
                SBC HL, BC
                EX DE, HL
                POP HL
                POP BC
                ; Выбор страницы рисователя, передача режима и сохранение указателя записи.
                LD A, #13
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                PUSH IX
                CALL #FA3A
                POP IX
                ; Восстановление страницы 0 и передача управления к следующей записи.
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                JP @Action.UpdateVisualEffects.SetStride

                endmodule
                endmodule
