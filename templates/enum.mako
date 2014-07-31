#include "${include_file}"
#include <utility>
<%
    def get_enum(x):
        for e in x.enums:
            if e.name == 'type':
                return e
        return None

    def enum_keys(e):
        return [x[0] for x in e.valuepairs]

    enum_classes = [x for x in classes if '::detail::enum_tag' in x.bases]
    fast_enum_classes =  [x for x in enum_classes if 'MAX' in enum_keys(get_enum(x))]
    general_enum_classes = [x for x in enum_classes if 'MAX' not in enum_keys(get_enum(x))]
%>
% for c in enum_classes:
% if c in fast_enum_classes:
<% _enum = get_enum(c) %>
const char *${c.name}::str[${c.name}::size()] = {
% for f,v in _enum.valuepairs:
% if f != 'MAX':
    "${f}"${',' if i != len(c.fields)-1 else ''}
% endif
% endfor
};
% elif c in general_enum_classes:
<% _enum = get_enum(c) %>
static const std::pair<const char *, ${c.name}::type> ${c.name}_valuepairs[${len(_enum.valuepairs)}] = {
% for f,v in _enum.valuepairs:
    std::pair<const char *, ${c.name}::type>("${f}", ${c.name}::${f})${',' if i != len(c.fields)-1 else ''}
% endfor
};
% endif
% endfor
