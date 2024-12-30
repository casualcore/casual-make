from dataclasses import dataclass, field

from types import SimpleNamespace
import json


@dataclass
class Directive( object):
    directive : list[str] = field(default_factory=list)

@dataclass
class Cpp_Standard( Directive):
    pass

@dataclass
class Warning( Directive):
    pass

@dataclass
class CommandDirective( object):
    command : list[str] = field(default_factory=list)
    directive : list[str] = field(default_factory=list)

@dataclass
class Dependency( CommandDirective):
    pass

@dataclass
class Compile( object):
    command : list[str] = field(default_factory=list)
    directive : list[str] = field(default_factory=list)
    warning: Warning = field(default_factory=Warning)

@dataclass
class Link( object):
    executable: CommandDirective = field(default_factory=CommandDirective)
    library: CommandDirective = field(default_factory=CommandDirective)
    archive: CommandDirective = field(default_factory=CommandDirective)

@dataclass
class Profile( object):
    name: str
    cpp_standard: Cpp_Standard = field(default_factory=Cpp_Standard)
    dependency: Dependency = field(default_factory=Dependency)
    compile : Compile = field(default_factory=Compile)
    link : Link = field(default_factory=Link)

@dataclass
class System( object):
    name: str = ""
    compiler: str = field(default_factory=list)
    profile: list[Profile] = field(default_factory=list)

@dataclass
class Configuration( object):
    version: float = field(default_factory=float)
    system: list[System] = field(default_factory=list)

    def __init__(self, document):
        jdoc = json.dumps( document["configuration"], indent=2, default=vars)
        x = json.loads( str(jdoc), object_hook=lambda d: SimpleNamespace(**d))
        self.__dict__.update( x.__dict__)        

    def profile_find( self, system, compiler, profile):
        for system_item in self.system:
            if system_item.name == system and system_item.compiler == compiler[0]:
                for profile_item in system_item.profile:
                    if profile_item.name == profile:
                        return profile_item

        raise SystemError(f"{system}, {compiler[0]}, {profile}: Not found in configuration")





