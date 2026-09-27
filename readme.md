# Documentation
## Introduction
casual-make is the build system used in casual.

We like the descriptive syntax and think it can be a market for it in the open source community.

## Technique
It uses python 3 as 'language' and internal 'engine'.

## Setup
### Alternative 1 - Setup via pip3
```
hostname$ pip install git+https://github.com/casualcore/casual-make.git@release/1.9
```

### Alternative 2 - Setup from cloned repo
```
hostname$ export PYTHONPATH=/path/to/casual-make/src:$PYTHONPATH
hostname$ export PATH=/path/to/casual-make/src:$PATH
```


## Environment variables
casual-make sets CASUAL_MAKE_SOURCE_ROOT to repository root of the current repository.

## Usage
```
usage: casual-make [-h] [-d] [--use-valgrind] [-a] [--dry-run] [-r]
                   [-c COMPILER] [--compiler-handler COMPILER_HANDLER] [-s]
                   [-f] [--statistics] [--no-colors] [-i] [--quiet] [-v]
                   [--version]
                   [target] ...

positional arguments:
  target                target to handle
  extra_args            argument passed to action

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           compiling with debug flags
  --use-valgrind        use valgrind when compiling
  -a, --analyze         build for analyzing
  --dry-run             only show the tasks to be done
  -r, --raw-format      echo command in raw format
  -c COMPILER, --compiler COMPILER
                        choose compiler
  --compiler-handler COMPILER_HANDLER
                        choose compiler module directly
  -s, --serial          compile in a serial maner
  -f, --force           force action to execute
  --statistics          printout some statistics
  --no-colors           no colors in printouts
  -i, --ignore-errors   ignore compiler errors
  --quiet               do not printout command logging
  -v, --verbose         print some verbose output
  --version             print version number
```

### Targets
- compile
- link
- test
- install

## DSL
Following 'tasks' can be used out of the box

- Compile( sourcefile, objectfile = None, directive = [])
- LinkLibrary( destination, objects, libs)
- LinkArchive( destination, objects)
- LinkExecutable( destination, objects, libs)
- LinkUnittest( destination, objects, libs)
- Install( source, path)
- Environment( variabel, value)
- IncludePaths( paths)
- LibraryPaths( paths)
- Dependencies(target, dependencies)
- Build( filename)

## Compiler
Right now g++ is supported.

### Customization
It is possible to register a customized DSL.

It is also possible to customize the toolchain.
There are two ways to do that customization.
You can use a file given by the environment variable CASUAL_MAKE_CONFIGURATION_PATH. 

You can also create and use the file .casual/toolchain.json in your own repository.

The third and last way is to use the .casual/toolchain.json file provided in the casual-make application.

The recommended way is to use alternative two with a toolchain.json file in your own repository. 

Prioritywise the system use the described alternatives in that order to find the config.


#### Example
```
{
   "Linux" : { 
      "g++" : {  
         "defaults": {
            "compiler": ["g++"],
            "executable_linker": ["g++"],
            "library_linker": ["g++"],
            "archive_linker": ["ar", "rcs"],
            "header_dependency_command": ["g++", "-std=c++23", "-E", "-MMD"],
            "common_compile_flags": [
               "-std=c++23",
               "-Wall",
               "-Wextra",
               "-Werror",
               "-Wno-unused-parameter",
               "-Wno-implicit-fallthrough",
               "-Wno-missing-field-initializers",
               "-Wno-dangling-reference",
               "-Wno-address", 
               "-Wno-class-memaccess",
               "-c", 
               "-fPIC"
            ],
            "common_link_flags": ["-pthread"]
         },
         "profiles" : {
            "normal" : {
               "compile_extra": ["-O3", "-pthread"],
               "link_extra_exe": ["-O3"],
               "link_extra_lib": ["-O3", "-shared"]
            },

            "debug" : {
               "compile_extra": ["-g", "-O0", "-DDEBUG"],
               "link_extra_exe": ["-g", "-O0"],
               "link_extra_lib": ["-g", "-O0", "-shared"]
            },

            "analyze" : {
               "compile_extra": ["-O0", "-fanalyzer"],
               "link_extra_exe": ["-O0", "-coverage"],
               "link_extra_lib": ["-O0", "-coverage","-shared"]
            }
         }
      }
   },
   "Darwin" : { 
      "g++" : {  
         "defaults": {
            "compiler": ["g++"],
            "executable_linker": ["g++"],
            "library_linker": ["g++"],
            "archive_linker": ["ar", "rcs"],
            "header_dependency_command": ["g++", "-std=c++23", "-E", "-MMD"],
            "common_compile_flags": [
               "-std=c++23",
               "-Wall",
               "-Wextra",
               "-Werror",
               "-Wno-unused-parameter",
               "-Wno-implicit-fallthrough",
               "-Wno-missing-field-initializers",
               "-Wno-character-conversion",
               "-Wno-deprecated-literal-operator",
               "-fPIC", 
               "-c"],
            "common_link_flags": ["-pthread"]
         },
         "profiles" : {
            "normal" : {
               "compile_extra": ["-O3","-pthread"],
               "link_extra_exe": ["-O3"],
               "link_extra_lib": ["-O3", "-dynamiclib"]
            },

            "debug" : {
               "compile_extra": ["-g", "-O0", "-DDEBUG", "-ggdb"],
               "link_extra_exe": ["-g","-ggdb"],
               "link_extra_lib": ["-g", "-dynamiclib","-ggdb"]
            },

            "analyze" : {
               "compile_extra": ["-O0", "-fanalyzer", "-fprofile-arcs", "-ftest-coverage"],
               "link_extra_exe": ["-O0", "-lgcov", "-fprofile-arcs"],
               "link_extra_lib": ["-O0", "-dynamiclib", "-fprofile-arcs"]
            }
         }
      }
   }

}

```

### To register own targets in the simplest form
```
from casual.make.entity.target import Recipe
import casual.make.entity.model as model

def example_function(arguments):
   """
   arguments is a dict with key/value
   """   

   doSomething( arguments)

# main - register function
custom_target = model.register( 'custom_name')
custom_target.execute = True # always execute
custom_target.need_serial_execution = True # execute in serial mode. Default is parallel.

custom_target.add_recipe( Recipe( example_function, some_argumet_dict))
```

Is used like this:
```
hostname$ casual-make custom_name
```

### More extended example with DSL creation
[casual dsl](https://bitbucket.org/casualcore/casual/src/b4c119f54b4306f96846e1d51a780d2b3f2beb5c/middleware/make/casual/middleware/make/api.py?at=feature%2F1.5%2Fuse-new-build-system)