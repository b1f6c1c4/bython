#! /usr/bin/python3
import os
import re
import argparse
import sys
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME

from bython import VERSION_NUMBER
from logger import Logger


def ends_in_py(word):
    """Returns True if word ends in .py, else False"""
    return word[-3:] == ".py"


def change_file_name(name):
    """Changes .py filenames to .by filenames

    If filename does not end in .py, adds .by to the end"""
    if ends_in_py(name):
        return name[:-3] + ".by"
    else:
        return name + ".by"


def reverse_parse(filename):
    """Changes a Python file to a Bython file
    
    All semantically significant whitespace resulting in a change
    in indentation levels will have a matching opening or closing
    curly-brace.
    """
    # Open a file as bytes
    infile = open(filename, "rb")
    inlines = infile.readlines()

    # Store and format the contents for later modification
    for index, line in enumerate(inlines):
        inlines[index] = line.decode("utf-8")
        inlines[index] = inlines[index].rstrip()

    # Tokenize the same file, close it
    infile.seek(0)
    tokens = list(tokenize(infile.readline))
    infile.close()
    
    # Stores a list of tuples for INDENT/DEDENT
    # (token, line_number, position_in_line)
    indent_tracker = []
    
    # Track line by line the indentation position.
    # Populates indent_tracker, using indent_levels as a stack
    # to properly record whitespace for each bython brace.
    indent_levels = []
    position = 0;
    line_of_last_name_token = 0;
    for token in tokens:
        current_line = token.start[0]
        if ((token.exact_type == NAME)
            and line_of_last_name_token != current_line):
            line_of_last_name_token = current_line
            position = token.start[1]
        if (token.exact_type == INDENT):
            indent_levels.append(position)
            indent_tracker.append((INDENT,current_line,position))
        if (token.exact_type == DEDENT):
            indent_tracker.append((DEDENT,current_line,indent_levels.pop()))
    
    # Add curly braces where necessary to create our bython file
    extra = 0
    for indent in indent_tracker:
        token = indent[0]
        index = indent[1]
        position = indent[2]
        inlines.insert(
            index + extra - 1,
            " " * position
            + ("}","{")[token==INDENT]
        )
        extra += 1

    # Save the file
    outfile = open(change_file_name(filename),"w")
    for line in inlines:

        # Quick fix to solve problem with remaining colons, should be reworked to
        # something more elegant
        line = re.sub(r"\s*:", "", line)

        print(line,file=outfile)


def main():
    """
    Translate python to bython

    Command line utility and Python module for translating python code
    to bython code, adding curly braces at semantically significant
    indentations.
    """ 
    argparser = argparse.ArgumentParser("py2by",
        description="py2by translates python to bython",
        formatter_class=argparse.RawTextHelpFormatter
    )
    argparser.add_argument("-v", "--version", action="version",
        version="py2by is a part of Bython v%s\nMathias Lohne and Tristan Pepin 2017" % VERSION_NUMBER)
    argparser.add_argument("input", type=str,
        help="python file to translate", nargs=1)

    cmd_args = argparser.parse_args()

    logger = Logger()

    try:
        reverse_parse(cmd_args.input[0])

    except FileNotFoundError:
        logger.log_error("No file named %s" % cmd_args.input[0])

    except Exception as e:
        logger.log_error("Unexpected error: %s" % str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
