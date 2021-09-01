# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse
import logging
import warnings

from .mostypes import MosFile, RunningOrder
from .moscollection import MosCollection
from .utils import s3
from .exc import MosRoMgrException, MosInvalidXML, UnknownMosFileType, InvalidMosCollection
from . import __version__


logger = logging.getLogger('mosromgr.cli')
logger.propagate = False
warnings.filterwarnings('ignore')


class CLI:
    def __init__(self):
        self._args = None
        self._commands = None
        self._config = None
        self._parser = None

    def __call__(self, args=None):
        self._args = self.parser.parse_args(args)
        try:
            return self._args.func()
        except Exception as e:
            sys.stderr.write(f"mosromgr error: {e}\n")
            return 2

    @property
    def parser(self):
        """
        The parser for all the sub-commands that the script accepts. Returns the
        newly constructed argument parser.
        """
        if self._parser is None:
            self._parser, self._commands = self._get_parser()
        return self._parser

    @property
    def commands(self):
        """
        A dictionary mapping command names to their sub-parser.
        """
        if self._commands is None:
            self._parser, self._commands = self._get_parser()
        return self._commands

    def _get_parser(self):
        parser = argparse.ArgumentParser(
            description=("mosromgr is a tool for managing MOS running orders"))
        parser.add_argument(
            '--version', action='version', version=__version__)
        parser.set_defaults(cmd=None, func=self.do_help)
        commands = parser.add_subparsers(title=("commands"))

        help_cmd = commands.add_parser(
            "help",
            description=(
                "With no arguments, displays the list of mosromgr "
                "commands. If a command name is given, displays the "
                "description and options for the named command."),
            help=("Displays help about the specified command"))
        help_cmd.add_argument(
            "cmd", metavar="cmd", nargs='?',
            help=("The name of the command to output help for")
        )
        help_cmd.set_defaults(func=self.do_help)

        detect_cmd = commands.add_parser(
            "detect",
            description=("Detect the MOS type of one or more files"),
            help=("Detect the MOS type of one or more files"))
        detect_cmd.add_argument(
            "-f", "--files", metavar="files", nargs='*',
            help=("The MOS files to detect")
        )
        detect_cmd.add_argument(
            "-b", "--bucket-name", metavar="bucket",
            help=("The name of the S3 bucket containing the MOS files")
        )
        detect_cmd.add_argument(
            "-p", "--prefix", metavar="prefix",
            help=("The prefix for MOS files in the S3 bucket")
        )
        detect_cmd.add_argument(
            "-s", "--suffix", metavar="suffix",
            help=("The suffix for MOS files in the S3 bucket")
        )
        detect_cmd.add_argument(
            "-k", "--key", metavar="key",
            help=("The file key for a MOS file in the S3 bucket")
        )
        detect_cmd.set_defaults(func=self.do_detect)

        inspect_cmd = commands.add_parser(
            "inspect",
            description=("Inspect the contents of a MOS file"),
            help=("Inspect the contents of a MOS file"))
        inspect_cmd.add_argument(
            "-f", "--files", metavar="files", nargs='*',
            help=("The MOS files to inspect")
        )
        inspect_cmd.add_argument(
            "-b", "--bucket-name", metavar="bucket",
            help=("The name of the S3 bucket containing the MOS files")
        )
        inspect_cmd.add_argument(
            "-p", "--prefix", metavar="prefix",
            help=("The prefix for MOS files in the S3 bucket")
        )
        inspect_cmd.add_argument(
            "-s", "--suffix", metavar="suffix",
            help=("The suffix for MOS files in the S3 bucket")
        )
        inspect_cmd.add_argument(
            "-k", "--key", metavar="key",
            help=("The file key for a MOS file in the S3 bucket")
        )
        inspect_cmd.set_defaults(func=self.do_inspect)

        merge_cmd = commands.add_parser(
            "merge",
            description=("Merge the provided MOS files"),
            help=("Merge the provided MOS files"))
        merge_cmd.add_argument(
            "-f", "--files", metavar="files", nargs='*',
            help=("The MOS files to merge")
        )
        merge_cmd.add_argument(
            "-b", "--bucket-name", metavar="bucket",
            help=("The name of the S3 bucket containing MOS files")
        )
        merge_cmd.add_argument(
            "-p", "--prefix", metavar="prefix",
            help=("The file prefix for MOS files in the S3 bucket")
        )
        merge_cmd.add_argument(
            "-s", "--suffix", metavar="suffix",
            help=("The file suffix for MOS files in the S3 bucket")
        )
        merge_cmd.add_argument(
            "-o", "--outfile", metavar="outfile",
            help=("Output to a file")
        )
        merge_cmd.add_argument(
            "-i", "--incomplete",
            action='store_true',
            help=("Allow an incomplete collection")
        )
        merge_cmd.add_argument(
            "-n", "--non-strict",
            action='store_true',
            help=("Downgrade MOS merge errors to warnings")
        )
        merge_cmd.set_defaults(cmd='merge', func=self.do_merge)

        return parser, commands.choices

    def get_mos_object_from_file(self, mos_file_path):
        try:
            return MosFile.from_file(mos_file_path)
        except MosInvalidXML as e:
            sys.stderr.write(f"{mos_file_path}: Invalid XML\n")
        except UnknownMosFileType as e:
            sys.stderr.write(f"{mos_file_path}: Unknown MOS file type\n")

    def get_mos_object_from_s3(self, bucket, file_key):
        try:
            return MosFile.from_s3(bucket_name=bucket, mos_file_key=file_key)
        except MosInvalidXML as e:
            sys.stderr.write(f"{file_key}: Invalid XML\n")
        except UnknownMosFileType as e:
            sys.stderr.write(f"{file_key}: Unknown MOS file type\n")

    def do_help(self):
        if self._args.cmd:
            self.parser.parse_args([self._args.cmd, '-h'])
        else:
            self.parser.parse_args(['-h'])

    def do_detect(self):
        self._args.cmd = 'detect'
        return self.detect_or_inspect(inspect=False)

    def do_inspect(self):
        self._args.cmd = 'inspect'
        return self.detect_or_inspect(inspect=True)

    def detect_or_inspect(self, inspect=False):
        if self._args.files:
            for file in self._args.files:
                try:
                    mo = MosFile.from_file(file)
                except MosRoMgrException as e:
                    sys.stderr.write(f"{file}: Invalid\n")
                    continue
                self.detect_file(mo, file)
                if inspect:
                    mo.inspect()
                    print()
        elif self._args.bucket_name:
            if self._args.prefix:
                if self._args.suffix:
                    mos_file_keys = s3.get_mos_files(
                        bucket_name=self._args.bucket_name,
                        prefix=self._args.prefix,
                        suffix=self._args.suffix,
                    )
                else:
                    mos_file_keys = s3.get_mos_files(
                        bucket_name=self._args.bucket_name,
                        prefix=self._args.prefix,
                    )
            elif self._args.key:
                mos_file_keys = [self._args.key]
            else:
                sys.stderr.write("Prefix or file key must be provided with bucket name\n\n")
                self.do_help()
                return 2
            for mos_file_key in mos_file_keys:
                try:
                    mo = MosFile.from_s3(self._args.bucket_name, mos_file_key)
                except MosRoMgrException as e:
                    sys.stderr.write(f"{mos_file_key}: Invalid\n")
                    continue
                self.detect_file(mo, mos_file_key)
                if inspect:
                    mo.inspect()
                    print()
        else:
            sys.stderr.write("Files or bucket name and prefix or key must be provided\n\n")
            self.do_help()
            return 2

    def detect_file(self, mo, filename):
        if mo.completed:
            print(f"{filename}: {mo.__class__.__name__} (completed)")
        else:
            print(f"{filename}: {mo.__class__.__name__}")

    def do_merge(self):
        self._args.cmd = 'merge'
        try:
            if self._args.files:
                mc = MosCollection.from_files(
                    self._args.files,
                    allow_incomplete=self._args.incomplete
                )
            elif self._args.bucket_name:
                if self._args.suffix:
                    mc = MosCollection.from_s3(
                        bucket_name=self._args.bucket_name,
                        prefix=self._args.prefix,
                        suffix=self._args.suffix,
                        allow_incomplete=self._args.incomplete,
                    )
                else:
                    mc = MosCollection.from_s3(
                        bucket_name=self._args.bucket_name,
                        prefix=self._args.prefix,
                        allow_incomplete=self._args.incomplete,
                    )
            else:
                sys.stderr.write("Files or bucket name and prefix must be provided\n\n")
                self.do_help()
                return 2
        except InvalidMosCollection as e:
            sys.stderr.write(f"Error: {e}\n")
            return 2
        strict = not self._args.non_strict
        mc.merge(strict=strict)
        if self._args.outfile:
            with open(self._args.outfile, 'w') as f:
                print("Writing merged running order to", self._args.outfile)
                f.write(str(mc))
        else:
            print(mc)

main = CLI()
