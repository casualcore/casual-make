# Documentation
## Introduction
casual-make is the build system used in casual.

We like the descriptive syntax and think it can be a market for it in the open source community.

## Technique
It uses python 3 as 'language' and internal 'engine'.

## Setup
```
hostname$ export PYTHONPATH=/path/to/casual-make/source:$PYTHONPATH
hostname$ export PATH=/path/to/casual-make/source:$PATH
```

## Environment variables
casual-make sets CASUAL_MAKE_SOURCE_ROOT to current directory where casual-make is run.
It is possible to override this behaviour by setting the variable in setup.

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
It is also possible to set the environment variable CASUAL_MAKE_CONFIGURATION_PATH to point to a jsonfile describing a model to be used performing the tasks.

#### Example
```
{
   "Linux" : { 
      "g++" : {  
         "normal" : {
            "link_directives_exe": 
               ["-fPIC", "-Wall", "-Wextra", "-Werror", "-std=c++17", "-O3"], 
            "link_directives_lib": 
               ["-fPIC", "-Wall", "-Wextra", "-Werror","-std=c++17", "-dynamiclib", "-O3"], 
            "executable_linker": 
               ["g++"], 
            "library_linker": 
               ["g++"], 
            "header_dependency_command": 
               ["g++", "-E", "-MMD", "-std=c++17"],
            "compiler": 
               ["g++"], 
            "archive_linker": 
               ["ar", "rcs"], 
            "compile_directives": 
               ["-Wall", "-Wextra", "-Werror", "-Wsign-compare", "-std=c++17", "-c", "-O3", "-fPIC", "-pthread"], 
            "link_directives_archive": 
               ["-O3", "-pthread"]
         },

         "debug" : {
            ...
         },

         "analyze" : {
            ...
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