"""

chains.reactor.rules

    This module contains the code related to defining and parsing rules.
    It consists of 3 sub modules:

        config
        definition
        functions

chains.reactor.rules.config

    This module contains the code to load/parse the rules
    F.ex: getRulesEnabled(), getRuleData() etc.

chains.reactor.rules.definition

    This module contains the bits necceceary to define rules. 
    Each rule in rules_available/ should import * from here.
    F.ex: evt(), act(), fun() etc
    
chains.reactor.rules.functions

    This module contains the built-in functions that can be
    used in rules. For now that's just the iff() function,
    but more may be added later. All of these are wrapped in
    a definition in the module above, so it is only used from there.

"""
