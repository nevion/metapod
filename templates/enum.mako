<%
def get_enum(x):
    for e in x.enums:
        if e.name == 'type':
            return e
    return None

def enum_keys(e):
    return [x[0] for x in e.valuepairs]

def is_enum_class(x):
    return '::detail::enum_tag' in x.bases

def is_fast_enum(x):
    return is_enum_class(x) and ('MAX' in enum_keys(get_enum(x)))
def is_general_enum(x):
    return is_enum_class(x) and ('MAX' not in enum_keys(get_enum(x)))
%>\
<%def name="enum_boilerplate(parents, c)">\
<%
for child in c.classes:
    enum_boilerplate(parents + [c], child)
accessor_name = c.name
flat_accessor_name = c.name
if len(parents) > 0:
    accessor_name = '::'.join([x.name for x in parents]) + '::'+accessor_name
    flat_accessor_name = '_'.join([x.name for x in parents]) + '_'+accessor_name
if not is_enum_class(c):
    return
_enum = get_enum(c)
%>\
% if is_fast_enum(c):
const char *${accessor_name}::str[${accessor_name}::size()] = {
% for f,v in _enum.valuepairs:
% if f != 'MAX':
    "${f}"${',' if i != len(c.fields)-2 else ''}
% endif
% endfor
};
% elif is_general_enum(c):
static const std::pair<const char *, ${accessor_name}::type> ${flat_accessor_name}_valuepairs[${len(_enum.valuepairs)}] = {
% for f,v in _enum.valuepairs:
    std::pair<const char *, ${accessor_name}::type>("${f}", ${accessor_name}::${f})${',' if i != len(c.fields)-1 else ''}
% endfor
};
size_t ${accessor_name}::size(){
    return ${len(_enum.valuepairs)};
}
const char* ${accessor_name}::string_at(const size_t index){
    return ${flat_accessor_name}_valuepairs[index].first;
}
${accessor_name}::type ${accessor_name}::value_at(const size_t index){
    return ${flat_accessor_name}_valuepairs[index].second;
}
% endif
</%def>\
% for c in classes:
<% enum_boilerplate([], c) %>\
% endfor
