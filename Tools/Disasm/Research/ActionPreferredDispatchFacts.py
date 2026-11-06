"""Четыре ранее зарегистрированных физических фрагмента выбора опоры."""
from ActionPreferredRecordFacts import FUNCTIONS as ALL,CONTINUATIONS,COMMENTS,contract,operands as name_operands
FUNCTIONS={a:ALL[a] for a in (0xF51E,0xF535,0xF541,0xF54D)}
LOCAL={};LABELS={}
RENAMES={'Action.Unknown'+format(a,'04X')+'.Entry':'Action.'+value[0]+'.Entry' for a,value in FUNCTIONS.items()}
CONTRACTS={('Action',a):contract(a) for a in FUNCTIONS}

LOCATION={a:"окно ACTION C000..FFFF, физический банк 0" for a in FUNCTIONS}
