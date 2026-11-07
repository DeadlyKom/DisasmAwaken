# State10, таймер и связанный сегмент

[StepTimedLinkedOverlay](../Source/Action/StepTimedLinkedOverlay.asm) занимает F3C8..F3EF ACTION банка 0. PhaseMoveTimer уменьшается по модулю 256. Только исходная единица даёт ноль и приводит к записи StateCode из полного Unknown19. Исходный ноль превращается в FF и продолжает обычный путь. Достоверность будущего кода состояния здесь не проверяется.

При ненулевом новом таймере [PrepareLinkedRecordContext](../Source/Action/PrepareLinkedRecordContext.asm) выбирает связанную запись и сохраняет Components текущей. Если он вернул Z, обработчик сразу продолжает общий F0F8. Иначе обновляется отдельный поток 0.

При L нового слова не меньше полного Unknown11 управление передаётся в [CheckClass17SpawnWindow](../Source/Action/CheckClass17SpawnWindow.asm). Его проверки A=F0, H>=5F, класса и Unknown14 могут создать ребёнка и обновить Unknown14. При L<Unknown11 исполняется [CheckAndToggleLinkedOverlay](../Source/Action/CheckAndToggleLinkedOverlay.asm) до полного возврата, включая оба проецируемых вектора, отсечение и XOR-пиксели. Его Carry обработчик игнорирует. Оба пути затем доходят до F0F8.

IX, I, IM, IFF и paging сохраняются. Рабочие пары, альтернативные регистры и IY определяются реально достигнутыми детьми. Внешний SP сохраняется. Изменения таймера, кэша и обратной связи не откатываются при последующем экранном отказе.

[Модель](../Tools/Disasm/Research/ReferenceActionTimedLinkedState.py) и [проверка](../Tools/Disasm/Research/CheckActionTimedLinkedState.py) исполняют настоящий State10 до F0F8. Прошли 65536 сценариев, все пары таймера и Unknown11, с истечением, оборачиванием нуля, обычной и особой связью, отказом контекста, созданием и рисованием. Сверены регистры, все восемь банков и кратность RAM-записей. R проверяется точно на путях без растеризатора. [Результат](../Tools/Disasm/Reports/ActionTimedLinkedStateVerification.json).

Общий F0F8, полное произведение входов, R и точные T растеризатора, аппаратные IRQ, сборка и нативная игра не проверялись.
