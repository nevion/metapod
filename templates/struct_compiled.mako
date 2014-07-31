<%
    def has_size_enum(x):
        for e in x.enums:
            if 'SIZE' in [x[0] for x in e.valuepairs]:
                return True
        return False
%>
% for i,c in enumerate(classes):
void ${c.name}::hdf_construct(H5::CompType &type){
    % for f in c.fields:
    hdf_add_field(${f.name});
    % endfor
}
% if size_check and has_size_enum(c):
static_assert(sizeof_unroller<
% for i,f in enumerate(c.fields):
    decltype(std::declval<${c.name}>().${f.name})${',' if i != len(c.fields)-1 else ''}
% endfor
    >::value == ${c.name}::SIZE, "packed ${f.name} size check failed");
% endif

% endfor
