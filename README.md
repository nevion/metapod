# metapod

## Introduction

metapod is a code generation utility for performing some ahead-of-compile-time introspection on POD datatypes (e.g. simple data structs) and performing some menial code generation on them.  Some tasks I have used it for include:

* Autocoding templated visitor methods - [the visitor pattern](http://en.wikipedia.org/wiki/Visitor_pattern) is a very simple but very helpful pattern in generic programming: 
* Adding size checks to ensure IOs of PODS (packed or unpacked in memory) have the correct number of bytes - a real life-saver for protocol implementation or communications code.
* Autocoding YAML apply/encode methods
* Autocoding HDF5 Compound Type construction

C++11 handles the heavy lifting using type traits and other template tricks, this tool just addresses the lack of class introspection with the help of clang.  A benefit of this approach is that the generated code has no dependence on clang and should be usable on any compiler decent compiler.

One of helpful bits this utility has enabled is less dependence on ```__attribute__(((packed)))```.  Packed structures carry as many disadvantages as advantages such as:

* Not being able to take the address of fields
* Unaligned accesses.

Instead, simply make an IOing visitor object which handles POD types itself and together with the autocoded size-checks you can be sure you're packing bytes correctly, potentially performing endian conversions along the way, optionally using field names in the process.

Note: the python binding of clang is a bit of a second class citizen - functional but ever changing and often running behind the C++ libraries and sometimes breaking.


## Examples

`./metapod.py --uml --hdf --size-check ../path/to/types.h -I../path/to/includes `
`./metapod.py --yaml ../path/to/types.h -I../path/to/includes `

## Output
Output will be relative to input files to prevent file collisions - look for
* path/to/generated/types.h for templated autocode - to be included at the bottom of path/to/generated/types.h" before the final #endif
* path/to/generated/types.cpp for non-template related code - add this to your project build files


## Dependencies

* Python
* Mako
* Clang
