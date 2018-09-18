#encoding: utf-8
import sys
import collections
import itertools

def read_file(file_name):

    lines = None
    try:
        with open(file_name) as f:
            lines = f.read().splitlines()
    except:
        print('file "%s" does not exitst, please check...' % file_name)
        sys.exit(0)
    
    return lines

def search_keyword(lines, kw_include, kw_exclude = [],\
             include_only_need_one = False, include_idx = False):

    count = 0
    found_lines = []

    if type(kw_include) is str: kw_include = [kw_include]
    if type(kw_exclude) is str: kw_exclude = [kw_exclude]   
        
    for idx, line in enumerate(lines):
        try:
            include_found = False
            for kw in kw_include:
                if not kw in line:
                    if not include_only_need_one:
                        raise StopIteration
                else:
                    include_found = True
            if include_only_need_one and not include_found:
                raise StopIteration
            
            for kw in kw_exclude:
                if kw in line:
                    raise StopIteration

        except StopIteration:
            continue

        count += 1
        if not include_idx:
            found_lines.append(line)
        else:
            found_lines.append((line, idx))

    return (count, found_lines)

def print_lines(lines):
    for line in lines:
        print(line)

def search_both_log(lines_a, lines_b, kw_include, kw_exclude = [], \
                    include_only_need_one = False):

    count_a, _ = search_keyword(lines_a, kw_include, kw_exclude, include_only_need_one)
    count_b, _ = search_keyword(lines_b, kw_include, kw_exclude, include_only_need_one)
    return (count_a, count_b)

def extract_str(line, start_delimiter, end_delimiter):

    name_start = line.find(start_delimiter)
    name_end = line.find(end_delimiter, name_start + 1)
    name = line[name_start + 1 : name_end]
    return name

def count_events(lines):

    event_list = ['execve', 'open', 'connect', 'write', 'sendto', 'read', 'access', \
    'stat', 'lstat', 'unlinkat', 'exit_group', 'fchmodat']

    event_count = collections.defaultdict(int)
    for line in lines:
        event_name = extract_str(line, ' ', '(').strip()
        if event_name in event_list:
            event_count[event_name] += 1

    event_group_list = ['execve', 'open', 'connect', 'write', 'sendto', 'read', \
    ('access', 'stat', 'lstat'), 'unlinkat', 'exit_group', 'fchmodat']

    event_group_count = collections.defaultdict(int)

    for event_group in event_group_list:
        if type(event_group) is str:
            event_group_count[event_group] = event_count[event_group]
        else:
            for elem in event_group:
                event_group_count[event_group] += event_count[elem]

    return event_group_count

def print_event_count(event_count):
    
    for event in event_count:

        if type(event) is str:
            event_name = event
        else:
            event_name = '/'.join(event)

        print(event_name + '\t' + str(event_count[event]))

def c1(logs):
    print('c1:')

    for log in logs:
        print(log)
        lines = read_file(log)
        event_count = count_events(lines)
        print_event_count(event_count)
        print('\n')

def c2(logs):

    print('c2:')

    file_info = collections.defaultdict(list)

    for idx, log in enumerate(logs):

        lines = read_file(log)
        
        for line_num, line in enumerate(lines):
            if 'open(' in line:
                file_name = extract_str(line, '"', '"')

                l = len(file_info[file_name])
                if l == idx + 1:
                    # because we only need the first occurance
                    continue
                
                # the current file does not show up in some of the previos logs
                if l < idx:
                    file_info[file_name].extend( [None] * (idx - l) )

                file_info[file_name].append(line_num + 1)

    # padding at the end. make the list of equal length
    l = len(logs)
    for file_name in file_info:
        file_info[file_name].extend( [None] * (l - len(file_info[file_name])) )

    for file_name in file_info:
        
        print(file_name, file_info[file_name])

    print('\n')

def c3(logs):
    print('c3:')

    for log in logs:
        print(log)
        lines = read_file(log)
        find_triple(lines)
        print('\n')

def c4(logs):
    print('c4:')
    
    all_lines = [read_file(log) for log in logs]
    log_info = zip(logs, all_lines)
    
    logs_iter = itertools.combinations(log_info, 2)
    for logs_pair in logs_iter:
        lines_pair = [logs_pair[0][1], logs_pair[1][1]]

        read_lines_1, read_lines_2 = get_event_lines(lines_pair, 'read(', ['<', '>'],\
                                     exclude_kw = ['tty', 'pipe', 'socket', 'inode'])
        read_score = similar_score(read_lines_1, read_lines_2)
        print(logs_pair[0][0], logs_pair[1][0], 'read', read_score)

        write_lines_1, write_lines_2 = get_event_lines(lines_pair, 'write(', ['<', '>'],\
                                     exclude_kw = ['tty', 'pipe', 'socket', 'inode'])
        write_score = similar_score(write_lines_1, write_lines_2)
        print(logs_pair[0][0], logs_pair[1][0], 'write', write_score)

        execve_lines_1, execve_lines_2 = get_event_lines(lines_pair, 'execve(', ['"', '"'])
        execve_score = similar_score(execve_lines_1, execve_lines_2)
        print(logs_pair[0][0], logs_pair[1][0], 'execve', execve_score)
    
    print('\n')

def c5(log):

    print('c5:')
    lines = read_file(log)
    print('\n')


def get_event_lines(lines, include_kw, delimiters, exclude_kw = []):

    _, event_lines_1 = search_keyword(lines[0], include_kw, exclude_kw)
    _, event_lines_2 = search_keyword(lines[1], include_kw, exclude_kw)
    lines_1 = count_behavior(event_lines_1, delimiters)
    lines_2 = count_behavior(event_lines_2, delimiters)
    return lines_1, lines_2

def count_behavior(lines, delimiters):
    
    targets = set()
    for line in lines:
        target = extract_str(line, delimiters[0], delimiters[1])
        if target != '':
            targets.add(target)
    # print(targets)
    return targets

def similar_score(set1, set2):

    files_common = set1.intersection(set2)
    # print(files_common)
    n3 = len(files_common)

    n1 = len(set1)
    n2 = len(set2)

    read_score = float(n3) / max(n1, n2) 
    return read_score

def find_triple(lines):

    line_num = 1

    # correspond to /usr/bin/wget, lstat, /bin/chmod
    kw_found = [False, False, False]
    line_nums = [None, None, None]
    line_strs = [None, None, None]

    for line in lines:
        if 'execve(' in line and '/usr/bin/wget' in line and 'remote_shell.elf' in line:
            kw_found[0] = True
            line_nums[0] = line_num
            line_strs[0] = line
        
        elif 'lstat(' in line:
            if kw_found[0]:
                kw_found[1] = True
                line_nums[1] = line_num
                line_strs[1] = line
        
        elif 'execve(' in line and '/bin/chmod' in line and 'remote_shell.elf' in line:
            if kw_found[0] and kw_found[1]:
                kw_found[2] = True
                line_nums[2] = line_num
                line_strs[2] = line

        if kw_found[0] and kw_found[1] and kw_found[2]:
            
            for i in [0, 1, 2]:
                print(str(line_nums[i]) + '\t' + line_strs[i])

            kw_found = [False, False, False]
            line_nums = [None, None, None]
            line_strs = [None, None, None]

        line_num += 1
    

def main():
    logs = ['LogA.strace', 'LogB.strace', 'LogC.strace']
    c1(logs)
    c2(logs)
    c3(logs)
    c4(logs)
    c5('LogB.strace')
    

if __name__  == '__main__':
    main()