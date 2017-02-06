#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
import json

try:
    from urllib import parse as urlparse
    from urllib import request
except ImportError:
    import urllib2 as request
    import urlparse

import vim  # pylint: disable=import-error

def get_response(endPoint, params=None, timeout=None):
    parameters = {}
    parameters['line'] = vim.eval('line(".")')
    parameters['column'] = vim.eval('col(".")')
    parameters['buffer'] = '\r\n'.join(vim.eval("getline(1,'$')")[:])
    parameters['filename'] = vim.current.buffer.name

    if params is not None:
        parameters.update(params)

    if timeout == None:
        timeout = int(vim.eval('g:OmniSharp_timeout'))

    host = vim.eval('g:OmniSharp_host')

    if vim.eval('exists("b:OmniSharp_host")') == '1':
        host = vim.eval('b:OmniSharp_host')

    target = urlparse.urljoin(host, endPoint)

    proxy = request.ProxyHandler({})
    opener = request.build_opener(proxy)
    req = request.Request(target)
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = opener.open(req, json.dumps(parameters), timeout)
        vim.command("let g:serverSeenRunning = 1")
    except Exception:
        vim.command("let g:serverSeenRunning = 0")
        return None

    json_string = response.read()
    if json_string.startswith("\xef\xbb\xbf"):  # Drop UTF-8 BOM
        json_string = json_string[3:]
    return  json.loads(json_string)

class Completion:
    def get_completions(self, column, partialWord):
        parameters = {}
        parameters['column'] = vim.eval(column)
        parameters['wordToComplete'] = vim.eval(partialWord)

        parameters['WantDocumentationForEveryCompletionResult'] = \
            bool(int(vim.eval('g:omnicomplete_fetch_full_documentation')))

        want_snippet = \
            bool(int(vim.eval('g:OmniSharp_want_snippet')))

        parameters['WantSnippet'] = want_snippet
        parameters['WantMethodHeader'] = want_snippet
        parameters['WantReturnType'] = want_snippet

        parameters['buffer'] = '\r\n'.join(vim.eval('s:textBuffer')[:])

        response = get_response('/autocomplete', parameters)

        enc = vim.eval('&encoding')
        vim_completions = []
        if response is not None:
            for completion in response:
                complete = {
                    'snip': completion['Snippet'] or '',
                    'word': completion['MethodHeader'] or completion['CompletionText'],
                    'menu': completion['ReturnType'] or completion['DisplayText'],
                    'info': (completion['Description'] or '').replace('\r\n', '\n'),
                    'icase': 1,
                    'dup':1
                }
                vim_completions.append(complete)

        return vim_completions
