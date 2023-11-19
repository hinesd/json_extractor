import json


def object_processor(next_index, is_escaped, source):
    index = next_index
    json_str = ''
    source_len = len(source)
    while index != source_len:
        char = source[index]
        if char == '"': # process the inside of the string
            new_index, append_str = handle_in_str(index, is_escaped, source)
            if append_str:
                index = new_index
                json_str += append_str
                continue
            else:
                return new_index, ''
        else:
            if char == '}':  # found matching bracket, return complete json_str
                json_str += char
                return index, json_str
            if char == '{':  # found new child object, step inside and find its matching pair.
                new_index, child_object = object_processor(index + 1, is_escaped, source)
                if child_object:
                    json_str += char + child_object
                if not child_object:
                    return new_index, child_object
                index = new_index
                index += 1
                continue
        # not in string and not control characters that needs validation, but still valid json character
        valid_char = validate_char(char, index, source)
        if valid_char:
            json_str += valid_char
            index += len(valid_char)
        else:
            # invalid json
            return index, False


def validate_char(char, index, source):
    if char in [':', '[', ']', '\\', ','] or char.isnumeric() or char.isspace():
       return char
    if char in ['-','.'] and source[index+1].isnumeric():
       return char
    if char in ['t', 'f', 'n']:
       if source[index:index+4] in ['true', 'null']:
           return source[index:index+4]
       if source[index:index+5] == 'false':
           return source[index:index+5]
    return False


def handle_in_str(index, is_escaped, source):

    ret_str = ''
    in_str = False
    while index != len(source):
        char = source[index]
        if char == '"':
            slash_count = 0
            temp_index = index - 1
            while source[temp_index] == '\\':
                slash_count += 1
                temp_index -= 1
            mod = 2 + is_escaped
            slash_remainder = slash_count % mod
            if is_escaped and not slash_remainder and in_str and slash_count != 1 or not is_escaped and in_str and slash_remainder:
                # this " is not a control character, its inside of a string
                ret_str += char
                index += 1
                continue
            else:
                is_valid = True
                # is control character, validate and add to json_str and flip in_str
                next_valid_char = index + 1
                while source[next_valid_char].isspace():
                    next_valid_char += 1
                next_valid_char = source[next_valid_char]
                if in_str and index + 1 != len(source) and not any(next_valid_char == x for x in [',', ":", "}", "]"]):
                    is_valid = False
                if not is_valid:
                    # found valid json, but it seems to be malformed, skip the whole block
                    return index - (3 + is_escaped), ''
                # End of string, exit
                if not in_str:
                    in_str = not in_str
                else:
                    return index + 1, ret_str + char
        # inside string, default add
        ret_str += char
        index += 1


def json_check(index, source):
    # check if the next character is a double quote indicating that we are probably looking at json
    while index < len(source):
        char = source[index]
        if not char.isspace():
            if char == '\\' and source[index + 1] == '"':
                return True, True  # is json and is escaped
            elif char == '"':
                return True, False  # is json but is not escaped
            else:
                return False, False
        index += 1
    return False


# Extract all valid json from provided string
def json_extractor(source):
    index = 0
    json_found = []
    while index + 1 <= len(source):
        char = source[index]
        if char == '{':
            process_source, is_escaped = json_check(index + 1, source)
            if not process_source:
                index += 1
                continue
            new_index, json_object = object_processor(index + 1, is_escaped, source)
            if json_object:
                if is_escaped:
                    json_object = json_object.encode().decode('unicode-escape')
                try:
                    json_found.append(json.loads('{'+json_object))
                except:
                    pass

            index = new_index
        index += 1
    if json_found:
        return {"content":json_found}
    else:
        return {"content":"Failed Extraction"}
