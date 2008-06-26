#!/usr/bin/env python

import cgitb
cgitb.enable()

import cgi
import cjson
import sys
import os

class Functional(object):
    """This class is a WSGI leaf that is designed to wrap functional code on the edge of a
       web application. This is specifically designed to allow integration of normal
       functions into code.

       """
    def __init__(self, callback, style="full",responsetype="text/plain"):
        self.callback = callback
        self.style = style
        self.responsetype = responsetype

    def call_callback(self, node, args):
        if self.style is "full":
            if node:
                status,headers,page = self.callback(jsonobject=node,**args)
            else:
                status,headers,page = self.callback(**args)
        elif self.style == "simple":
            if node:
                page = self.callback(node,**args)
            else:
                page = self.callback({}, **args)
            status,headers = "200 OK", [('Content-type',self.responsetype)]
        else:
            if node:
                status,headers,page = self.callback(node,**args)
            else:
                status,headers,page = self.callback({}, **args)


        return status,headers,page

    def __call__(self, environ, start_response):
        node = None
        args = environ.get("bbc.args",{})
        if args.get("__json__"):
            node = args["__json__"]
            del args["__json__"]
        args["__environ__"] = environ
        status,headers,page  = self.call_callback(node, args)
        start_response(status,headers)
        return [ page ]


                # Do we really prefer this to be:
                # status, headers, page = callback(**args,environ=environ)

                # HA! The content is actually TYPED.
                    # Go one stage further - what if the TYPE was more complex - but more akin to an object reference?
                # Actually want STATUS, mimetype, data as well.

class EnvironDumper(object):
    def __call__(self, environ, start_response):
        start_response('200 OK',[('Content-type','text/html')])
        yield '<html>'
        yield '<body>'
        yield '<h1> BBC Functional Environment Dumper </h1>'
        if environ.get("bbc.args"):
            yield '<h2> CGI Based URL Parameters</h2>'
            for arg in environ["bbc.args"]:
                yield "%s=%s (%s)" % (arg, repr(environ["bbc.args"][arg]),environ["bbc.args"][arg].__class__.__name__ )
                yield "<br>"
        yield '<h2> The rest of the WSGI Environment</h2>'
        yield "<ul>"
        for k in environ:
            yield "<li><b> %s</b> : %s</li>" % (str(k), repr(environ[k]))
        yield "</ul>"
        yield '</body>'
        yield '</html>'


class JSON_Interceptor(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if environ.get("bbc.args"):
            if environ["bbc.args"].get("__json__"):
                import sys
                json = environ["bbc.args"]["__json__"]
#                sys.stderr.write("JSON: %s\n" % json)
                environ["bbc.args"]["__json__"] = cjson.decode(json)

        R = self.application(environ, start_response)
        for line in R:
            yield line

from Cookie import SimpleCookie

class CookieExtracter(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        cookies_in = SimpleCookie()
        try:
            cookies_in.load(environ["HTTP_COOKIE"])
            cookies = {}
            for C in cookies_in:
                cookies[C] = cookies_in[C].value
            environ["bbc.cookies"] = cookies
        except KeyError:
            pass
        R = self.application(environ, start_response)
        for line in R:
            yield line

class CGI_Parser(object):
    def __init__(self, application, upload_dir="/tmp/uploads"):
        self.application = application
        self.upload_dir = upload_dir

    def get_new_filename(self):
        try:
            F = open( os.path.join(self.upload_dir, ".meta") )
            X = F.read()
            F.close()
        except IOError:
            X = ""

        try:
            meta = cjson.decode(X)
        except cjson.DecodeError:
            meta = { }

        next = meta.get("max", 0)+1
        meta["max"] = next

        F = open( os.path.join(self.upload_dir, ".meta"), "w" )
        F.write( cjson.encode(meta) )
        F.close()

        return os.path.join(self.upload_dir, str(next))
                
#        try:
#            files = os.listdir(self.upload_dir)
#        except OSError:
#            os.makedirs(self.upload_dir)
#            files  = os.listdir(self.upload_dir)
#        next = len(files) # This is fragile...
#        return os.path.join(self.upload_dir, str(next))

    def save_upload(self, fileitem, filename):
        if not fileitem.file:
            return
        fout = file (filename, 'wb')
        while 1:
            chunk = fileitem.file.read(10000)
#            sys.stderr.write("Upload: %s read %s bytes\n" % (fileitem.filename,len(chunk)) )
            if not chunk: break
            fout.write (chunk)
        fout.close()

    def __call__(self, environ, start_response):
        X = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)
        env = {}
        for f in X:
            try:
               X_filename = X[f].filename
            except AttributeError:
#               sys.stderr.write("Hmmm (%s)\n" %  f )
               env[f] = X.getvalue(f)
               continue

            if X[f].filename is None:
#                sys.stderr.write("Hmmm (%s)\n" %  f )
                env[f] = X.getvalue(f)
            else:
                if X[f].filename != "":
                    filename = self.get_new_filename()
                    try:
                        extension = os.path.basename(X[f].filename).split(os.path.extsep)[-1]
                    except:
                        extension = "dat"
                    filename = filename + os.path.extsep + extension
                    self.save_upload(X[f], filename)
#                    sys.stderr.write("We were sent a file %s (%s, to save as %s)\n" % (X[f].filename, f, filename) )
                    env[f+".__originalfilename"] = X[f].filename
                    env[f+".__filename"] = filename
#                    sys.stderr.write("key: %s filename: %s\n" % (f+".__filename",  filename))
        environ["bbc.args"] = env
        for line in self.application(environ, start_response):
            yield line

if __name__ == "__main__":
    from wsgiref.handlers import CGIHandler
    CGIHandler().run( CGI_Parser( JSON_Interceptor( EnvironDumper() ) ) )

"""
http://127.0.0.1/cgi-bin/app/people
http://127.0.0.1/cgi-bin/app/bbcwsgitools.py
http://127.0.0.1/cgi-bin/app/bbcwsgitools.py?hello=world
http://zetazeros.wordpress.com/2008/01/28/thesis-database-and-python-cgi-uploading/
http://www.google.com/search?num=100&hl=en&safe=off&client=firefox-a&rls=org.mozilla%3Aen-GB%3Aofficial&hs=VxG&q=%2Bpython+cgi+handle+%22large+file%22+upload&btnG=Search
http://wiki.pylonshq.com/display/pylonsdocs/Form+Handling
http://pythonpaste.org/
http://www.python.org/dev/peps/pep-0333/
"""
