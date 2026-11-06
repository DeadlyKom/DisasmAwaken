"""Публикация исходного кодировщика знаков с физическими именами трёх записей."""
from ClassifyActionRegionType import main
import ActionComponentEncodingFacts as facts

if __name__=='__main__':
    constants='\n                module ActionComponentEncodeConst\n'
    constants+=('SignBit'.ljust(16)+'equ #07').ljust(80)+'; знаковый разряд старшего байта кодируемого слова\n'
    constants+='                endmodule\n'
    main(facts,'ActionComponentEncoding','ActionComponentEncoding',(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionComponentEncodeConst',constants),))
