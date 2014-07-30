#!/usr/bin/python
# vim: set fileencoding=utf-8

import sys
import os
import clang.cindex
import itertools
from mako.template import Template

def get_annotations(node):
    return [c.displayname for c in node.get_children()
            if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR]

class Field(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        print ' +%s: %s'%(self.name, cursor.type.spelling)
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier

class Method(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        print ' %s(%s): %s'%(self.name, ', '.join(map(lambda x: '%s:%s'%(x.spelling, x.type.spelling), cursor.get_arguments())), cursor.result_type.spelling)
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier

class Class(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        print 'class: %s'%(self.name,)
        self.methods = []
        self.fields = []
        self.annotations = get_annotations(cursor)

        for c in cursor.get_children():
            #print c.kind
            if (c.kind == clang.cindex.CursorKind.CXX_METHOD and
                c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                f = Method(c)
                self.methods.append(f)
            elif (c.kind == clang.cindex.CursorKind.FIELD_DECL and
                c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                f = Field(c)
                self.fields.append(f)
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
    translation_unit = index.parse(_input, ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__'])

    classes = build_classes(_input, translation_unit.cursor)
    tpl = Template(filename='struct.mako')
    rendered = tpl.render(classes=classes, include_file=_input)
    print output
    with open(output, "w") as f:
        f.write(rendered)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='database framelog upload script')
    parser.add_argument('input', nargs='+', help='input files')
    opts = parser.parse_args()
    for _input in opts.input:
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
