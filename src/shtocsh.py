#!/bin/env python3
# shtocsh -- convert SOME sh syntax to csh syntax to support using pastes;

if True:
    import os
    import sys


shfile = sys.argv[1]
nm, src_ext = os.path.splitext(shfile)
obuf = [ ]
with open(shfile, 'r') as ifd:
    for ln in ifd.readlines():
        s = ln.replace("export ", "setenv ")
        s = s.replace("=", " ")
        obuf.append(s)
ostr = "\n".join(obuf)
cshfile = f"{nm}.csh"
with open(cshfile, 'w') as ofd:
    ofd.write(ostr)
sys.exit(0)
