% for c in classes:
template<typename Op>
void ${c.name}::visit_fields(Op &op){
    % for f in c.fields:
    op("${f.name}", ${f.name});
    % endfor
}
% if i != len(classes) - 1:

% endif
% endfor
