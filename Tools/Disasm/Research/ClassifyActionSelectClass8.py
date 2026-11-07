"""Выделение 17 исходных байтов поиска класса 8 из физического хвоста перед E98D."""
from PublishActionRawFunction import main
import ActionSelectClass8Facts as facts

if __name__=='__main__':
    main(facts,'ActionSelectClass8',0xE97C,0xE98D,6656,allow_subrange=True)
