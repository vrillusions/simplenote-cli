"""
Progress bar.

src: http://snipplr.com/view/25735/python-cli-command-line-progress-bar/

Note, when determining percent make sure one of the numbers is a float
example:
  >>> import math
  >>> currently = 23
  >>> total = 42
  >>> math.floor(currently / total * 100)
  0.0
  >>> math.floor(currently / total * 100.0)
  0.0
  >>> math.floor(currently / float(total) * 100)
  54.0

Update: This is solved now with __future__.division

"""
from __future__ import division
import sys
import time
import math

# Output example: [=======   ] 75%

# width defines bar width
# percent defines current percentage
def progress(width, percent):
    marks = math.floor(width * (percent / 100.0))
    spaces = math.floor(width - marks)

    loader = '[' + ('=' * int(marks)) + (' ' * int(spaces)) + ']'

    sys.stdout.write("%s %d%%\r" % (loader, percent))
    if percent >= 100:
        sys.stdout.write("\n")
    sys.stdout.flush()
