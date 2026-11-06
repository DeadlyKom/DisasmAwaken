"""Выделение проверенного родительского прохода, физические адреса сохраняются."""
from PublishActionRawFunction import main
import ActionObjectVerticesFacts as facts

if __name__=='__main__':
    main(facts,'ActionObjectVertices',0xD5C9,0xD5F9,2560,allow_subrange=True)
