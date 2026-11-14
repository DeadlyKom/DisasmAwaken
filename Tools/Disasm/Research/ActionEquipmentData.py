"""Физическая раскладка, подтверждённая всей последовательностью встроенного описания оборудования."""
from PreviewSceneTables import render as render_records,parse as parse_records

SHIP=(
    ('MineMx1','число мин МХ-1'),('LaserGrad','лазер «Град»'),('LaserStorm1','лазер «Шторм-1»'),
    ('LaserStorm2','лазер «Шторм-2»'),('LaserDeath1','лазер «Смерть-1»'),('LaserDeath2','лазер «Смерть-2»'),
    ('AntiMissilePs1','противоракетная система ПС-1, читатель выбирает порог 1E'),
    ('AntiMissilePs2','противоракетная система ПС-2, читатель выбирает порог 3C'),
    ('ShieldFortress','защита «Крепость», читатель выбирает стоимость события 3'),
    ('ShieldDefense1','защита «Оборона-1», читатель выбирает стоимость события 2'),
    ('ShieldDefense2','защита «Оборона-2», читатель выбирает стоимость события 1'),
    ('BoostPhoton','форсажный движитель «Фотон»'),('BoostProton','форсажный движитель «Протон»'),
    ('RepairRd1','ремонтный дроид РД-1'),('RepairRd2','ремонтный дроид РД-2'),('RepairRd3','ремонтный дроид РД-3'),
    ('TractorBeam','система «Силовой луч»'),('Guidance','система наведения'),('HyperTrail','система «Гиперслед»'),
    ('ReturnSystem','система возврата'),('FreeFlight','система свободного полёта'),
    ('RefuelSystem','система заправки, FF запрещает ветвь пополнения счётчика'),
    ('FuelAdditive','система распознавания'),('TargetIdentity','идентификатор целей'),('RoutePlanner','маршрутизатор'),
    ('Cryogen','криогенная установка'),('LandingModule','посадочный модуль'),('CyberKiller','киберкиллер ККР-0562'),
    ('HyperDiablo','гиперсистема «Дьявол»'),('EndMarker','полный завершающий байт 80 авторского блока'))
SKIMMER=(
    ('FuelBenzol','топливо «Бензол»'),('MissileSrk1','число ракет СРК-1'),('MissileSrk2','число ракет СРК-2'),
    ('LaserPower','лазер «Силовой»'),('LaserHurr1','лазер «Ураган-1»'),('LaserHurr2','лазер «Ураган-2»'),
    ('ShieldArmor1','защита «Броня-1»'),('ShieldArmor2','защита «Броня-2»'),
    ('JumpFar1','прыжковый движитель «Даль-1»'),('JumpFar2','прыжковый движитель «Даль-2»'),
    ('AntiMissile','противоракетная система'),('DockingNode','стыковочный узел'),('DriveModule','ходовой модуль'),
    ('BombBr0910','бомба БР-0910'),('EndMarker','полный завершающий байт 80 авторского блока'))
FIELDS=(('Value',1,'полный числовой байт, отдельные битовые флаги не назначаются'),)
TABLES=(('ActionShipEquipment','Source/Action/Data/ShipEquipment.asm',0x3C14,0x3C32,'FEquipmentCode',FIELDS,tuple(n for n,_ in SHIP)),
        ('ActionSkimmerEquipment','Source/Action/Data/SkimmerEquipment.asm',0x3C32,0x3C41,'FEquipmentCode',FIELDS,tuple(n for n,_ in SKIMMER)))


def render(source,table):
    text,labels=render_records(source,table,0x6000)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                      '[происхождение имён и проверенные потребители](../../../Docs/ActionEquipmentCodes.md)')
    meanings=SHIP if table[0]=='ActionShipEquipment' else SKIMMER
    resolved={
        'FuelAdditive':'В заметке «С распознавания», на станции «Присадка к топливу», наличие сокращает ожидание гиперперехода',
        'TargetIdentity':'Идентификатор целей, при отсутствии радар рисует все допущенные объекты формой 1',
        'HyperDiablo':'В заметке гиперсистема «Дьявол», станционная строка «Анекдот», остаточный сброс проверяет весь код',
    }
    for name,note in meanings:
        needle='                ; исходная физическая запись '+name+'\n';assert text.count(needle)==1
        text=text.replace(needle,needle+'                ; '+resolved.get(name,'По встроенному описанию, '+note)+'\n')
    return text,labels


def parse(text,table):return parse_records(text,table,0x6000)


def structure():
    return '''
                ; Байтовый код либо счётчик оборудования по физической раскладке авторского описания
                struct FEquipmentCode
Value           db #00                                                          ; полный байт, трактовка счётчика, наличия и маркера зависит от записи
                ends
                assert FEquipmentCode == 1
                assert FEquipmentCode.Value == 0
'''


def name_operands(region,address,operation):
    if region!='Action':return operation
    for byte,name in ((0x9C1A,'AntiMissilePs1'),(0x9C1B,'AntiMissilePs2'),(0x9C1C,'ShieldFortress'),
                      (0x9C1D,'ShieldDefense1'),(0x9C1E,'ShieldDefense2'),(0x9C29,'RefuelSystem')):
        operation=operation.replace('(#'+format(byte,'04X')+')','(@ActionShipEquipment.'+name+'.Value)')
    return operation
