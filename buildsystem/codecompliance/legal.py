# Copyright 2014-2018 the openage authors. See copying.md for legal info.

"""
Checks the legal headers of all files.
"""

from datetime import date
import re
from subprocess import Popen, PIPE

from .util import findfiles, readfile, writefile, has_ext, SHEBANG


OPENAGE_AUTHORS = (
    "Copyright (?P<crstart>\\d{4})-(?P<crend>\\d{4}) the openage authors\\."
)
OPENAGE_AUTHORTEMPLATE = (
    "Copyright {crstart}-{crend} the openage authors."
)

NATIVELEGALHEADER = re.compile(
    "^"
    # Allow shebang line, followed by an optional empty line.
    "(" + SHEBANG + ")?"

    # Next line must be the copyright line.
    "(#|//) " + OPENAGE_AUTHORS + " See copying\\.md for legal info\\.\n"
)

THIRDPARTYLEGALHEADER = re.compile(
    "^"
    # 3rd-party copyright/license
    "(#|//) This file (was (taken|adapted)|contains (data|code)) from .*\n"
    "(#|//) Copyright \\d{4}-\\d{4} .*\n"
    "(#|//) .*license.*\n"

    # any number of lines containing further 3rd-party copyright info
    "((#|//) .*\\n)*"

    # the openage copyright
    "(#|//) (Modifications|Other (data|code)|Everything else) " +
    OPENAGE_AUTHORS + "\n"
    "(#|//) See copying\\.md for further legal info\\.\n")

# Empty files (consisting of only comments) don't require a legal header.
EMPTYFILE = re.compile("^(((#|//) .*)?\n)*$")

# cython-generated files
CYTHONGENERATED = re.compile("^[^\\n]*(Generated by Cython |failed Cython compilation.)")


# all those files will be checked.
EXTENSIONS_REQUIRING_LEGAL_HEADERS = {
    '.h', '.cpp', '.py', '.pyx', '.pxi', '.cmake', '.h.in',
    '.cpp.in', '.py.in', '.h.template', '.cpp.template',
    '.py.template', '.qml'
}


def get_git_change_year(filename):
    """ Returns git-log's opinion on when the file was last changed. """

    invocation = [
        'git', 'log', '-1', '--format=%ad', '--date=short', '--no-merges', '--',
        filename
    ]

    proc = Popen(invocation, stdout=PIPE)
    output = proc.communicate()[0].decode('utf-8', errors='ignore').strip()

    if proc.returncode != 0 or not output:
        # git doesn't know about the file
        return None

    return int(output[:4])


def match_legalheader(data):
    """
    Tests whether data matches any of the regular expressions,
    and returns a tuple of (matching header regex, match).
    """
    for hdr in (NATIVELEGALHEADER,
                THIRDPARTYLEGALHEADER,
                EMPTYFILE,
                CYTHONGENERATED):

        match = re.match(hdr, data)
        if match is not None:
            return hdr, match

    raise ValueError("no match found")


def create_year_fix(filename, file_content, expected_end_year,
                    found_start_year, headertype):
    """
    Create a function that, when called, fixes the copyright header.
    """

    # check if a fix can be created
    if headertype not in {NATIVELEGALHEADER, THIRDPARTYLEGALHEADER}:
        return None

    def year_fix_function():
        """
        Store the file with correct copyright years.
        """

        fixed_file, success = re.subn(
            OPENAGE_AUTHORS,
            OPENAGE_AUTHORTEMPLATE.format(crstart=found_start_year,
                                          crend=expected_end_year),
            file_content
        )

        if not success:
            raise Exception("copyright year fix did not suceeed")

        writefile(filename, fixed_file)

        return "Copyright for %s was fixed." % filename

    return year_fix_function


def test_headers(check_files, paths, git_change_years, third_party_files):
    """ Tests all in-sourcefile legal headers. """

    if not git_change_years:
        print("warning: I won't check if the copyright matches the git history.")
        print("         Run with --test-git-change-years to enable the check.")

    # determine all uncommited files from git.
    # those definitely need the current year in the copyright message.
    proc = Popen(['git', 'diff', '--name-only', 'HEAD'], stdout=PIPE)
    uncommited = set(proc.communicate()[0].decode('ascii').strip().split('\n'))
    current_calendar_year = date.today().year

    for filename in findfiles(paths, EXTENSIONS_REQUIRING_LEGAL_HEADERS):
        try:
            file_content = readfile(filename)
            headertype, match = match_legalheader(file_content)
        except ValueError:
            yield (
                "Legal header missing or invalid",
                (filename + "\nSee copying.md for a template"),
                None
            )
            continue

        if headertype is THIRDPARTYLEGALHEADER:
            third_party_files.add(filename)

        try:
            found_start_year = int(match.group('crstart'))
            found_end_year = int(match.group('crend'))
        except IndexError:
            # this header type has/needs no copyright years
            # (e.g. empty file)
            continue

        expected_end_year = None
        if filename in uncommited:
            expected_end_year = current_calendar_year
        elif git_change_years:
            if check_files is None or filename in check_files:
                expected_end_year = get_git_change_year(filename)

        if expected_end_year is None:
            continue

        if found_end_year != expected_end_year:

            fix = create_year_fix(
                filename,
                file_content,
                expected_end_year,
                found_start_year,
                headertype
            )

            yield (
                "Bad copyright year",
                (filename + "\n" +
                 "\tExpected %d\n" % expected_end_year +
                 "\tFound    %d" % found_end_year),
                fix
            )


def find_issues(check_files, paths, git_change_years=False):
    """
    Tests all source files for the required legal headers.
    """

    third_party_files = set()

    yield from test_headers(
        check_files, paths, git_change_years, third_party_files)

    # test whether all third-party files are listed in copying.md
    listed_files = set()
    for line in readfile('copying.md').split('\n'):
        match = re.match("^ - `([^`]+)`.*$", line)
        if not match:
            continue

        filename = match.group(1)
        listed_files.add(filename)

    # file listed, but has no 3rd-party header?
    for filename in sorted(listed_files - third_party_files):
        if has_ext(filename, EXTENSIONS_REQUIRING_LEGAL_HEADERS):
            yield (
                "third-party file listing issue",
                ("{}\n\tlisted in copying.md, but has no "
                 "third-party license header.").format(filename),
                None
            )

    # file has 3rd-party header, but is not listed?
    for filename in sorted(third_party_files - listed_files):
        yield (
            "third-party file listing issue",
            ("{}\n\thas a third-party license header, but isn't "
             "listed in copying.md").format(filename),
            None
        )
