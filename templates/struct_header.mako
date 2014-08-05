<%
def is_enum_class(x):
    return '::detail::enum_tag' in x.bases
%>
<%def name="gen_visitors(parents, c)">
<%
for child in c.classes:
    if not is_enum_class(child):
        gen_visitors(parents + [c], child)
accessor_name = c.name
flat_accessor_name = c.name
if len(parents) > 0:
    accessor_name = '::'.join([x.name for x in parents]) + '::'+accessor_name
    flat_accessor_name = '_'.join([x.name for x in parents]) + '_'+accessor_name
%>
template<typename Op>
void visit(Op &op);
static void hdf_construct_type();
</%def>
% for c in classes:
%if not is_enum_class(c):
<% gen_visitors([], c) %>\
%endif
% endfor
