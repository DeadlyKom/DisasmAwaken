                module Station
                module ResumeActionPointer
                ; Документация [битовый резервуар, неизменность F, созданный на стеке возврат и SP+4](../../Docs/PackedWordAndActionReturn.md)
                ; -----------------------------------------
                ; Возобновление указателя после RET непрямого рисователя с продолжением восстановления AF
                ; исходная запись 4, файловые смещения #21DC..#21DE
                ; In:
                ;   HL, DE, BC и индексные регистры удовлетворяют ResumePointer, фоны, таблицы и параметры указателя подготовлены
                ;   SP указывает на FActionReturnFrame после RET рисователя, SavedAF по +0 и внешний ReturnAddress по +2
                ;   перед JP (HL) HandleStatusPanelAction создал FActionDrawFrame с DrawReturn=7F30, рисователь уже снял это первое слово
                ; Out:
                ;   HL, DE, BC, HL', DE', BC', IX и IY сохранены по ResumePointer, AF восстановлен из SavedAF
                ;   AF' рабочий указателя, I, IFF и IM сохранены, страница не меняется
                ;   UpdateBlocked=0, указатель возобновлён согласно его договору, PC равен внешнему ReturnAddress, SP увеличен на четыре
                ; Corrupt:
                ;   AF, AF' по указателю, SP по кадру, bitmap и состояние указателя согласно ResumePointer
                ; Note:
                ;   единственная инструкция CALL ResumePointer занимает три ранее невыделенных байта CD D8 63 по 7F30
                ;   после неё исполнение физически продолжается в RestoreActionAF, порядок include (0), (1) жёсткий
                ;   полный HandleStatusPanelAction проверен отдельно в StatusPanelAction, произвольные рисователи ограничены своими договорами
                ; -----------------------------------------
                ; возобновление указателя после снятия созданного DrawReturn рисователем
Entry:          CALL @Station.ResumePointer.Entry
                ; JP @Station.RestoreActionAF.Entry, продолжение в RestoreActionAF.asm

                endmodule
                endmodule
