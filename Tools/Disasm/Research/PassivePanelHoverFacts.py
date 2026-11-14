"""Пустые наведения пяти панелей, подтверждённые физическими записями и заголовками."""
PANELS=((11,0x6C0A,0x6D43,'GalaxyMap','карты галактики'),(19,0x7676,0x7687,'SystemInfo','информации о системе'),
 (20,0x7838,0x7884,'SystemMap','карты системы'),(32,0xAA55,0xAA84,'Contract','контракта'),(45,0x7948,0x7954,'Welcome','приветствия'))
FUNCTIONS={};RENAMES={};CONTRACTS={};DOCUMENTS={};COMMENTS={};TARGETS={};LABELS={}
for index,proxy,noop,name,title in PANELS:
 parent='Handle'+name+'Hover';child='Ignore'+name+'Hover'
 FUNCTIONS[proxy]=(parent,'Пустая JP-обёртка наведения панели '+title)
 FUNCTIONS[noop]=(child,'Игнорирование наведения панели '+title+' с полным сохранением контекста')
 RENAMES['HandleItem'+str(index).zfill(2)]=parent;RENAMES['Unknown'+format(noop,'04X')]=child;TARGETS[noop]='Station.'+child+'.Entry'
 for address in (proxy,noop):
  CONTRACTS['Station',address]=(
   ['нет регистровых параметров, исходный код Entry и обычный CPU-возврат доступны'],
   ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
    'память, bitmap, список рисования, курсор, страница и порты не меняются'],
   ['нет, кроме обычного потребления CPU-возврата'],
   ['физическая FInterfaceItem '+str(index)+' указывает на эту JP-обёртку, исходный заголовок подтверждает назначение панели',
    'основное действие Entry+3 не выполняется при наведении, его отдельный алгоритм не подменяется этим пустым контрактом',
    'обёртка не создаёт нового кадра CALL, обе точки сохраняют все 65536 значений AF'])
  DOCUMENTS['Station',address]=('PassivePanelHovers','физические владельцы пяти пустых наведений и сохранение каждого AF')
 COMMENTS[proxy]=(['передача наведения панели '+title+' в её пустой обработчик без нового CPU-кадра'],None)
 COMMENTS[noop]=(['наведение панели '+title+' не меняет состояние и не запускает основное действие'],None)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for target,name in TARGETS.items():operation=operation.replace('#'+format(target,'04X'),'@'+name)
 return operation


# Даже пустой RET изменяет R, хвостовой JP добавляет ещё один M1.
for _index,_proxy,_noop,_name,_title in PANELS:
    for _address,_m1 in ((_proxy,2),(_noop,1)):
        _parts = [list(part) for part in CONTRACTS['Station',_address]]
        _parts[0].append('IRQ и NMI не вмешиваются между входом и обычным возвратом, точный счёт R относится к этому условию')
        _parts[2] = ['R, SP и PC по обычному возврату']
        _parts[3].append('R увеличивает младшие семь битов на '+str(_m1)+' modulo 128, бит 7 сохраняется, IRQ в модели не исполняется')
        CONTRACTS['Station',_address] = tuple(_parts)
