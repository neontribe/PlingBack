def set_trace():
    import pdb, sys
    sys.stdout = sys.__stdout__
    sys.stdin = sys.__stdin__
    debugger = pdb.Pdb()
    debugger.set_trace(sys._getframe().f_back)