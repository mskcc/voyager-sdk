class SchemaProcessor(object):

    CWLTypes = [
        "Any",
        "null",
        "boolean",
        "int",
        "long",
        "float",
        "double",
        "string",
        "File",
        "Directory",
        "array",
        "record",
    ]

    @staticmethod
    def resolve_cwl_type(input_type, required=True):
        if isinstance(input_type, dict):
            port_type = input_type.get("type")
            if port_type == "record":
                t = {"type": "record", "fields": {}}
                for item in input_type.get("fields"):
                    for key in item:
                        value = item[key]
                        t["fields"][key] = SchemaProcessor.resolve_cwl_type(value)
                return t if required else ["null", t]
            elif port_type == "array":
                resolved_items = (
                    [SchemaProcessor.resolve_cwl_type(item) for item in input_type.get("items")]
                    if isinstance(input_type.get("items"), list)
                    else SchemaProcessor.resolve_cwl_type(input_type.get("items")).get("type")
                )
                t = {"type": "array", "items": resolved_items}
                return t if required else ["null", t]

        elif isinstance(input_type, list):
            resolved_types = []
            required = True
            if "null" in input_type:
                required = False
                input_type.remove("null")
            for pt in input_type:
                resolved_types.append(SchemaProcessor.resolve_cwl_type(pt))
            if required:
                resolved_types = ["null"].extend(resolved_types)
                return resolved_types
            else:
                return resolved_types[0] if len(resolved_types) == 1 else resolved_types

        elif isinstance(input_type, str):
            is_required = True
            simple_type = input_type
            is_array = True
            if simple_type.endswith("?"):
                simple_type = simple_type.replace("?", "")
                t = {"type": simple_type}
                is_required = False
            if simple_type.endswith("[]"):
                simple_type = input_type
                simple_type = simple_type.replace("[]", "")
                is_array = True

            if is_array:
                ttype = "array"
                items = simple_type
                if is_required:
                    ttype = ["null", "array"]
                t = {"type": ttype, "items": items}
            else:
                if is_required:
                    t = {"type": simple_type}
                else:
                    t = {"type": ["null", simple_type]}
            return t
