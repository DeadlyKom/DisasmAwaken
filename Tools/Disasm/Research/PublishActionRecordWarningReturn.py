"""Три исходных байта E655..E657 заменяют свой бинарный фрагмент после проверки."""
from PublishActionRawFunction import main
import ActionRecordWarningReturnFacts as facts

if __name__=='__main__':main(facts,'ActionRecordWarningReturn',0xE655,0xE658,65536)
