"""Выделение первого доказанного входа из 48 исходных байтов."""
from PublishActionRawFunction import main
import ActionDirectDecimalScrollFacts as facts

if __name__=='__main__':
    main(facts,'ActionDirectDecimalScroll',0x6010,0x6029,3584,
         allow_subrange=True,proof_tag='ActionDirectDecimal')
