import i18n
import time

name="Basilic"
version="0.2"
copyright="2004-%d Olivier Deckmyn" % time.localtime()[0]
project_url="http://basilic.sourceforge.net/"
see_url=_("see %s") % project_url

version_string="%s - v%s" % (name, version,)
full_copyright="""%s version %s
(c)%s
%s""" % (name, version, copyright, see_url)

