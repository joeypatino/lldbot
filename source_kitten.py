import subprocess
import json
import re

def is_swift_file(filename):
    return re.match(r'^.*\.swift$', filename) is not None


def matches_end(string, key):
    pattern = re.escape(key) + '$'
    return bool(re.search(pattern, string))


def extract_function(file_path, start_byte, end_byte):
    with open(file_path, 'r') as file:
        lines = file.read()
    function_code = lines[start_byte:end_byte]
    return function_code


def get_structure(file_path, fnName):
    result = subprocess.run(['/usr/local/bin/sourcekitten', 'structure', '--file', file_path], stdout=subprocess.PIPE)
    structure = json.loads(result.stdout)
    functions = []

    for d in structure['key.substructure']:
        try:
            dictionary = d['key.substructure']
        except KeyError:
            continue
        for dict in dictionary:
            if dict['key.kind'] == 'source.lang.swift.decl.function.method.instance' and matches_end(fnName, dict[
                'key.name']) == True:
                name = dict.get('key.name', '')
                start = int(dict.get('key.offset'))
                end = int(dict.get('key.offset')) + int(dict.get('key.length'))
                function_info = {"fn": name, "start": start, "end": end}
                functions.append(function_info)

    return json.dumps(functions, indent=4)
