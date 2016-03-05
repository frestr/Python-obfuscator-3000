import re
import hashlib
import random

class Obfuscator:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.nonlocal_funcs = {}
        self.strings = {}
        self.imports = {}

        self.generated_names = []

    def obfuscate_file(self, in_file, out_file):
        if not self.does_file_exist(in_file):
            print('Cannot find specified file')
            return;

        self.analyze_file(in_file)
        self.write_obfuscated_file(in_file, out_file)

    def analyze_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.change_strings(lines)
            self.reassign_imports(lines)
            self.change_func_names(lines)
            self.reassign_nonlocal_funcs(lines)
            self.change_var_names(lines)

    def write_obfuscated_file(self, in_file, out_file):
        has_reassigned = False
        with open(in_file, 'r') as i_f, open(out_file, 'w') as o_f:
            for line in i_f.readlines():
                # Do not write comments or blank lines
                if ((re.match('[ ]*#', line) is not None 
                        and re.match('[ ]*#!', line) is None) or
                        re.match('[ ]*\n', line) is not None):
                    continue

                # Change strings
                for old, new in self.strings.items():
                    line = self.replace_name(line, old, new)

                # Change imports
                for old, new in self.imports.items():
                    if 'import' in line and old in line:
                        line = line[:-1] + ' as ' + new + '\n'
                    else:
                        line = self.replace_name(line, old, new)

                # Reassign functions
                if (not has_reassigned and 
                        'import' not in line and 
                        '#' not in line and
                        re.match('[ ]*\n', line) is None):
                    for old, new in self.nonlocal_funcs.items():
                        o_f.write(new + '=' + old + '\n')
                    has_reassigned = True
                
                # Change function names
                if 'import' not in line:
                    for old, new in self.functions.items():
                        line = self.replace_name(line, old, new)
                    for old, new in self.nonlocal_funcs.items():
                        line = self.replace_name(line, old, new)

                # Change variable names
                for old, new in self.variables.items():
                    line = self.replace_name(line, old, new)

                o_f.write(line)

    def replace_name(self, line, old, new):
        new_line = ''
        prev_index = 0
        for i in range(len(line)):
            try:
                if (line[i:i+len(old)] == old and
                        (i == 0 or not line[i-1].isalnum()) and
                        (i + len(old) >= len(line) or not line[i+len(old)].isalnum())):
                    new_line += line[prev_index:i] + new
                    prev_index = i + len(old)
            except IndexError:
                break
        new_line += line[prev_index:]
        return new_line
        

    def change_func_names(self, file_cont):
        for line in file_cont:
            res = re.search('^[ ]*def ([a-zA-Z_][a-zA-Z0-9_]*)\(.*\):', line)
            if res is not None:
                self.functions[res.group(1)] = self.get_random_name()

    def reassign_nonlocal_funcs(self, file_cont):
        for line in file_cont:
            res = re.search('([a-zA-Z_][a-zA-Z0-9_]*)\(.*\)', line)
            if (res is not None and 
                    res.group(1) not in self.functions and
                    res.group(1) not in self.imports and
                    line[line.index(res.group(1)) - 1] != '.'):
                self.nonlocal_funcs[res.group(1)] = self.get_random_name()

    def change_strings(self, file_cont):
        chr_replacement = self.get_random_name()
        self.nonlocal_funcs['chr'] = chr_replacement
        for line in file_cont:
            res = re.findall('\'.+?\'', line)
            if res != []:
                for string in set(res):
                    new_str = ''
                    i = 1
                    while i < len(string) - 1:
                        if string[i] == '\\':
                            new_str += '\'' + string[i:i+2] + '\'+'
                            i += 2
                        else:
                            new_str += chr_replacement + '(' + str(ord(string[i])) + ')+'
                            i += 1
                    new_str = new_str[:-1] # Remove the last +
                    self.strings[string] = new_str

    def reassign_imports(self, file_cont):
        for line in file_cont:
            if 'import' in line and ',' not in line:
                words = line.split()
                self.imports[words[-1]] = self.get_random_name()

    def change_var_names(self, file_cont):
        for line in file_cont:
            res = re.search('^[ ]*([a-zA-Z_][a-zA-Z0-9_]*)[ ]*=', line)
            if res is not None:
                self.variables[res.group(1)] = self.get_random_name()
            res = re.search(
                    '^[ ]*def [a-zA-Z_][a-zA-Z0-9_]*\(([a-zA-Z0-9_, ]+)(=.*)?\):', line)
            if res is not None:
                params = res.group(1).split(',')
                for param in params:
                    self.variables[param.strip()] = self.get_random_name()

    def get_random_name(self):
        rand_str = list(u'abcdefghijklmnopqrstuvwxyz')
        random.shuffle(rand_str)
        name = 'a' + hashlib.sha512(bytes(str(rand_str), 'utf-8')).hexdigest()

        if name in self.generated_names:
            return get_random_name()
        else:
            self.generated_names.append(name)
            return name

    def does_file_exist(self, filename):
        try:
            open(filename, 'r')
        except FileNotFoundError:
            return False
        return True
