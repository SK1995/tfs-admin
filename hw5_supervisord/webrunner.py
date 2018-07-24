#!/usr/bin/python

from cgi import parse_qs

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/plain')])

    wsgi_content = env["wsgi.input"].read(0)
    request_uri_content = env["REQUEST_URI"]
    request_method_content = env["REQUEST_METHOD"]
    d = parse_qs(wsgi_content)
    return ["Method: " + request_method_content + "\n" +
        "Get content: " + request_uri_content + "\n" +
        "Post content: " + wsgi_content + "\n"]
