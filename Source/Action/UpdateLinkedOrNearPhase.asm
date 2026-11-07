                module Action
                module UpdateLinkedOrNearPhase
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedNearState.md)
                ; -----------------------------------------
                ; Проверка перехода к связи и условное продолжение в обработке близкого вектора
                ; исходная запись 17, адреса F081..F086
                ; In:
                ;   IX указывает FActionRecord, действуют договоры CheckLinkedTargetTransition и UpdateNearVectorPhase
                ;   ACTION банка 0 выбран, десять дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   CheckLinkedTargetTransition выполняет выбор связанной записи либо фазовую проверку
                ;   при Carry сразу достигнут F0F8, это относится и к StateCode=0E, и к успешному фазовому переходу 14
                ;   при NC исполнение продолжается непосредственно в UpdateNearVectorPhase с его выходами, отдельного CALL либо RET между файлами нет
                ;   C, AF', IX, I/IM/IFF и paging сохраняются, остальные регистры и поля определяются исполненными детьми
                ;   PC=F0F8 и SP сохраняется, R добавляет 2 M1 к стоимости проверки перехода и при NC к стоимости общего хвоста
                ; Corrupt:
                ;   HL, DE, B, AF, HL', DE', BC', IY, R, условные поля и операнды по договорам детей, до десяти байтов CPU-стека
                ; Note:
                ;   исходная цель State03, Carry проверяет завершённый переход, а не достоверность нового индекса цели
                ;   жёсткий порядок include, (0) UpdateLinkedOrNearPhase.asm, (1) UpdateNearVectorPhase.asm
                ;   1664 сценария этого входа входят в общий отчёт 75008 сценариев, точные регистры, R, банки и записи сверены
                ;   общий F0F8, аппаратные IRQ, сборка и нативный запуск не исполнялись
                ; -----------------------------------------
                ; Проверка перехода к связанной записи либо фазового перехода с точным смыслом возвращаемого Carry.
Entry:          CALL @Action.CheckLinkedTargetTransition.Entry
                JP C, @Action.PrepareObjectOffsetTransform.Entry                ; переход, если Carry установлен после выбора связи либо фазового перехода, пропустить обработку близкого вектора

                ; JP @Action.UpdateNearVectorPhase.Entry, продолжение в UpdateNearVectorPhase.asm

                endmodule
                endmodule
