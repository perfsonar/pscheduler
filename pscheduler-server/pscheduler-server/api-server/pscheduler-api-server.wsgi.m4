#
dnl The quoting forces M4 to process the line.
`#' WSGI File for __NAME__
#

import logging
import sys

sys.path.insert(0, '__API_DIR__')

from pschedulerapiserver import application


