# Instant File Access
A command line utility that gives you "instant" access to a file (or directory).

# How?
  Use a search pattern and the program will open the file that best matches that pattern. The program will navigate
  through the directory tree for you, reducing considerably the time to access that file. The program will no require
  you to give it the precise file name, so you can relay on the program to make the best guess.

# Features
  Use of path variables to tell the program where to start the search.

# Use
```
  ifa [options] [<root>] <search_pattern>
  ifa <subcommand> [args]

Options 
  --directory  | -d   searchs for a directory instead for a file.

Subcommands 	 	
  set <var_name> <path>
  unset <var_name>
  open <var_name>
  echo
```
# Subcomands
ifa provides a list of subcommands to manipulate path variables. These variables are used to store paths names to a system directory. You 
can use a variable name insetead of the full path name of the directory when you want to do a search.

## set
Creates or sets a variable. It requires two arguments: the variable identifier and the path it will point to.
```
ifa set doc E:\Users\user\Documents
```

## unset
Deletes a variable. It takes only one argument, the name of the variable to be removed.
```
ifa unset doc
```

## open
Opens a directory. Takes path name or just a variable identifier and opens the directory it refers to.
```
ifa open doc
```

## echo
Shows all stored variables, with its corresponding value.
```
ifa echo
```

## Examples
The following are actual outputs of the program. All "Best match in" outs, will open the refered directory or file.
```
ifa set doc E:\Documents
"E:\Documents" saved as "doc"

ifa -d doc instant access
Best match in:
"E:\Documents\GitHub\Instant File Access"

ifa -d doc ifa modules
Best match in:
"E:\Documents\GitHub\Instant File Access\modules"

ifa echo
doc="E:\Documents"
```

Note that after you especified a search root (ej. doc), followed arguments are concatenated together as a single search pattern, so you don't
lose time wrapping your search between quotation marks.
