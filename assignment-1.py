# This is a comment line! It is started with a "#"!

# change the following line to open different file
file_path='Log-A.strace'
# file_path='Log-B.strace'

print("Now I am going to open file: " + file_path)
file1 = open(file_path)
lines = file1.readlines()
lines = [line.strip() for line in lines]
print("Now that the data is got, this file is now to be closed!")
file1.close()

# e.g., 
# 16999 read(3</etc/nsswitch.conf>, "", 4096) = 0

def parse_line(line):
    
    # timestamp = line.split()[0]

    # file name is quoted with <>
    file_name_start = line.find('<')
    file_name_end = line.find('>')
    file_name = line[file_name_start + 1 : file_name_end]

    # return (timestamp, file_name)
    return file_name

# e.g.
# file_occurance = {/etc/nsswitch.conf': ['16997', '16999', '16999']}
# the key of the dictionary is the file name
# the value of the dictionary is a list of timestamp

def stat_file_occurance(file_occurance, timestamp, file_name):

    # if the file_name is already in the dictionary, append the timestamp
    if file_name in file_occurance:
        file_occurance[file_name].append(timestamp)
        
    # if the file_name is not yet there, create the list
    else:
        file_occurance[file_name] = [timestamp]

# print the file occurance information
def print_file_occurance(file_occurance):

    # print table head
    table_head = '%-50s\t%s\t%s' % ('file', 'count', 'timestamp (line no.)')
    # table_head = '%s\t%s\t%s' % ('file', 'count', 'timestamp (line no.)')
    print(table_head)

    for file in file_occurance:

        # small technique to make each file occupy 50 columns and left justified
        output = '%-50s' % file + '\t' 
        # output = '%s' % file + '\t' 

        # the number of occurance
        output += str(len(file_occurance[file])) + '\t'

        # each timestamps
        for timestamp in file_occurance[file]:
            output += str(timestamp) + '\t'

        print(output)

def print_file_occurance_simple(file_occurance):

    for idx, file in enumerate(file_occurance):
        print('line %d' % (idx + 1))
        print('file_name: %s' % file)
        print('count: %d' % len(file_occurance[file]))
        for t in file_occurance[file]:
            print(t)

        print('\n')
        


count = 0

# put the include and exclude terms in lists
term_include = [' read(']
term_exclude = ['tty', 'pipe']

# use a dictionary to keep all file occurance information
file_occurance = {}

for idx, line in enumerate(lines):

    try:
        for term in term_include:
            # if the include term is not in the line, raise an exception
            if not term in line:
                raise StopIteration

        for term in term_exclude:
            # if the exclude term is in the line, raise an exception
            if term in line:
                raise StopIteration

        file_name = parse_line(line)
        stat_file_occurance(file_occurance, idx, file_name)
        count += 1
    
    # proceed to the next line
    except StopIteration:
        continue

print('total: %d' % count)
print_file_occurance(file_occurance)
# print_file_occurance_simple(file_occurance)

# Now I am going to open file: Log-A.straceNow that the data is got, this file is now to be closed!total: 26file                                                    count   timestamp
# /lib/x86_64-linux-gnu/libpthread-2.23.so                1       518
# /etc/locale.alias                                       2       561     562
# /lib/x86_64-linux-gnu/libnss_files-2.23.so              2       327     622
# /lib/x86_64-linux-gnu/libpcre.so.3.13.2                 1       501
# /lib/x86_64-linux-gnu/libnss_compat-2.23.so             2       295     590
# /proc/filesystems                                       2       548     549
# /lib/x86_64-linux-gnu/libdl-2.23.so                     1       509
# /lib/x86_64-linux-gnu/libc-2.23.so                      4       88      256     492     892
# /lib/x86_64-linux-gnu/libnss_nis-2.23.so                2       319     614
# /lib/x86_64-linux-gnu/libselinux.so.1                   1       482
# /etc/nsswitch.conf                                      4       286     287     581     582
# /lib/x86_64-linux-gnu/libnsl-2.23.so                    2       303     598
# /proc/sys/kernel/ngroups_max                            2       655     658