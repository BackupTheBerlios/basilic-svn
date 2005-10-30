# ______________________________________________________________________
"""Module HTTPServer
Part of Basilic Project.
http://basilic.berlios.de/

(c) 2004-2005 - Olivier Deckmyn

Implementation of the HTTP server for Basilic.
Configuration don't stand here, but in config module.

$Id: httpserver.py 10 2005-10-30 16:47:54Z odeckmyn $
"""
# ______________________________________________________________________



import urllib, shutil, string
from cStringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import decoder, api


class HTTPHandler(BaseHTTPRequestHandler):

    def exec_test(self, stream, params=None):
        """Executes a "test" operation. Result is sent trough stream."""
        api.operation_test(self.server.basilic, stream, params)

    def exec_request(self, stream, params=None):
        """Executes a "request" operation. Result is sent trough stream."""
        (userlogin,userbase,tags,format)=decoder.decode_request(params)
        api.operation_request(self.server.basilic, stream, params)

    def _serve(self, send=1):
        f=StringIO()
        (operation, params)=decoder.decode_path(self.path)

        # Run the exec_<operation> method now
        mname = 'exec_' + operation
        if not hasattr(self, mname):
            self.send_error(501, _("Unknown operation (%s)") % `operation`)
            return
        method = getattr(self, mname)
        method(f,params)

        length=f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if send:
            shutil.copyfileobj(f, self.wfile)
        f.close()

    def do_HEAD(self):
        """Serves a HEAD request."""
        self._serve(send=0)

    def do_GET(self):
        """Serve a GET request."""
        self._serve(send=1)


class Server:

    def __init__(self, basilic):
        self.basilic=basilic
        self.server_config=basilic.config['http-server']

    def run(self):
        server_address = (self.server_config["host"], self.server_config["port"])
        httpd = HTTPServer(server_address, HTTPHandler)
        httpd.basilic=self.basilic
        sa = httpd.socket.getsockname()
        print "---"
        print "%s running %s server :" % (self.basilic.version.name, "HTTP")
        print "  host: %s" % sa[0]
        print "  port: %s" % sa[1]
        print "---"
        httpd.serve_forever()

