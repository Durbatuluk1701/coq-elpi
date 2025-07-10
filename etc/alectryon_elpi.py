#!/usr/bin/env python3
import sys
from os.path import join, dirname

# This is a custom driver: it exposes the same interface as
# Alectryon's usual CLI, but:
# - it sets the internal parameter pp_margin of SerAPI to a different value
# - it installs a new ghref RST role
# - it install a new pygments lexer for Elpi
# - it patches Coq's pygments lexer to handle quotations to Elpi

root = join(dirname(__file__), "..")
sys.path.insert(0, root)

# SERAPI ######################################################################

from alectryon.cli import main
from alectryon.serapi import SerAPI

SerAPI.DEFAULT_PP_ARGS['pp_margin'] = 55

# PYGMENTS ELPI ###############################################################

from pygments.lexer import RegexLexer, default, words, bygroups, include, inherit
from pygments.regexopt import regex_opt, regex_opt_inner
from pygments.token import \
    Text, Comment, Operator, Keyword, Name, String, Number, Punctuation

class ElpiLexer(RegexLexer):
    """
    Lexer for the Elpi programming language.
    """

    name = 'Elpi'
    url = 'http://github.com/LPCIC/elpi'
    aliases = ['elpi']
    filenames = ['*.elpi']
    mimetypes = ['text/x-elpi']
    version_added = '2.11'

    lcase_re = r"[a-z]"
    ucase_re = r"[A-Z]"
    digit_re = r"[0-9]"
    schar2_re = r"([+*^?/<>`'@#~=&!])"
    schar_re = rf"({schar2_re}|-|\$|_)"
    idchar_re = rf"({lcase_re}|{ucase_re}|{digit_re}|{schar_re})"
    idcharstarns_re = rf"({idchar_re}*(\.({lcase_re}|{ucase_re}){idchar_re}*)*)"
    symbchar_re = rf"({lcase_re}|{ucase_re}|{digit_re}|{schar_re}|:)"
    constant_re = rf"({ucase_re}{idchar_re}*|{lcase_re}{idcharstarns_re}|{schar2_re}{symbchar_re}*|_{idchar_re}+)"
    symbol_re = r"(,|<=>|-->|:-|:>|;|\?-|->|&|=>|\bas\b|\buvar\b|<|=<|=|==|>=|>|\bi<|\bi=<|\bi>=|\bi>|\bis\b|\br<|\br=<|\br>=|\br>|\bs<|\bs=<|\bs>=|\bs>|@|::|\[\]|`->|`:|`:=|\^|-|\+|\bi-|\bi\+|r-|r\+|/|\*|\bdiv\b|\bi\*|\bmod\b|\br\*|~|\bi~|\br~)"
    const_sym_re = rf"({constant_re}|{symbol_re}|\({symbol_re}\))"

    tokens = {
        'root': [
            include('elpi')
        ],

        'elpi': [
            include('_elpi-comment'),

            (r"(:before|:after|:if|:name)(\s*)(\")",
             bygroups(Keyword.ElpiMode, Text.Whitespace, String.Double),
             'elpi-string'),
            (r"(:functional)",
             bygroups(Keyword.ElpiMode)),
            (r"(:index)(\s*)(\()", bygroups(Keyword.ElpiMode, Text.Whitespace, Punctuation),
             'elpi-indexing-expr'),
            (rf"\b(external pred|pred)(\s+)({const_sym_re})",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-pred-item'),
            (rf"\b(func)(\s+)({const_sym_re})",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-func-item'),
            (rf"\b(external type|type)(\s+)(({const_sym_re}(,\s*)?)+)",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-type'),
            (rf"\b(kind)(\s+)(({const_sym_re}|,)+)",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-type'),
            (rf"\b(typeabbrev)(\s+)({const_sym_re})",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-type'),
            (r"\b(typeabbrev)(\s+)(\([^)]+\))",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-type'),
            (r"\b(accumulate)(\s+)(\")",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, String.Double),
             'elpi-string'),
            (rf"\b(accumulate|namespace|local)(\s+)({constant_re})",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Text)),
            (rf"\b(shorten)(\s+)({constant_re}\.)",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Text)),
            (r"\b(pi|sigma)(\s+)([a-zA-Z][A-Za-z0-9_ ]*)(\\)",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiVariable, Text)),
            (rf"\b(constraint)(\s+)(({const_sym_re}(\s+)?)+)",
             bygroups(Keyword.ElpiKeyword, Text.Whitespace, Name.ElpiFunction),
             'elpi-chr-rule-start'),

            (rf"(?=[A-Z_]){constant_re}", Name.ElpiVariable),
            (rf"(?=[a-z_])({constant_re}|_)(:[A-Za-z0-9_ ]*)?(\\)", Name.ElpiVariable),
            (r"_", Name.ElpiVariable),
            (rf"({symbol_re}|!|=>|;)", Keyword.ElpiKeyword),
            (constant_re, Text),
            (r"\[|\]|\||=>", Keyword.ElpiKeyword),
            (r'"', String.Double, 'elpi-string'),
            (r'`', String.Double, 'elpi-btick'),
            (r'\'', String.Double, 'elpi-tick'),
            #(r'\{\{', Punctuation, 'elpi-quote'),
            (r'\{[^\{]', Text, 'elpi-spill'),
            (r"\(", Punctuation, 'elpi-in-parens'),
            (r'\d[\d_]*', Number.Integer),
            (r'-?\d[\d_]*(.[\d_]*)?([eE][+\-]?\d[\d_]*)', Number.Float),
            (r"[\+\*\-/\^\.]", Operator),
        ],
        '_elpi-comment': [
            (r'%[^\n]*\n', Comment),
            (r'/(?:\\\n)?[*](?:[^*]|[*](?!(?:\\\n)?/))*[*](?:\\\n)?/', Comment),
            (r"\s+", Text.Whitespace),
        ],
        'elpi-indexing-expr':[
            (r'[0-9 _]+', Number.Integer),
            (r'\)', Punctuation, '#pop'),
        ],
        'elpi-type': [
            (r"(ctype\s+)(\")", bygroups(Keyword.Type, String.Double), 'elpi-string'),
            (r'->', Keyword.Type),
            (r'prop', Keyword.ElpiMode),
            (constant_re, Keyword.Type),
            (r"\(|\)", Keyword.Type),
            (r"\.", Text, '#pop'),
            include('_elpi-comment'),
        ],
        'elpi-chr-rule-start': [
            (r"\{", Punctuation, 'elpi-chr-rule'),
            include('_elpi-comment'),
        ],
        'elpi-chr-rule': [
           (r"\brule\b", Keyword.ElpiKeyword),
           (r"\\", Keyword.ElpiKeyword),
           (r"\}", Punctuation, '#pop:2'),
           include('elpi'),
        ],
        'elpi-pred-item': [
            (r"[io]:", Keyword.ElpiMode),
            (r"\.", Text, '#pop'),
            (r",", Keyword.ElpiMode),
            include('_elpi-inner-pred-fun'),
            (r"\)", Keyword.ElpiMode, '#pop'),
            (r"\(", Keyword.Type, '_elpi-type-item'),
            include('_elpi-comment'),
            include('_elpi-type-item'),
        ],
        'elpi-func-item': [
            (constant_re, Keyword.Type),
            (r"\.", Text, '#pop'),
            (r",", Keyword.ElpiMode),
            (r'->', Keyword.ElpiMode),
            include('_elpi-inner-pred-fun'),
            (r"\)", Keyword.ElpiMode, '#pop'),
            (r"\(", Keyword.Type, '_elpi-type-item'),
            include('_elpi-comment'),
            include('_elpi-type-item'),
        ],
        '_elpi-inner-pred-fun': [
            (r"(\()(\s*)(pred)", bygroups(Keyword.ElpiMode,Text.Whitespace,Keyword.ElpiKeyword), 'elpi-pred-item'),
            (r"(\()(\s*)(func)", bygroups(Keyword.ElpiMode,Text.Whitespace,Keyword.ElpiKeyword), 'elpi-func-item'),
        ],
        '_elpi-type-item': [
            (r'->', Keyword.Type),
            (constant_re, Keyword.Type),
            include('_elpi-inner-pred-fun'),
            (r"\(", Keyword.Type, '#push'),
            (r"\)", Keyword.Type, '#pop'),
            include('_elpi-comment'),
        ],

        ''

        'elpi-btick': [
            (r'[^` ]+', String.Double),
            (r'`', String.Double, '#pop'),
        ],
        'elpi-tick': [
            (r'[^\' ]+', String.Double),
            (r'\'', String.Double, '#pop'),
        ],
        'elpi-string': [
            (r'[^\"]+', String.Double),
            (r'"', String.Double, '#pop'),
        ],
        # 'elpi-quote': [
        #     (r'\}\}', Punctuation, '#pop'),
        #     (r"\s+", Text.Whitespace),
        #     (r"(lp:)(\{\{)", bygroups(Number, Punctuation), 'elpi-quote-exit'),
        #     (rf"(lp:)((?=[A-Za-z_]){constant_re})", bygroups(Number, Name.ElpiVariable)),
        #     (r"(lp:\()([A-Za-z]+)( )([^)]*)(\))", bygroups(Number, Name.ElpiVariable, Text.Whitespace, Text, Number)),
        #     (r"((?!lp:|\}\})(.|\n))+", using(CoqLexer)),
        # ],
        # 'elpi-quote-exit': [
        #     include('elpi'),
        #     (r'\}\}', Punctuation, '#pop'),
        # ],
        'elpi-spill': [
            (r'\{[^\{]', Text, '#push'),
            (r'\}[^\}]', Text, '#pop'),
            include('elpi'),
        ],
        'elpi-in-parens': [
            (r"\(", Punctuation, '#push'),
            include('elpi'),
            (rf"(\))(:[A-Za-z0-9_ ]*)?", bygroups(Punctuation,Name.ElpiVariable), '#pop'),
        ],
    }

from pygments.lexers._mapping import LEXERS
LEXERS['ElpiLexer'] = ('alectryon_elpi','Elpi',('elpi',),('*.elpi',),('text/x-elpi',))

# PYGMENTS COQ-ELPI ###########################################################

from alectryon.pygments_lexer import CoqLexer

class CoqElpiLexer(CoqLexer, ElpiLexer):

    tokens = {
      'root': [
            # No clue what inherit would do here, so we copy Coq's ones
            include('_basic'),
            include('_vernac'),
            include('_keywords'),
            include('_other'),
      ],
      '_quotations': [
            (r"lp:\{\{",String.Interpol, 'elpi'),
            (r"(lp:)([A-Za-z_0-9']+)",bygroups(String.Interpol, Name.ElpiVariable)),
            (r"(lp:)(\()([A-Z][A-Za-z_0-9']*)([a-z0-9 ]+)(\))",bygroups(String.Interpol,String.Interpol,Name.ElpiVariable,Text,String.Interpol)),
      ],
      'antiquotation': [
            (r"\}\}",String.Interpol,'#pop'),
            include('root')
      ],
      'elpi': [
            (r"\}\}",String.Interpol,'#pop'),
            (r"\b(global|sort|app|fun|let|prod|match|fix)\b", Keyword.ElpiKeyword),
            (r"\{\{(:[a-z]+)?",String.Interpol,'antiquotation'), # back to Coq
            inherit
      ],
      '_other': [
          include('_quotations'),
          inherit
      ],

    }

import alectryon.pygments_lexer
alectryon.pygments_lexer.CoqLexer = CoqElpiLexer

# DOCUTILS ####################################################################

import docutils
from docutils.parsers.rst import directives, roles # type: ignore
from docutils import nodes

def set_line(node, lineno, sm):
    node.source, node.line = sm.get_source_and_line(lineno)

import re
import time
import pickle
import atexit

ghref_cache = {}

def dump_ghref_cache():
    when = int(time.time() / 1000)
    file = '/tmp/ghref_cache_{}'.format(str(when))
    pickle.dump(ghref_cache,open(file,'wb'))

atexit.register(dump_ghref_cache)

try:
    when = int(time.time() / 1000)
    file = '/tmp/ghref_cache_{}'.format(str(when))
    ghref_cache = pickle.load(open(file,'rb'))
    #print('loaded cache', when, file)
except:
    #print('failed to loaded cache', file)
    ghref_cache = {}

ghref_scrape_re = re.compile("\"sha\"[: ]*\"([a-zA-Z0-9]+)\"",re.IGNORECASE)

def ghref_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    src = options.get('src',None)
    if src is None:
        msg = inliner.reporter.error("{}: no src option".format(role), line=lineno)
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    components = str.split(src,sep=" ")
    if len(components) != 4:
        msg = inliner.reporter.error("{}: src should be 4 space separated strings".format(role), line=lineno)
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    org, repo, branch, path = components
    uri = "https://github.com/{}/{}/blob/{}/{}".format(org,repo,branch,path)
    roles.set_classes(options)
    options.setdefault("classes", []).append("ghref")
    if uri in ghref_cache:
        code, rawuri, uri = ghref_cache[uri]
    else:
        from urllib import request
        apiuri = "https://api.github.com/repos/{}/{}/commits/{}/branches-where-head".format(org,repo,branch)
        try:
            with request.urlopen(apiuri) as f:
                json = f.read().decode('utf-8')
        except:
            msg = inliner.reporter.error("{}: could not download: {}".format(role,apiuri), line=lineno)
            return [inliner.problematic(rawtext, rawtext, msg)], [msg]
        try:
            # A json parser would be nicer
            sha = ghref_scrape_re.search(json).group(1)
        except:
            msg = inliner.reporter.error("{}: could not scrape for permalink: {}".format(role,uri), line=lineno)
            return [inliner.problematic(rawtext, rawtext, msg)], [msg]
        puri = "https://github.com/{}/{}/blob/{}/{}".format(org,repo,sha,path)
        rawuri = "https://raw.githubusercontent.com/{}/{}/{}/{}".format(org,repo,sha,path)
        try:
            with request.urlopen(rawuri) as f:
                code = f.read().decode('utf-8')
        except:
            msg = inliner.reporter.error("{}: could not download: {}".format(role,rawuri), line=lineno)
            return [inliner.problematic(rawtext, rawtext, msg)], [msg]
        ghref_cache[uri]=(code,rawuri,puri)
        uri=puri
    mangler = options.get('replace',None)
    mangler_with = options.get('replace_with','')
    if mangler is None:
        name = text
    else:
        name = re.sub(mangler,mangler_with,text)
    pattern = options.get('pattern','')
    from string import Template
    pattern = Template(pattern).safe_substitute(name = re.escape(name))
    pattern = re.compile(pattern)
    for num, line in enumerate(code.splitlines(), 1):
        if pattern.search(line):
            uri = uri + '#L' + str(num)
            break
    else:
        msg = inliner.reporter.error("{}: {} not found in {} using pattern {}".format(role,text,rawuri,pattern), line=lineno)
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    node = nodes.reference(rawtext, text, refuri=uri, **options)
    set_line(node, lineno, inliner.reporter)
    return [node], []
ghref_role.name = "ghref"
ghref_role.options = {
    # the GH source, 4 fields separated by space: org repo branch path. Eg
    #   :src: cpitclaudel alectryon master alectryon/docutils.py
    "src": directives.unchanged,
    # the regex to find the location in the raw file at path. I must use $name
    # this is replaced by the text in :ghref:`text`. Eg
    #   :pattern: ^def $name
    "pattern": directives.unchanged,
    # optionally mangle the name before substituting it in the regexp using
    # re.sub. Eg
    #   :replace: this
    #   :replace_with: that
    "replace": directives.unchanged,
    "replace_with": directives.unchanged
}

roles.register_canonical_role("ghref", ghref_role)

###############################################################################

__all__ = [ "ElpiLexer", "CoqElpiLexer"]

if __name__ == "__main__":
    main()
