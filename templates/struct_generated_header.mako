<%
def is_enum_class(x):
    return '::detail::enum_tag' in x.bases
%>\
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
%>\
template<typename Op>
void ${accessor_name}::visit_fields(Op &op){
    % for f in c.fields:
    op("${f.name}", ${f.name});
    % endfor
}
</%def>\
<%def name="gen_assignable(parents, c)">
<%
for child in c.classes:
    if not is_enum_class(child):
        gen_assignable(parents + [c], child)
accessor_name = c.name
flat_accessor_name = c.name
if len(parents) > 0:
    accessor_name = '::'.join([x.name for x in parents]) + '::'+accessor_name
    flat_accessor_name = '_'.join([x.name for x in parents]) + '_'+accessor_name
%>\
template<typename RHST>
void ${accessor_name}::assign_from(const RHST &rhs){
    % for f in c.fields:
%if concept_assignable_accessors:
    assign(this->${f.name}, rhs.${f.name}());
%else:
    assign(this->${f.name}, rhs.${f.name});
%endif
    % endfor
}
template<typename RHST>
void ${accessor_name}::assign_to(RHST &rhs) const{
    % for f in c.fields:
%if concept_assignable_accessors:
    rhs.${f.name}(this->${f.name});
%else:
    assign(rhs.${f.name}, this->${f.name});
%endif
    % endfor
}
</%def>\
% for namespace, classes in namespaced_classes.iteritems():
<%
nonenum_classes = [x for x in classes if not is_enum_class(x)]
if len(nonenum_classes) == 0:
    continue
%>\
<% nsprint = None if len(namespace) == 0 else ''.join(['namespace '+x+'{ ' for x in namespace])[:-1] %>\
% if nsprint is not None:
${nsprint}
%endif
% for c in nonenum_classes:
%if visitors:
<% gen_visitors([], c) %>\
%endif
%if concept_assignable:
<% gen_assignable([], c) %>\
%endif
%endfor
% if nsprint is not None:
${''.join(['}' for x in namespace])}
%endif
% endfor
