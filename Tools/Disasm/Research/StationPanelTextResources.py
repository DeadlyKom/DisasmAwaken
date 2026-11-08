"""Доказанные текстовые потоки банка станции, исходная CP866 сохраняется побайтно."""
RESOURCES=(
    (0x6E19,0x71BA,'QueuedMessages',17,'LF','DrawQueuedMessagePanel'),
    (0x71BA,0x7E53,'EquipmentDescriptions',34,'LF','UpdateEquipmentInfo'),
    (0x7E53,0x7E8F,'SaveSlotLabels',5,'CR','DrawSaveSlotPanel'),
    (0x7E8F,0x7ECB,'LoadSlotLabels',5,'CR','DrawLoadSlotPanel'),
    (0x7ECB,0x7F3C,'EnvironmentLabels',13,'CR','PrintEnvironmentRows'),
    (0x7F3C,0x80E4,'GameSettingsLabels',43,'CR','PrintGameSettingsRows'),
    (0x8262,0x832E,'DecodedMessages',2,'LF','PrintDecodedMessage'),
)


def path(name):
    return 'Source/Station/Resources/'+name+'.bin'


def records(data,separator):
    """Деление по фактическим LF либо CR, конечный LF завершает подписи CR."""
    if separator=='LF':
        assert data[0]==data[-1]==10
        chunks=data[1:-1].split(b'\n');offset=1
    else:
        assert data[-1]==10
        offset=int(data[0]==13)
        chunks=data[offset:-1].split(b'\r')
    result=[]
    for chunk in chunks:
        result.append((offset,chunk));offset+=len(chunk)+1
    assert offset==len(data)
    return result


def escaped(data):
    """Текст для чтения, управляющие и непечатаемые байты показаны явно."""
    return ''.join(chr(c) if 32<=c<127 else bytes([c]).decode('cp866') if c>=128
                   else '\\x'+format(c,'02X') for c in data)
