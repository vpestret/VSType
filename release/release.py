
import sys, re, os.path
from xml.etree import ElementTree as ET
import py_compile # for build
import shutil # for files copy
import datetime # for date stamp on release dir

release_notes_in_name = 'release_notes.xml' 
release_notes_out_name = 'release_notes.txt' 
release_list_name = 'release.list' 
releases_directory = 'releases' 

# -------------- script routines

def dump_to_file(out_file, rn_root):
    for note in rn_root:
        out_file.write('Release for version %s:\n' % note.attrib['version'])
        out_file.write('%s\n' % note.text)

def check_version_gt(ver1, ver2):
    match = re.search(r'^(\d+)\.(\d+)\.(\d+)$', ver1)
    if match:
        aver1 = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    else:
        raise ValueError()
    match = re.search(r'^(\d+)\.(\d+)\.(\d+)$', ver2)
    if match:
        aver2 = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    else:
        raise ValueError()
    # compare 
    assert(len(aver1) == len(aver2))
    for idx in range(len(aver1)):
        if (aver1[idx] > aver2[idx]):
            return True
    return False

# -------------- sainty check of input arguments

if len(sys.argv) < 2:
    print 'Error: first mandatory argument must contain version number' +\
          ' to increase'
    print 'Error: second optional argument must contain relative path' +\
          ' to the releases directory'
    sys.exit(1)

match = re.search(r'^\d+\.\d+\.\d+$', sys.argv[1])
if match:
    version_to_inc = sys.argv[1]
else:
    print 'Error: incorrect version number to increase'
    print '       acceptable format: X.Y.Z where X,Y and Z - decimal numbers'
    sys.exit(1)

if len(sys.argv) >= 3:
    releases_directory = sys.argv[2]

# check if releases directory available
releases_directory = os.path.abspath(releases_directory)
if not os.path.isdir(releases_directory):
    print 'Error: directory does not exist %s' % releases_directory
    sys.exit(1)

# -------------- script itself

file_root = ET.parse(release_notes_in_name)
found_unversioned_tag = False
for note in file_root.getroot():
    note_version = ''
    if 'version' in note.attrib.keys():
        note_version = note.attrib['version']
    if note_version != '':
        print 'recognized tag: ' + note.tag + ' with version ' + note_version
        # make comparison to check novelity of version_to_inc
        if not(check_version_gt(version_to_inc, note_version)):
            print 'Error: greater or equal version than requested %s was found'\
                % version_to_inc, note_version
            sys.exit(1)
    else:
        if found_unversioned_tag:
            print 'Error: multiple unversioned tags detected'
            sys.exit(1)
        found_unversioned_tag = True
        print 'recognized unversioned tag: ' + note.tag
        note.attrib['version'] = version_to_inc

if not(found_unversioned_tag):
    print 'Error: No unversioned tags detected'
    sys.exit(1)

# -------------- write to the distribution release notes 
out_file = open(release_notes_out_name, 'w')
if out_file:
    dump_to_file(out_file, file_root.getroot())
    out_file.close()
else:
    print 'Error: cannot open file %s for ouput' % release_notes_out_name
    sys.exit(1)

# -------------- compile steps
py_compile.compile('../VSType.py')

# -------------- create distribution directory
now = datetime.datetime.now()
date_stamp = '%.2d%.2d%.2d' % (now.year % 100, now.month, now.day)
distr_dir = os.path.abspath(releases_directory + '/VSType_' + \
                            date_stamp + '_' + version_to_inc)
if os.path.exists(distr_dir):
    print 'Error: directory already exists %s' % releases_directory
    sys.exit(1)
os.makedirs(distr_dir)

# -------------- copy files
list_file = open(release_list_name, 'r')
if list_file:
    for name in list_file.readlines():
        name = name.rstrip()
        to_name = os.path.basename(name) if os.path.dirname(name) == "release" else name
        # print 'to_name = %s' % to_name
        file_dir = os.path.abspath(distr_dir + '/' + os.path.dirname(to_name))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        from_name = '../' + name
        # print 'from_name = %s' % from_name
        if os.path.exists(os.path.abspath(from_name)):
            shutil.copy(os.path.abspath(from_name),\
                        os.path.abspath(distr_dir + '/' + os.path.dirname(to_name)))
        else:
            print 'Error: cannot open file %s for input' %\
                  os.path.abspath(from_name)
            print '           or open file %s for output' %\
                  os.path.abspath(distr_dir + '/' + os.path.dirname(to_name))
            sys.exit(1)
else:
    print 'Error: cannot open file %s for input' % release_list_name
    sys.exit(1)

# -------------- write back to the release notes template
out_file = open(release_notes_in_name, 'w')
if out_file:
    out_file.write(ET.tostring(file_root.getroot()) + '\n')
    out_file.close()
else:
    print 'Error: cannot open file %s for ouput' % release_notes_in_name
    sys.exit(1)

