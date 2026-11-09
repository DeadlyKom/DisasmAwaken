"""29 действующих строк CONTROL, логический конец файла отделён от хвоста секторов."""
NAMES=('SystemsReady','SystemsNormal','ModeEnabled','ModeDisabled','FreeFlight','Targeting','ForwardView','RearView',
 'TargetLost','TargetsLocked','MissilePrefix','MissileSuffix','NoMissiles','TargetDestroyed','ShipDestroyed',
 'TargetNotLocked','TractorBeam','MissileDeparted','SystemDamaged','SystemsDamaged','AntimissileOn','TargetsForgot',
 'ObjectCollected','HyperWarmup','DockApproach','CargoEjected','MineEjected','NoMines','NoCargo')
SLOT=23
START,END=0x16CD,0x194A
ORIGIN=0xDADE
PATH='Source/Controls/Resources/FlightMessages.bin'
TAIL_PATH='Source/Resources/23_CONTROL/SectorTail.bin'
FORMAT='CP866_FLIGHT_MESSAGES_CR_LF'


def records(source):
    raw=source[START:END];rows=[];position=START
    for name,part in zip(NAMES,raw.split(b'\n')):
        data=part+b'\n';rows.append(dict(name=name,offset=position,address=ORIGIN+position,length=len(data),raw=data))
        position+=len(data)
    assert len(NAMES)==len(rows)==29 and position==END and raw.count(10)==29 and raw.endswith(b'\r\n')
    assert raw.split(b'\n')[-1]==b''
    for row in rows:assert row['raw'].decode('cp866').encode('cp866')==row['raw']
    assert rows[20]['address']==0xF32D and rows[23]['address']==0xF37F and rows[-1]['address']==0xF41C
    return rows
