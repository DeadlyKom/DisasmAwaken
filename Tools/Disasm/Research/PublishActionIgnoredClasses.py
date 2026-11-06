"""Публикация существующего общего RET после проверки полного диспетчерского пути."""
import ActionIgnoredClassesFacts as facts
from PublishActionRawFunction import main

if __name__=='__main__':
    main(facts,'ActionIgnoredClasses',0x6524,0x6525,832,allow_subrange=True)
