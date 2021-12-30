#!/usr/bin/env python

import webrepl
repl=webrepl.Webrepl(**{'host':'10.0.0.81','port':8266,'password':'markset','debug':True})
ver=repl.get_ver()
print(ver)

