#!/usr/bin/python
# vim: set fileencoding=utf-8

import sys
import os
import clang.cindex
import itertools
from mako.template import Template
import argparse
opts = None

def get_annotations(node):
    return [c.displayname for c in node.get_children()
            if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR]

class Enum(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        self.valuepairs = []
        if opts.uml:
            print ' enum: %s: %s'%(self.name, cursor.type.spelling)
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier
        for c in cursor.get_children():
            #print 'enum class: ',c.kind
            #print c.displayname, c.enum_value
            #print dir(c)
            self.valuepairs.append((c.displayname, c.enum_value))

class Field(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        if opts.uml:
            print ' +%s: %s'%(self.name, cursor.type.spelling)
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier

class Method(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        if opts.uml:
            print ' %s(%s): %s'%(self.name, ', '.join(map(lambda x: '%s:%s'%(x.spelling, x.type.spelling), cursor.get_arguments())), cursor.result_type.spelling)
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier

class Class(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        if opts.uml:
            print 'class: %s'%(self.name,)
        self.bases = []
        self.methods = []
        self.fields = []
        self.enums = []
        self.annotations = get_annotations(cursor)

        for c in cursor.get_children():
            if opts.debug:
                print c.kind
            if c.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
                self.bases.append(c.spelling)
            elif (c.kind == clang.cindex.CursorKind.CXX_METHOD and
                c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                f = Method(c)
                self.methods.append(f)
            elif (c.kind == clang.cindex.CursorKind.FIELD_DECL and
                c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                f = Field(c)
                self.fields.append(f)
            elif (c.kind == clang.cindex.CursorKind.ENUM_DECL and
                c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                f = Enum(c)
                self.enums.append(f)
        if opts.uml:
            print ''

def build_classes(_input, cursor):
    result = []
    for c in cursor.get_children():
        if (c.kind in (clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL) and c.location.file.name == _input):
            a_class = Class(c)
            result.append(a_class)
        elif c.kind == clang.cindex.CursorKind.NAMESPACE:
            child_classes = build_classes(_input, c)
            result.extend(child_classes)

    return result


def do_one(opts, _input, output):
    clang.cindex.Config.set_library_file('/usr/lib64/libclang.so.3.4')
    index = clang.cindex.Index.create()
    clang_args = ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__']+opts.args
    translation_unit = index.parse(_input, clang_args)

    classes = build_classes(_input, translation_unit.cursor)
    rendered = ''
    tpl = Template(filename=os.path.join('templates', opts.template+'.mako'))

    if opts.template == 'struct':
        classes = [x for x in classes if '::detail::enum_tag' not in x.bases]
        rendered = tpl.render(classes=classes, include_file=_input, size_check=opts.size_check)
    elif opts.template == 'enum':
        classes = [x for x in classes if '::detail::enum_tag' in x.bases]
        rendered = tpl.render(classes=classes, include_file=_input)
    with file(opts.output, 'w') as f:
        f.write(rendered)


def main():
    global opts
    parser = argparse.ArgumentParser(description='database framelog upload script')
    parser.add_argument('--template', '-t', required=True, help='template')
    parser.add_argument('--size-check', action='store_true', help='size-check')
    parser.add_argument('--debug', action='store_true', help='debug')
    parser.add_argument('--uml', action='store_true', help='uml')
    parser.add_argument('--output', '-o', type=str, required=True, help='output')
    parser.add_argument('input', help='input file')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='remainding args')
    opts = parser.parse_args()
    for _input in [opts.input]:
        head,ext = os.path.splitext(_input)

        if ext == 'in':
            head,ext = os.path.splitext(head)
            output = head+ext
        else:
            output = head+'_generated'+ext
        try:
            print _input, output
            do_one(opts, _input, output)
        except Exception as e:
            print 'error processing %s'%_input
            print e

if __name__ == '__main__':
    main()
