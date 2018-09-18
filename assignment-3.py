#encoding: utf-8
import sys

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

def extract_program_name(line, start_delimiter, end_delimiter):

    name_start = line.find(start_delimiter)
    name_end = line.find(end_delimiter, name_start + 1)
    name = line[name_start + 1 : name_end]
    return name

def output_a(lines):
    line_num = 1

    stat_pid = None
    stat_line_num = None
    stat_line = None
    
    for line in lines:
        if 'stat(' in line:
            
            stat_line_num = line_num
            stat_pid = pid_from_line(line)
            stat_line = line

        elif 'clone(' in line:
            clone_line_num = line_num
            clone_pid = pid_from_line(line)
            clone_line = line

            if clone_pid == stat_pid:
                print(str(stat_line_num) + '\t' + stat_line)
                print(str(clone_line_num) + '\t' + clone_line)
                
                stat_pid = None
                stat_line_num = None
                stat_line = None

        line_num += 1

def pid_from_line(line):
    # return line.split()[0]
    idx = line.find(' ')
    pid = line[0 : idx]
    return pid

def output_c(lines):

    line_num = 1

    # correspond to open, getdents, close
    kw_found = [False, False, False]
    pids = [None, None, None]
    line_nums = [None, None, None]
    line_strs = [None, None, None]

    for line in lines:
        if 'open(' in line:
            kw_found[0] = True
            pids[0] = pid_from_line(line)
            line_nums[0] = line_num
            line_strs[0] = line
        
        elif 'getdents(' in line:
            if kw_found[0]:
                pid = pid_from_line(line)
                if pid == pids[0]:
                    kw_found[1] = True
                    pids[1] = pid
                    line_nums[1] = line_num
                    line_strs[1] = line
        
        elif 'close(' in line:
            if kw_found[0] and kw_found[1]:
                pid = pid_from_line(line)
                if pid == pids[0] and pid == pids[1]:
                    kw_found[2] = True
                    pids[2] = pid
                    line_nums[2] = line_num
                    line_strs[2] = line

        if kw_found[0] and kw_found[1] and kw_found[2]:
            
            for i in [0, 1, 2]:
                print(str(line_nums[i]) + '\t' + line_strs[i])

            kw_found = [False, False, False]
            pids = [None, None, None]
            line_nums = [None, None, None]
            line_strs = [None, None, None]

        line_num += 1

def main():
    log_a_name = 'Log-A.strace'
    lines_a = read_file(log_a_name)

    log_b_name = 'Log-B.strace' 
    lines_b = read_file(log_b_name)

    print('output a')
    output_a(lines_a)

    print('output b')
    output_a(lines_b)

    print('output c')
    output_c(lines_a)
    output_c(lines_b)


if __name__ == '__main__':
    main()


# output a
# 126     16931 stat("/var/mail/user", 0x7fffffffda90) = -1 ENOENT (No such file or directory)
# 180     16931 clone( <unfinished ...>
# 808     16931 stat("/bin/uname", {st_mode=S_IFREG|0755, st_size=31440, ...}) = 0
# 816     16931 clone( <unfinished ...>
# output b
# 36      16931 stat("./count_keystrokes.c", {st_mode=S_IFREG|0775, st_size=280, ...}) = 0
# 62      16931 clone( <unfinished ...>
# 317     16955 stat("/bin/cat", {st_mode=S_IFREG|0755, st_size=52080, ...}) = 0
# 324     16955 clone( <unfinished ...>
# 500     16956 stat("/bin/ls", {st_mode=S_IFREG|0755, st_size=126584, ...}) = 0
# 501     16956 clone( <unfinished ...>
# 611     16956 stat("/bin/rm", {st_mode=S_IFREG|0755, st_size=60272, ...}) = 0612     16956 clone( <unfinished ...>output c4       16931 open("/home/user/test/", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 3</home/user/test>42      16931 getdents(3</home/user/test>, /* 0 entries */, 32768) = 0
# 44      16931 close(3</home/user/test>)         = 0
# 583     16959 open(".", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 3</home/user/test>
# 586     16959 getdents(3</home/user/test>, /* 0 entries */, 32768) = 0
# 587     16959 close(3</home/user/test>)         = 0
# 745     16961 open(".", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 3</home/user/test>
# 748     16961 getdents(3</home/user/test>, /* 0 entries */, 32768) = 0
# 749     16961 close(3</home/user/test>)         = 0
# 899     16963 open(".", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 3</home/user/test>
# 902     16963 getdents(3</home/user/test>, /* 0 entries */, 32768) = 0
# 903     16963 close(3</home/user/test>)         = 0