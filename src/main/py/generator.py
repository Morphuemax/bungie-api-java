import json
import os
import glob
import shutil
import chevron


type_conversion_dict = {
    "boolean": "Boolean",
    "byte": "Byte",
    "int16": "Short",
    "int32": "Integer",
    "uint32": "Long",
    "int64": "Long",
    "double": "Double",
    "string": "String",
    "date-time": "String",
    "object": "Object",
    "": "String"
}

def recursive_search(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.iteritems():
            if k == lookup_key:
                yield v
            else:
                for child_val in item_generator(v, lookup_key):
                    yield child_val
    elif isinstance(json_input, list):
        for item in json_input:
            for item_val in item_generator(item, lookup_key):
                yield item_val


def compile_enum_data(data):
    all_enums = {}  # Create empty dict which we will fill and return
    for k, v in data:
        isEnum = False  # Assume it's not an enum until known
        if v.get('enum') is not None:  # Confirm that JSON has 'enum' key
            isEnum = True
        if isEnum:
            class_name = k.split('.')[-1]  # Keys are formated {Tag}.{Name}
            values = []
            for value in v.get('x-enum-values'):  # This will give us the value, identifier and description
                numerical_value = value.get('numericValue')
                identifier = value.get('identifier')
                # Not every enum has a description
                description = value.get('description') if value.get('description') is not None else ""
                values.append({'numericValue': numerical_value,
                               'identifier': identifier,
                               'description': description
                               })

            enum = {'class_name': class_name,
                    'values': values
                    }
            # Name:{
            #     'class_name': Name,
            #     'values': [...]
            # }
            entry = {class_name: enum}
            all_enums.update(entry)
    return all_enums


def generate_enums(data_json):
    path = '../../../generated-src/main/java/lib/enums/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the enums folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared Enums directory")
    print("Generating Enums")
    # For each enum we are making a separate file
    for key in data_json:
        template_path = "./templates/enum.mustache"
        isFile = os.path.isfile(template_path)
        with open(template_path, 'r') as f:
            # Render enum.mustache with enum data we collected
            rendered = chevron.render(f, data_json[key])
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        print(key + ".java created...")
    print("!All Enum files created!")

    "##################################################################"


def compile_model_data(data):
    all_models = {}
    for k,v in data:
        enum_imports = []
        model_imports = []
        isResponse = False
        if v.get('type') == "object":  # Confirm that JSON has 'enum' key
            isResponse = True
        if isResponse:
            class_name = k.split("/")[-1].split(".")[-1]  # Get ref name
            print(key)
            all_properties = []
            model_properties = data[key].get('properties')
            if model_properties is not None:
                for k2, v2 in model_properties:
                    model_property = v2
                    property_name = k2
                    print("\t"+property_name)
                    isArray = True if model_property.get('type') == "array" else False
                    property_type = recursive_search(model_property, 'x-enum-value')
                    if property_type is not None:
                        property_type = property_type['$ref']
                        property_type = property_type.split("/")[-1].split(".")[-1]  # Get ref name
                        enum_imports.append(property_type)
                    else:
                        property_type = recursive_search(model_property, '$ref')
                        if property_type is None:
                            property_type = recursive_search(model_property, 'format')
                            if property_type is None:
                                property_type = recursive_search(model_property, 'type')
                        else:
                            property_type = property_type.split("/")[-1].split(".")[-1]  # Get ref name
                            model_imports.append(property_type)
                    if property_type in type_conversion_dict:
                        property_type = type_conversion_dict[property_type]
                    #################################
                    #if isArray:
                    #    items = model_property['items']
                    #    if items.get('$ref') is not None:
                    #        property_type = items.get('$ref').split("/")[-1].split(".")[-1]  # Get ref name
                    #    else:
                    #        if items.get('x-enum-reference') is not None:
                    #            property_type = items.get('x-enum-reference')['$ref']
                    #            property_type = property_type.split("/")[-1].split(".")[-1]  # Get ref name
                    #        else:
                    #            if items.get('format') is not None:
                    #                property_type = items.get('format')
                    #            else:
                    #                property_type = model_property.get('type')
                    #    if property_type in type_conversion_dict:
                    #        property_type = type_conversion_dict[property_type]
                    #    if items.get('$ref') is not None:
                    #        model_imports.append(property_type)
                    #    else:
                    #        if items.get('x-enum-reference') is not None:
                    #            enum_imports.append(property_type)
                    # If property is not an array
                    #else:
                    #    if model_property.get('$ref') is not None:
                    #        property_type = model_property.get('$ref')
                    #        property_type = property_type.split("/")[-1].split(".")[-1]  # Get ref name
                    #    else:
                    #        if model_property.get('x-enum-reference') is not None:
                    #            property_type = model_property.get('x-enum-reference')['$ref']
                    #            property_type = property_type.split("/")[-1].split(".")[-1]  # Get ref name
                    #        else:
                    #            if model_property.get('format') is not None:
                    #                property_type = model_property.get('format')
                    #            else:
                    #                property_type = model_property.get('type')
                        # Check if property is a primative
                    #    if property_type in type_conversion_dict.keys():
                    #        property_type = type_conversion_dict[property_type]
                    #    if model_property.get('$ref') is not None:
                    #        model_imports.append(property_type)
                    #    else:
                    #        if model_property.get('x-enum-reference') is not None:
                    #            enum_imports.append(property_type)
                    all_properties.append({
                        'property_type': property_type,
                        'property_name': property_name,
                        'Property_Name': property_name[0].upper()+property_name[1:],
                        'isArray': isArray,
                        'isRequest': True if "Request" in class_name else False
                    })
                entry = {
                    class_name: {
                        'imports': {
                            'enums': enum_imports,
                            'models': model_imports
                        },
                        'properties': all_properties,
                        'class_name': class_name
                    }
                }
                all_models.update(entry)
    return all_models


def generate_models(data_json):
    path = '../../../generated-src/main/java/lib/models/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the enums folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared Models directory")
    print("Generating Models")
    # For each enum we are making a separate file
    for key in data_json:
        template_path = "./templates/model-class.mustache"
        isFile = os.path.isfile(template_path)
        with open(template_path, 'r') as f:
            # Render enum.mustache with enum data we collected
            rendered = chevron.render(f, data_json[key])
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        print(key + ".java created...")
    print("!All Model files created!")

    "##################################################################"


def compile_api_parameters(parameter_data):
    param_json = []  # List allows us to dynamically add parameters
    imports = []  # If any parameters require enums, we will add them here for importing later
    has_query = False
    for k, v in parameter_data:
        param_name = key['name']
        param_desc = key['description']
        type = key['schema']['type']  # The data type of the parameter: str, int, lst, ...
        isArray = True if type == "array" else False  # Some query params allow multiple values
        if not isArray:
            param_type = key.get("schema").get('format')
            param_type = param_type if param_type is not None else ""
            enum_reference = key['schema'].get('x-enum-reference')  # Get the enum reference, if any
            # Since not every param has an associated enum, we must split this into two lines
            enum_reference = enum_reference['$ref'] if enum_reference is not None else ""
            # Reference is formatted as: /{path}/{Tag}.{Name}
            enum_reference = enum_reference.split("/")[-1].split(".")[-1]  # Get ref name
        else:
            param_type = key.get("schema").get('items')
            param_type = param_type['format'] if param_type is not None else ""
            enum_reference = key['schema']['items'].get('x-enum-reference')  # Get the enum reference, if any
            # Since not every param has an associated enum, we must split this into two lines
            enum_reference = enum_reference['$ref'] if enum_reference is not None else ""
            # Reference is formatted as: /{path}/{Tag}.{Name}
            enum_reference = enum_reference.split("/")[-1].split(".")[-1]  # Get ref name
        in_type = key['in']  # Is "in" a path parameter or query parameter
        isQuery = True if in_type == "query" else False  # Used for template formatting
        array_type = key['schema']['items']['type'] if type == "array" else ""  # Data type within array
        # We want to make sure that the inputs are the correct type
        param_type = type_conversion_dict.get(param_type) if enum_reference == "" else enum_reference

        required = True if key.get('required') is True else False  # Not every param is required for endpoint

        param_json.append({'param_name': param_name,
                           'param_desc': param_desc,
                           'param_type': param_type,
                           'in_type': in_type,
                           'array_type': array_type,
                           'isArray': isArray,
                           'isQuery': isQuery,
                           'required': required
                           })
        imports.append(enum_reference)
        if isQuery:
            has_query = True
    return param_json, imports, has_query


def sortParams(params):
    i = len(params) - 1
    # Recursive sort - Required params in front
    while i > 0:
        if params[i]['required']:
            if not params[i - 1]['required']:
                temp = params[i - 1]
                params[i - 1] = params[i]
                params[i] = temp
                sortParams(params)
        i = i - 1
    return params


def compile_api_data(data):
    all_methods = {}  # Creating a dict of dicts to split files by Tag
    for path in data:
        path_data = data[path]
        method_name = path_data['summary'].split('.')[1]  # Summary/Endpoint is formatted {Tag}.{Name}
        method_desc = path_data['description']
        # The key for further inspection is dependent on whether endpoint is get or post
        # If 'get' key doesn't exist, we know it must be 'post'
        if not (path_data.get('get') is None):
            endpoint_type = 'get'
        else:
            endpoint_type = 'post'
        isPost = True if endpoint_type == 'post' else False
        endpoint_tag = path_data[endpoint_type]['tags'][0]
        # Gets endpoint params & enum imports
        param_data_unsorted, import_data, has_query = compile_api_parameters(
            data[path][endpoint_type].get('parameters'))
        # Python needs required method params to appear before non-required ones
        param_data = sortParams(param_data_unsorted)

        param_info = []
        # Appending each parameter to param_info
        for i in param_data:
            param_info_json = {}
            for j in i.keys():
                param_info_json.update({j: i[j]})
            last = True if i == param_data[-1] else False  # Used for template formatting
            param_info_json.update({'last': last})

            param_info.append(param_info_json)

        return_type = path_data[endpoint_type]['responses']['200']['$ref']
        return_type = return_type.split("/")[-1].split(".")[-1]  # Get ref name
        if type_conversion_dict.get(return_type) is not None:
            return_type = type_conversion_dict.get(return_type)

        request_type = path_data[endpoint_type].get('requestBody')
        request_type = request_type['content']['application/json']['schema'] if request_type is not None else ""

        if request_type != "":
            if request_type.get('$ref') is not None:
                request_type = request_type['$ref']
                request_type = request_type.split("/")[-1].split(".")[-1]
            else:
                request_type = request_type['items']['format']
                request_type = type_conversion_dict.get(request_type)

        method_info = {"method_name": method_name,
                       "endpoint_tag": endpoint_tag,
                       'endpoint_type': endpoint_type,
                       'isPost': isPost,
                       'path': path,
                       'method_desc': method_desc,
                       'param_info': param_info,
                       'request_type': request_type,
                       'return_type': return_type,
                       'has_query': has_query
                       }

        if endpoint_tag not in all_methods:
            entry = {
                endpoint_tag: {
                    'imports': {
                        'enums': [],
                        'models': []
                    },
                    "tag": endpoint_tag,
                    'methods': []
                }
            }
            all_methods.update(entry)
        all_methods[endpoint_tag]['methods'].append(method_info)
        # TODO: See if reference/model imports are needed
        for import_ref in import_data:
            if import_ref not in all_methods[endpoint_tag]['imports']['enums']:
                all_methods[endpoint_tag]['imports']['enums'].append(import_ref)
        if request_type != "":
            if request_type not in all_methods[endpoint_tag]['imports']['models']:
                if request_type not in type_conversion_dict.values():
                    all_methods[endpoint_tag]['imports']['models'].append(request_type)
        if return_type not in all_methods[endpoint_tag]['imports']['models']:
            if return_type not in type_conversion_dict.values():
                all_methods[endpoint_tag]['imports']['models'].append(return_type)
    return all_methods


def generate_api(data_json):
    path = '../../../generated-src/main/java/lib/api/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the api folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared API directory")
    print("Generating API")
    # For each tag we are making a separate file
    for key in data_json:
        template_path = "./templates/api-class.mustache"
        with open(template_path, 'r') as f:
            # Render api.mustache with method data we collected
            rendered = chevron.render(f, data_json[key])
        # Some endpoints don't have a tag, we will lump them together in a 'Misc' file
        if key == '':
            key = 'Misc'
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        print(key + ".java created...")
    print("!All API files created!")

    "#######################################################################"


def generate():
    # apiFile = './api-src/openapi.json'
    apiFile = '../../../api-src/openapi.json'
    with open(apiFile, 'r', encoding='utf-8') as data_file:
        rawData = json.load(data_file)
    pathData = rawData.get('paths')
    schemaData = rawData.get('components').get('schemas')

    print("Generating Sources:\n")
    compiled_enum_data = compile_enum_data(schemaData)
    compiled_model_data = compile_model_data(schemaData)
    compiled_api_data = compile_api_data(pathData)

    generate_enums(compiled_enum_data)
    print()
    generate_models(compiled_model_data)
    print()
    generate_api(compiled_api_data)


if __name__ == '__main__':
    generate()