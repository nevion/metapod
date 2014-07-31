% for i,c in enumerate(classes):
static void ${c.name}::hdf_construct(){
    % for f in c.fields:
    hdf_add_field("${f.name}", ${f.name});
    % endfor
}
% if size_check:
static_assert(sizeof_unroller<
% for i,f in enumerate(c.fields):
    decltype(declval<${c.name}>().${f.name})${',' if i == len(c.fields)-1 else ''}
% endfor
    >::value == ${f.name}::SIZE, "packed ${f.name} size check failed")
% endif
% if i != len(classes) - 1:

% endif
% endfor
