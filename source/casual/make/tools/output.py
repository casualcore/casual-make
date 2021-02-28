import sys
import casual.make.tools.color as color_module
import casual.make.entity.state as state
import re

# globals
if state.settings.no_colors:
    color_module.color.active(False)


def reformat(line):
    """ reformat output from make and add som colours"""

    for regex in reformat.ingore_filters:
        match = regex.match(line)
        if match:
            return ''

    for regex, filter in reformat.filters:
        match = regex.match(line)

        if match:
            return filter(match)

    return line


reformat.ingore_filters = [
    re.compile(r'(^make.*)Nothing to be done for'),
]

reformat.filters = [
    [re.compile(r'(^(g|c|clang)\+\+).* -o (\S+\.o) (\S+\.cc|\S+\.cpp|\S+\.c).*'),
     lambda match: color_module.color.green('compile: ') + color_module.color.white(match.group(4)) + '\n'],
    [re.compile(r'(^(g|c|clang)\+\+).* -E .*?(\S+\.cc|\S+\.cpp|\S+\.c).*'),
     lambda match: color_module.color.green('dependency: ') + color_module.color.white(match.group(3)) + '\n'],
    [re.compile(r'(^ar) \S+ (\S+\.a).*'),
     lambda match: color_module.color.blue('archive: ') + color_module.color.white(match.group(2)) + '\n'],
    [re.compile(r'(^(g|c|clang)\+\+).* -o (\S+).*(?:(\S+\.o) ).*'),
     lambda match: color_module.color.blue('link: ') + color_module.color.white(match.group(3)) + '\n'],
    [re.compile(r'^(.*[.]cmk )(.*)'),
     lambda match: color_module.color.cyan('makefile: ') + color_module.color.blue(match.group(2)) + ' ' + match.group(1) + '\n'],
    [re.compile(r'(^make.*:)(.*)'),
     lambda match: color_module.color.header(match.group(1)) + match.group(2) + '\n'],
    [re.compile(r'^rm -f (.*)'),
     lambda match: color_module.color.header('delete: ') + match.group(1) + '\n'],
    [re.compile(r'^mkdir( [-].+)*[ ](.*)'),
     lambda match: color_module.color.header('create: ') + match.group(2) + '\n'],
    [re.compile(r'.*casual-build-server[\S\s]+-c (\S+)[\s]+-o (\S+) .*'),
     lambda match: color_module.color.blue('buildserver: ') + color_module.color.white(match.group(2)) + '\n'],
    [re.compile(r'^copy +(\S+) (.*)'),
     lambda match: color_module.color.blue('prepare install: ') + color_module.color.white(match.group(1)) + ' --> ' + color_module.color.white(match.group(2)) + '\n'],
    [re.compile(r'^(>[a-zA-Z+.]+)[\s]+(.*)'),
     lambda match: color_module.color.green('updated: ') + match.group(2) + ' ' + color_module.color.blue(match.group(1)) + '\n'],
    [re.compile(r'^(.*/bin/test-.*)'),
     lambda match: color_module.color.cyan('unittest: ') + color_module.color.white(match.group(1)) + '\n'],
    [re.compile(r'^casual-build-resource-proxy.*--output[ ]+([^ ]+)'),
     lambda match: color_module.color.blue('build-rm-proxy: ') + color_module.color.white(match.group(1)) + '\n'],
    [re.compile(r'^ln -s (.*?) (.*)'),
     lambda match: color_module.color.blue('symlink: ') + color_module.color.white(match.group(2)) + ' --> ' + color_module.color.white(match.group(1)) + '\n'],
    [re.compile(r'^[^ ]*clang-tidy (.*?) (.*)'),
     lambda match: color_module.color.green('lint: ') + color_module.color.white(match.group(1)) + '\n'],
    [re.compile(r'^[^ ]*building model: '),
     lambda match: color_module.color.green('building model: ')],
    [re.compile(r'^[^ ]*processed command: (.*?)(-o .*?)( .*)'),
     lambda match: color_module.color.red('processed command: ', bright=True) + match.group(1) + color_module.color.blue(match.group(2)) + match.group(3)],
    [re.compile(r'^[^ ]*processed (.*?): (.*)'),
     lambda match: color_module.color.red('processed ' + match.group(1) + ': ', bright=True) + match.group(2)],
    [re.compile(r'^[^ ]*progress: (.*)'),
     lambda match: color_module.color.cyan('progress: ' + match.group(1))],
]


def print(message, end='\n', file=sys.stdout, flush=True, format=True):
    import builtins
    message = reformat(message) if format else message
    builtins.print(message, file=file, end=end, flush=flush)


def error(message, header=False):
    if header:
        print(color_module.color.red('error:', bright=True), file=sys.stderr)
    print(message, file=sys.stderr)
