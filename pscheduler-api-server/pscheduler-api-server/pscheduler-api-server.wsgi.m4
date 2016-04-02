#
dnl The quoting forces M4 to process the line.
`#' WSGI File for __NAME__
#

import sys
sys.path.insert(0, '__API_DIR__')

# TODO: Redirect stdout?
sys.stdout = sys.stderr

from pschedulerapiserver import application
