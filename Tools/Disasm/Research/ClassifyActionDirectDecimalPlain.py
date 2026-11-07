"""Выделение второго доказанного входа без изменения исходных обращений."""
from PublishActionRawFunction import main
import ActionDirectDecimalPlainFacts as facts

if __name__=='__main__':
    main(facts,'ActionDirectDecimalPlain',0x6029,0x6040,3584,
         proof_tag='ActionDirectDecimal')
