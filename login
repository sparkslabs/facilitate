#!/usr/bin/env python

from bbcwsgitools import EnvironDumper, JSON_Interceptor, CGI_Parser, Functional, CookieExtracter
from Login import page_render_html


if __name__ == "__main__":
    import cgitb ; cgitb.enable()
    from wsgiref.handlers import CGIHandler

    CGIHandler().run(
        CGI_Parser(
          CookieExtracter(
            JSON_Interceptor( 
                Functional(page_render_html, style="fuller",responsetype="text/html") 
            ) 
          )
        ) 
    )
