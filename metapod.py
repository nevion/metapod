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
        #print c.kind
        #print dir(c)
        #print dir(c.location)
        if (c.kind in (clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL) and c.location.file.name == _input):
            #print c.location.file, c.location.line, c.location.column, c.location.offset
            a_class = Class(c)
            result.append(a_class)
        elif c.kind == clang.cindex.CursorKind.NAMESPACE:
            child_classes = build_classes(_input, c)
            result.extend(child_classes)

    return result


def do_one(opts, _input):
    clang.cindex.Config.set_library_file('/usr/lib64/libclang.so.3.4')
    index = clang.cindex.Index.create()
    clang_args = ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__']+opts.args
    translation_unit = index.parse(_input, clang_args)

    classes = build_classes(_input, translation_unit.cursor)

    header_template = Template(filename=os.path.join('templates', 'struct_header.mako'))
    generated_header_template = Template(filename=os.path.join('templates', 'struct_generated_header.mako'))
    non_enum_classes = [x for x in classes if '::detail::enum_tag' not in x.bases]
    #print 'header declarations: \n' + header_template.render(classes=klasses)
    generated_header_body = generated_header_template.render(classes=non_enum_classes)
    generated_header_outname = os.path.join(os.path.dirname(_input), 'generated', os.path.basename(_input))
    if opts.stdout:
        print ('header definitions: %s\n'%(generated_header_outname)) + generated_header_body
    else:
        try:
            os.makedirs(os.path.dirname(generated_header_outname))
        except Exception as e:
            pass
        with file(generated_header_outname, 'w') as f:
            f.write(generated_header_body)

    rendered = ''
    enum_template = Template(filename=os.path.join('templates', 'enum'+'.mako'))
    enum_classes = [x for x in classes if '::detail::enum_tag' in x.bases]
    rendered += enum_template.render(classes=enum_classes, include_file=_input)
    struct_compiled_template = Template(filename=os.path.join('templates', 'struct_compiled.mako'))
    rendered += '\n' + struct_compiled_template.render(classes=non_enum_classes, size_check = opts.size_check)

    generated_cpp_outname = os.path.join(os.path.dirname(_input), 'generated', os.path.splitext(os.path.basename(_input))[0]+'.cpp')
    if opts.stdout:
        print ('compiled definitions: %s\n'%(generated_cpp_outname)) +rendered 
    else:
        try:
            os.makedirs(os.path.dirname(generated_cpp_outname))
        except Exception as e:
            pass
        with file(generated_cpp_outname, 'w') as f:
            f.write(rendered)


def main():
    global opts
    parser = argparse.ArgumentParser(description='database framelog upload script')
    parser.add_argument('--size-check', action='store_true', help='size-check')
    parser.add_argument('--debug', action='store_true', help='debug')
    parser.add_argument('--uml', action='store_true', help='uml')
    parser.add_argument('--stdout', action='store_true', help='output to stdout')
    parser.add_argument('input', help='input file')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='remainding args')
    opts = parser.parse_args()
    for _input in [opts.input]:
        try:
            do_one(opts, _input)
        except Exception as e:
            print 'error processing %s'%_input
            print e

if __name__ == '__main__':
    main()
