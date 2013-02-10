#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import sys
import unittest

VERBOSE = False

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
BUILD_PATH = os.path.join(PROJECT_PATH, 'build')
EXAMPLES_PATH = os.path.join(PROJECT_PATH, 'examples')

LIBRARIES = {
    # core stuff
    'marex': os.path.join(PROJECT_PATH, 'marex'),
    'mapreduce': os.path.join(PROJECT_PATH, 'mapreduce'),
}

def _errwrite(line):
    sys.stderr.write('{0}\n'.format(line))


def _errwrite_verbose(line):
    if VERBOSE:
        _errwrite(line)


def _argparser():
    parser = argparse.ArgumentParser(description='Build "marex" project examples.')
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose', action='store_true',
        help='Provide additional output.'
    )
    parser.add_argument(
        'command',
        choices=['clean', 'build', 'rebuild', 'test'],
        default='rebuild',
        help='Command to execute.'
    )
    parser.add_argument(
        'targets',
        metavar='target', nargs='*',
        default=['all'],
        help='List of targets to (re)build.'
    )
    return parser


def test(*args):
    if len(args) > 0 and (len(args) != 1 or args[0] != 'all'):
        _errwrite('warning: command "test" only accepts one optional target "all", any other values are ignored.')
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=1 if VERBOSE else 0)
    runner.run(loader.discover(PROJECT_PATH, pattern='*_test.py'))


def clean(*args):
    if len(args) == 0 or (len(args) == 1 and args[0] == 'all'):
        _errwrite_verbose('Clean all')
        if os.path.exists(BUILD_PATH):
            args = os.listdir(BUILD_PATH)
            clean(*args)
    elif len(args) > 1:
        for arg in args:
            clean(arg)
    else:
        name = args[0]
        path = os.path.join(BUILD_PATH, name)
        if os.path.exists(path):
            _errwrite_verbose('Clean "{0}"'.format(name))
            shutil.rmtree(path)


def build(*args):
    if len(args) == 0 or (len(args) == 1 and args[0] == 'all'):
        _errwrite_verbose('Build all')
        args = os.listdir(EXAMPLES_PATH)
        args = filter(lambda arg: os.path.isdir(os.path.join(EXAMPLES_PATH, arg)), args)
        build(*args)
    elif len(args) > 1:
        for arg in args:
            build(arg)
    else:
        name = args[0]
        _errwrite_verbose('build "{0}"'.format(name))
        source_path = os.path.join(EXAMPLES_PATH, name)
        target_path = os.path.join(BUILD_PATH, name)
        shutil.copytree(source_path, target_path)

        blobstore_path = os.path.join(target_path, '_blobstore')
        if not os.path.exists(blobstore_path):
            os.makedirs(blobstore_path)

        for library, library_source_path in LIBRARIES.items():
            library_target_path = os.path.join(target_path, library)
            shutil.copytree(library_source_path, library_target_path)


def rebuild(*args):
    clean(*args)
    build(*args)


def main():
    parser = _argparser()
    args = parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose

    commands = {
        'clean': clean,
        'build': build,
        'rebuild': rebuild,
        'test': test,
    }
    commands[args.command](*args.targets)

if __name__ == '__main__':
    main()

