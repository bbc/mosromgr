import argparse
import sys
from glob import glob
from pathlib import Path
import logging

from ..utils import s3
from ..moscollection import MosCollection
from ..exc import MosRoMgrException


"mosromgr command line tool"


class Runner:
    def __init__(self):
        self.logger = logging.getLogger('mos_runner')
        self.parser = argparse.ArgumentParser(
            description=__doc__
        )
        self.parser.add_argument(
            '-d', '--directory',
            dest='directory',
            default=None,
            help=''
        )
        self.parser.add_argument(
            '-b', '--bucketname',
            dest='bucket_name',
            default=None,
            help=''
        )
        self.parser.add_argument(
            '-p', '--prefix',
            dest='bucket_prefix',
            default=None,
            help=''
        )

    def __call__(self, args=None):
        if args is None:
            args = sys.argv[1:]
        try:
            return self.main(self.parser.parse_args(args)) or 0
        except argparse.ArgumentError as e:
            # argparse errors are already nicely formatted, print to stderr and
            # exit with code 2
            raise e
        except Exception as e:
            raise
            # Output anything else nicely formatted on stderr and exit code 1
            self.parser.exit(1, '{prog}: error: {message}\n'.format(
                prog=self.parser.prog, message=e))

    def main(self, args):
        try:
            if args.directory:
                files = glob(f'{args.directory}/*.mos.xml')
                mos_files = [Path(f) for f in files]
                self.logger.info('found %s mos files', len(mos_files))
                mc = MosCollection.from_files(mos_files)
                self.logger.info('Created MosCollection')
            elif args.bucket_name and args.bucket_prefix:
                mos_file_keys = s3.get_mos_files(args.bucket_name, args.bucket_prefix)
                self.logger.info('Got %s mos files from s3', len(mos_file_keys))
                mc = MosCollection.from_s3(
                    bucket_name=args.bucket_name,
                    mos_file_keys=mos_file_keys
                )
                self.logger.info('Created MosCollection')
            else:
                print("Invalid arguments")
                return 2
            mc.merge()
            print(mc)
            return 0
        except MosRoMgrException as e:
            print(e)
            return 2


main = Runner()
