#include "${include_file}"

% for c in classes:
    template<typename Op>
    void ${c.name}::visit(Op &op){
        % for f in c.fields:
        op("${f.name}", ${f.name});
        % endfor
    }
    static void ${c.name}::hdf_construct(){
        % for f in c.fields:
        hdf_add_field("${f.name}", ${f.name});
        % endfor
    }
    static_assert(sizeof_args<
    % for i,f in enumerate(c.fields):
        decltype(declval<${c.name}>().${f.name})${',' if i == len(c.fields)-1 else ''}
    % endfor
        >::value == ${f.name}::SIZE, "packed ${f.name} size check failed")

% endfor
