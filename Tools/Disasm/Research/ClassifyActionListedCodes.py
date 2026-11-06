"""Защищённое выделение доказанного обхода кодов без изменения соседнего рисователя."""
from PublishActionRawFunction import main
import ActionListedCodesFacts as facts

if __name__=='__main__':main(facts,'ActionListedCodes',0xDDD1,0xDDF0,99712,allow_subrange=True)
