"""State06, целиком исполненный малый эффект банка 3 и переход к проверенному State07."""
FUNCTIONS={0xF6EC:('StartSmallRecordEffect','Создание малого эффекта по заголовку модели и переход текущей записи к состоянию затухания 7')}
LOCAL={0xF720:'SetDecay'}
MODIFIED_WRITERS=((0xF711,0x6D39,0x6D38,1),(0xF71D,0x6D3D,0x6D3C,1))
CONTRACTS={('Action',0xF6EC):(
    ['HL, DE, BC и AF числовых аргументов не задают, F альтернативного AF учитывается результатом банкового выделения',
     'IX указывает Components и ModelOffset текущей FActionRecord, StateCode и Unknown11 доступны для записи',
     'действуют договоры ReadObjectHeaderWord, DispatchBank3Callback, Voxel.CreateSmallEffect и RestoreRuntimePage',
     'OBJECT3D загружен в банк 4, VOXAL0 и VOXAL в банк 3, список эффектов от A795 имеет отрицательный маркер State',
     'изначально выбран ACTION банка 0, 7FFD разблокирован, шесть дополнительных байтов CPU-стека доступны, IRQ исключены'],
    ['HL=D800, DE=00C0 и BC=0012 после полного возврата малого эффекта',
     'A=max(исходные Frames,26), F соответствует CP исходных Frames с 26 и не пересчитывается после возможной загрузки 26',
     'HL\', DE\' и BC\' содержат Components0, 1 и 2 текущей записи, исходные альтернативные пары не сохраняются',
     'при выделении AF\'=0054, при достижении отрицательного маркера A\'=1A и F\' равен входному альтернативному F',
     'IY указывает выбранную запись эффекта либо отрицательный маркер, IX и I/IM/IFF сохраняются, SP после RET увеличен на два',
     'старший байт заголовка модели задаёт Mode малого эффекта, его State=1A передаётся отдельно через альтернативный A',
     'при свободном слоте создана полная FVisualEffect с сохранёнными Components и ресурсом D800, при полном списке запись не создаётся',
     'в обоих случаях Enabled=1, Frames=max(прежние Frames,26), родитель получает StateCode=07 и Unknown11=12',
     'OUT 7FFD последовательно получает 14, 10, 13 и 10, итоговая полная конфигурация равна 10',
     'R получает 142+7*n M1 при выделении после n занятых записей либо 100+7*n при отрицательном маркере, ещё 2 M1 при прежних Frames<26'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IY, R, StateCode и Unknown11 родителя, условно запись эффекта, четыре операнда банка 3, Enabled, условно Frames, шесть временных байтов CPU-стека, 7FFD, SP внешним RET"],
    ['это исходная цель State06, при неудаче выделения переход к затуханию и включение обхода не отменяются',
     'Unknown11=12 означает 18 последующих вызовов State07 до освобождения при обычном проходе без иных писателей, это не универсальная длительность всех объектов',
     '32256 сценариев исполнили реальные чтение OBJECT3D, банковый создатель, выделение и оба возвратных хвоста до полного RET',
     'проверены исходные чётные ModelOffset, все Frames, все принудительные Mode и альтернативные F, тестовые подмены заголовка отмечены отдельно',
     'точные регистры, флаги, R, восемь банков, кратность записей и четыре настоящих OUT проверены, полное произведение входов не исчерпано',
     'неизвестный хвост банка 4 в модели заполнен A4, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись'])}
COMMENTS={
    0xF6EC:(['Чтение полного слова заголовка модели из OBJECT3D, для режима малого эффекта используется его старший байт.'],None),
    0xF6F2:(['Сохранение режима в альтернативном A для последующего обмена внутри банкового диспетчера.'],None),
    0xF6F4:(['Подготовка трёх Components родителя, EXX передаёт их в сохраняемый набор для заполнения FVisualEffect.'],None),
    0xF706:(['Подготовка отдельного State=26 для эффекта, это не режим и не новое состояние родителя.'],None),
    0xF709:(['Выбор настоящего CreateSmallEffect банка 3 и вызов через возвратный диспетчер общей RAM.'],None),
    0xF70F:(['Обновление допуска кадрового обхода независимо от наличия свободной записи эффекта.'],None),
    0xF714:(['Проверка минимальной оставшейся длительности обхода перед возможным увеличением.'],None),
    0xF719:([],'переход, если прежние Frames не меньше 26, сохранить их и установить затухание родителя'),
    0xF71B:(['Обновление Frames до 26, флаги предыдущего CP сохраняются.'],None),
    0xF720:(['Обновление состояния родителя до State07 и исходного счётчика затухания 18.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionSmallEffectConst','''
                ; Исходные параметры малого эффекта и последующего затухания родителя
                module ActionSmallEffectConst
EffectState     equ #1A                                                         ; State записи FVisualEffect, передаётся через альтернативный A
MinimumFrames   equ #1A                                                         ; минимальное число оставшихся обновлений обхода, 26
DecayState      equ #07                                                         ; исходный индекс StepTimedRecordDecay
DecayCount      equ #12                                                         ; 18 вызовов декремента State07 без вмешательства иных писателей
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF6EC):return operation
    for offset in range(6):
        name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        operation=operation.replace('(IX+#'+format(offset,'02X')+')','(IX + @FActionRecord.'+name+')')
    for literal,name in (('06','ModelOffset'),('0A','StateCode'),('11','Unknown11')):
        operation=operation.replace('(IX+#'+literal+')','(IX + @FActionRecord.'+name+')')
    for address,name in ((0xAACC,'ReadObjectHeaderWord'),(0x6CEF,'DispatchBank3Callback')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    return (operation.replace('LD HL, #EC00','LD HL, @Voxel.CreateSmallEffect.Entry')
            .replace('LD A, #1A','LD A, @ActionSmallEffectConst.EffectState',1)
            .replace('CP #1A','CP @ActionSmallEffectConst.MinimumFrames')
            .replace('LD A, #1A','LD A, @ActionSmallEffectConst.MinimumFrames')
            .replace('(#6D39)','(@ActionVisualEffectListState.Enabled)')
            .replace('(#6D3D)','(@ActionVisualEffectListState.Frames)')
            .replace('LD (IX + @FActionRecord.StateCode), #07','LD (IX + @FActionRecord.StateCode), @ActionSmallEffectConst.DecayState')
            .replace('LD (IX + @FActionRecord.Unknown11), #12','LD (IX + @FActionRecord.Unknown11), @ActionSmallEffectConst.DecayCount'))


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xF711,0xF71D):
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=item['target']-0x6000+0x23D,target_bank=5,target_region='Action',
                target_path='Source/Action/UpdateVisualEffects.asm',target_source_classified=True,writer_source_classified=True)
