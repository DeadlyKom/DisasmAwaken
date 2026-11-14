                module Action
                module ResumeVisualEffect
                ; Документация [контракт обёртки](../../Docs/ActionVisualEffectResume.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionVisualEffectWalk.md)
                ; -----------------------------------------
                ; Восстановление стека и банковый вызов рисователя эффекта при положительной глубине
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #100E..#1067
                ; In:
                ;   HL, DE, BC входных аргументов не задают, AF задаёт P/V вычислителя, IX указывает FVisualEffect
                ;   SavedSP по 6DD2 задаёт настоящий SP в общей RAM, страница 0 выбрана, paging доступен
                ;   Output0, Output1 и Output2 задают горизонталь, вертикаль и глубину, Mode допустим для DrawProjectedEffect
                ;   FramePointer указывает ресурс банка 3, FrameWidth и FrameHeight задают размеры, действуют договоры рисователя и его детей
                ;   CPU-стек и буферы доступны по договорам детей, IRQ не вмешиваются
                ; Out:
                ;   на всех путях SP равен SavedSP, внешний возврат не снимается, PC=UpdateVisualEffects.SetStride
                ;   при входном P/V=1 все регистры кроме SP, PC и R сохраняются, записей памяти и OUT нет, R получает 2 M1
                ;   при P/V=0 и отрицательной глубине BC=Output2, A сохранён, F от BIT 7,B с исходным Carry, R получает 7 M1
                ;   при P/V=0 и нулевой глубине BC=0, AF=0044, R получает 10 M1
                ;   оба выхода по глубине сохраняют HL, DE, альтернативные и индексные регистры, I, IM и IFF, без записей памяти и OUT
                ;   при положительной глубине рисователь получает центр с вычтенными половинами размеров, исходные размеры и FramePointer в альтернативном наборе
                ;   после рисователя HL, DE, BC, F, альтернативные пары и IY сохраняют его результат, A=10, IX восстановлен, выбрана страница 0
                ;   после возврата рисователя два слова перед SavedSP получают BC дочернего выхода и адрес 6E28
                ;   на рисующей ветви I, IM и IFF сохраняются при договорах детей, порты 7FFD получают 13 и 10
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, SP восстановлением, paging, буфер, операнды и стек по договорам детей
                ; Note:
                ;   1152 ранних выхода сверяют все регистры и R, 168 рисующих вызовов сверяют подготовку, результат ребёнка и точные записи завершающего кода
                ;   полная геометрия дочернего рисователя имеет отдельные проверки, точные R/T рисующей ветви и IRQ не проверены
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
                LD L, (IX + @FVisualEffect.FrameWidth)
                LD H, (IX + @FVisualEffect.FrameHeight)
                LD E, (IX + @FVisualEffect.FramePointer)
                LD D, (IX + @FVisualEffect.FramePointer + 1)
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
                CALL @Voxel.DrawProjectedEffect.Entry
                POP IX
                ; Восстановление страницы 0 и передача управления к следующей записи.
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                JP @Action.UpdateVisualEffects.SetStride

                endmodule
                endmodule
