% for namespace, classes in namespaced_classes.iteritems():
<%
nonenum_classes = [x for x in classes if '::detail::enum_tag' not in x.bases]
if len(nonenum_classes) == 0:
    continue
%>
${''.join(['namespace '+x+'{ ' for x in namespace])[:-1]}
% for c in nonenum_classes:
template<typename Op>
void ${c.name}::visit_fields(Op &op){
    % for f in c.fields:
    op("${f.name}", ${f.name});
    % endfor
}
% if i != len(classes) - 1:

% endif
% endfor
${''.join(['}' for x in namespace])}
% endfor
