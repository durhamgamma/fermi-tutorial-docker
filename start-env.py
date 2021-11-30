#!/usr/bin/env python
import os

#Print all environment variables
print( '\n'.join([f'{k}: {v}' for k, v in sorted(os.environ.items())]) )
