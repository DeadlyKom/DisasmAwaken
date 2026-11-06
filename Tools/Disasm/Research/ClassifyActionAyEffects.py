"""Публикация доказанного тика звуковых эффектов, без сборки и без выделения памяти."""
from ClassifyActionRegionType import main
import ActionAyEffectsFacts as facts


if __name__=='__main__':
    main(facts,'ActionAyEffects','ActionAyEffects',(
        ('CursorB',0xECF6,'операнд LD HL,nn по ECF5, поток канала B, банк 0'),
        ('ChannelCLevel',0xED83,'операнд LD A,n по ED82, исходный байт уровня C до деления на два')))
