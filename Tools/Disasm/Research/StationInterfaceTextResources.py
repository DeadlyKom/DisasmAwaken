"""Физические границы подписей интерфейса, общий LF хранится только один раз."""
RESOURCES=(
    (0x839A,0x84AA,'CaptionLabels','DrawCaptionItem',21,0),
    (0x84AA,0x8A3B,'CenteredItemTexts','DrawCenteredItem',43,30),
    (0x8A3B,0x8A89,'LegalStatusLabels','DrawItem00',5,0),
    (0x8A89,0x8A9B,'StatusFieldLabels','DrawItem00',4,0),
    (0x8A9B,0x8B82,'SystemInfoTemplate','DrawSystemInfoPanel',1,20),
    (0x8B82,0x8B8D,'NoPlanetsText','DrawSystemInfoPanel',0,0),
    (0x8B8D,0x8BC2,'GovernmentLabels','PrintSystemTraits',5,0),
    (0x8BC2,0x8BF3,'EconomyLabels','PrintSystemTraits',5,0),
    (0x8BF3,0x8C4C,'TradeHeadings','DrawTradePanel',1,2),
    (0x8C4C,0x8E19,'TradeGoodsLabels','DrawTradeNumericColumns',1,30),
    (0x8E19,0x8E57,'EquipmentHeadings','DrawEquipmentList',1,1),
    (0x8E57,0x9066,'EquipmentNames','PrintEquipmentRows',1,33),
    (0x90B2,0x90FD,'PoliticalAreaLabels','DrawSystemInfoPanel',5,0),
)


def path(name):return 'Source/Station/Resources/'+name+'.bin'


def verify(data):
    for start,end,name,consumer,lf,cr in RESOURCES:
        raw=data[start:end]
        assert raw.count(10)==lf and raw.count(13)==cr,(name,'delimiters')
    # Проверка общих ограничителей, принадлежащих следующему ресурсу либо предыдущему меню.
    assert data[0x8399:0x839B]==b'\n\n'
    assert all(data[a]==10 for a in (0x84AA,0x8A89,0x8B8D,0x8BC2))
