                module Station
                module ActivateItem
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [активация и закрытие элемента](../../Docs/ActiveItem.md)
; -----------------------------------------
; Перенос элемента в конец списка, условная смена активного индекса и установка callback
; исходная запись 4, файловые смещения #6C81..#6CA9
; In:
;   HL - новая обёртка только для отсутствующего в списке DE-индекса, DE - требуемый индекс
;   ActiveItemState.NextCallback содержит адрес нового callback, здесь он записывается, но не вызывается
;   выполняются предусловия MoveItemToTail, GetItemFrameBit, CloseActiveItem и ToggleItemFrame на выбранных путях
;   HALT получает пробуждение с сохранением контекста, доступны операнды активного состояния и EventCode
; Out:
;   HL - значение NextCallback, DE и BC сохранены, IX и IY сохранены
;   при исходном бите 0 равном 1 активность и активный индекс не меняются, Callback заменяется NextCallback
;   при исходном бите 0 равном 0 прежний callback отключён, прежний элемент закрыт, Active=#FF, Index=DE
;   текущий элемент затем передан ToggleItemFrame, его бит 4 может запретить смену контура
;   A=((EventCode<<1) OR Carry_previous) AND #FF, F сохраняет предыдущие S,Z,P/V, берёт X/Y из нового A и Carry из EventCode.bit7
; Corrupt:
;   HL, AF, HL', AF' при перерисовках
; Note:
;   предыдущий Carry и S,Z,P/V берутся от GetItemFrameBit при уже выбранном элементе, иначе от последнего ToggleItemFrame
;   перед закрытием прежнего элемента Callback безусловно заменяется EmptyCallback, прежний внешний callback не вызывается
;   даже при запрете ToggleItemFrame новое Active и Index уже записаны, состояние контура и активности может различаться
;   при совпадении прежнего и нового индекса разрешённый контур может инвертироваться дважды и вернуться к исходному
;   MoveItemToTail текущего элемента вызывается до закрытия прежнего, последующий перенос прежнего может изменить конец списка
;   нет собственного постоянного стекового кадра, вложенные вызовы используют исходные кадры закрытия и рисователей
;   H', DE', BC', I и IFF сохраняются собственными процедурами, влияние ISR исключено предусловием, SP восстанавливается
; -----------------------------------------
                ; поиск текущего DE-индекса и перенос его обработчика до проверки бита контура
Entry:          CALL @Station.MoveItemToTail.Entry
                ; чтение бита 0 Flags по индексу DE с сохранением контекста
                CALL @Station.GetItemFrameBit.Entry
                JR NZ, @Station.ActivateItem.InstallCallback                    ; переход, если бит контура уже установлен, заменить только callback после переноса списка

                ; отключение прежнего callback перед CloseActiveItem, его внешний код вызываться не должен
                LD HL, @Station.EmptyCallback.Entry
                LD (@ActiveItemState.Callback), HL
                ; закрытие прежнего активного индекса, если байт активности ненулевой
                CALL @Station.CloseActiveItem.Entry
                ; установка активности до переключения контура нового элемента
                LD A, #FF
                LD (@ActiveItemState.Active), A
                ; сохранение требуемого индекса в операнде CloseActiveItem
                LD (@ActiveItemState.Index), DE
                ; ожидание пробуждения HALT, даже если бит 4 запретит последующее рисование
                HALT
                ; переключение контура требуемой записи с собственным условием запрета битом 4
                CALL @Station.ToggleItemFrame.Entry
                ; чтение кода события без изменения предыдущих флагов перед RLA
InstallCallback:LD A, (@InterfaceState.EventCode)
                ; расчёт A через удвоение EventCode и предыдущий Carry, новый Carry равен EventCode.bit7
                RLA
                ; чтение ранее сохранённого NextCallback из собственного изменяемого операнда LD HL
                LD HL, #0000
                ; установка нового callback закрытия без его немедленного исполнения
                LD (@ActiveItemState.Callback), HL
                RET

                endmodule
                endmodule
