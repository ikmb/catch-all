"""
Uploading the files in the Yoda/iRods system and adding the metadata
"""
import argparse
import os

import iRodsClass
from Common import Misc
from SubmittingJobs import SubmittingJobsClass

parser = argparse.ArgumentParser(description="Uploading the files in the Yoda/iRods system and adding the metadata. "
                                             "You need to login first using iinit")
subparsers = parser.add_subparsers(help='sub-commands help')
sp = subparsers.add_parser('fastq', help='Uploading the fastq files. For now only works for pair end illumina'
                                         'genome sequences')
sp.set_defaults(cmd='fastq')
sp.add_argument('xlsx', help="Path of the metadata info excel sheet that is generated. check "
                             "https://github.com/ikmb/data-management/scripts/metadata_set_table_from_lims.rb for more "
                             "information on excel sheet. Mainly it will read Metadata sheet in excel file. Metadata "
                             "sheet should have information in rows. first row is units, second row attribute name"
                             "and everything else is values needed for irods to be uploaded",
                type=lambda x: Misc.args_valid_file(parser, x))
sp.add_argument('--ifolder', help="The abs path of irods folder. Please do not upload realtive path", required=True)
sp.add_argument('--folder', help="The path of the folder where fastq is present in locally. default is current working "
                                 "directory")
sp.add_argument('--run',
                help='As the name suggest. by default it will submit the jobs in the cluster. But if we dont want '
                     'that this will force run all the jobs in the single terminal', action="store_true")
sp.add_argument('--upload',
                help='By default it will upload and add the meta data. But you can run it separately. If --upload is '
                     'used it will only upload the data', action="store_true")
sp.add_argument('--meta',
                help='By default it will upload and add the meta data. But you can run it separately. If --meta is '
                     'used it will remove the previously uploaded files metadata and add new meta data. Only use'
                     'after --upload', action="store_true")
args = parser.parse_args()
if args.cmd == "fastq":
    commands = iRodsClass.UploadFastq.main(metadata=args.xlsx, ifolder=args.ifolder, folder=args.folder,
                                           upload=args.upload, meta=args.meta)
    if args.run:
        Misc.creatingfolders("shfiles")
        if args.upload:
            prefix="upload"
        elif args.meta:
            prefix="meta"
        else:
            prefix="all"
        _ = [Misc.writing_bylines4mlist([commands[name]], output=f'shfiles/{prefix}_{name}.sh') for name in commands]
    for name in commands:
        if args.run:
            # os.system(f'sh shfiles/{name}.sh')
            print(f'{name} is done')
        else:
            args = argparse.Namespace(command=commands[name], name=name, log=True, sh=True, memory=4000)
            submission = SubmittingJobsClass.sbatchoneliner(args)
            submitcommand = submission.argsparser()
            os.system(submitcommand)
