<%
    def is_enum_class(x):
        return '::detail::enum_tag' in x.bases
    def has_size_enum(x):
        for e in x.enums:
            if 'SIZE' in [x[0] for x in e.valuepairs]:
                return True
        return False
%>\
<%def name="gen_code(parents, c)">\
<%
for child in c.classes:
    if not is_enum_class(child):
        gen_code(parents + [c], child)
accessor_name = c.name
flat_accessor_name = c.name
if len(parents) > 0:
    accessor_name = '::'.join([x.name for x in parents]) + '::'+accessor_name
    flat_accessor_name = '_'.join([x.name for x in parents]) + '_'+accessor_name
%>\
%if yaml and ('class AppConfigBase' in c.bases or 'class IYAMLable' in c.bases or 'yamlable_object_tag' in c.bases):
void ${accessor_name}::apply(const YAML::Node &node){
    % for f in c.fields:
    yaml_opt_load(${f.name});
    % endfor
}
void ${accessor_name}::encode(YAML::Emitter &emitter) const{
    % for f in c.fields:
    yaml_save(${f.name});
    % endfor
}
%endif
%if hdf:
void ${accessor_name}::hdf_construct_type(H5::CompType &type){
    % for f in c.fields:
    hdf_add_field(${f.name});
    % endfor
}
%endif
% if size_check and has_size_enum(c):
static_assert(sizeof_unroller<
% for i,f in enumerate(c.fields):
    decltype(std::declval<${accessor_name}>().${f.name})${',' if i != len(c.fields)-1 else ''}
% endfor
    >::value == ${c.name}::SIZE, "packed ${accessor_name} size check failed");
% endif
</%def>\
<%
nonenum_classes = [x for x in classes if not is_enum_class(x)]
if len(nonenum_classes) == 0:
    return
%>\
% for c in nonenum_classes:
<% gen_code([], c) %>\
% endfor
