import glob
import os
import sys

import pandas

import Misc
from _version import __version__

class UploadFastq:
    """
    This class will help to upload fastq files in the irods/yoda system
    """

    @classmethod
    def main(cls, metadata, ifolder, folder=None, upload=False, meta=False):
        """
        The main wrapper function for uploading the fastq files with all the necessary checks. given a metadata
        csv file. It will read it, guess the folder names from the metadata and search it in the <folder>. Every row
        in the metadata should have corresponding folder. folders should be same prefix as fastq files, without
        _R1_001.fastq.gz or _R2_001.fastq.gz. Fastq naming system are automatically created from the cluster. So does
        not need much attention. it will check if every folder has 4 files. Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5, Read2.fastq.gz.md5. Then it will give commands to start uploading the data irods and
        remove all the metadata first but then after removing the metadata it will update the new metadata

        Args:
            metadata: Path of the metadata info Excel sheet that is generated. check
                https://github.com/ikmb/data-management/scripts/metadata_set_table_from_lims.rb for more information on
                Excel sheet. Mainly it will read Metadata sheet in Excel file. Metadata sheet should have information in
                rows. first row is units, second row attribute name and everything else is values needed for irods to be
            uploaded. <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory
            upload: By default it will return commands for upload and add the metadata. But you can run it separately.
            If upload=True is used it will only return upload commands. Good in case very big multiple files
            meta: By default it will return commands for upload and add the metadata. But you can run it separately.
            If meta=True is used it will return commands to remove the previously uploaded files metadata and
            add new metadata. Only use after you have uploaded the files

        Returns: it will check necessary files present or not and then will return all the commands necessary to upload
        it. It will not run it. For running use os.system(list(dict_commands.values())) or check Submit_iRods.py

        """
        metadf = pandas.read_excel(metadata, sheet_name="Metadata", header=[0, 1]).transpose()
        samples = metadf.loc[('String', 'sample name'), :]
        if metadf.shape[1] != samples.unique().shape[0]:
            print("There are repeated sample name for multiple sequences. Right now the code can not handle that.")
            print("Please check these samples")
            print(samples[samples()])
            sys.exit(1)
        commands = [
            cls.single_meta_commands(single_meta=single_meta, ifolder=ifolder, folder=folder, upload=upload, meta=meta)
            for index, single_meta in metadf.items()]
        name, commands = zip(*commands)
        dict_commands = dict(zip(name, commands))
        return dict_commands

    @classmethod
    def single_meta_commands(cls, single_meta, ifolder, folder=None, upload=False, meta=False):
        """
        commands necessary for a single row in the metadata to upload all the files and adding all the necessary
        metadata. for fastq it means you need 4 files inside every folder. folder should be same prefix as fastq files,
        without _R1_001.fastq.gz or _R2_001.fastq.gz. Fastq naming system are automatically created from the cluster.
        So does not need much attention. it will check if every folder has 4 files. Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5, Read2.fastq.gz.md5. Then it will give commands to start uploading the data irods and
        remove all the metadata first but then after removing the metadata it will update the new metadata
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory
            upload: By default it will return commands for upload and add the metadata. But you can run it separately.
            If upload=True is used it will only return upload commands. Good in case very big multiple files
            meta: By default it will return commands for upload and add the metadata. But you can run it separately.
            If meta=True is used it will return commands to remove the previously uploaded files metadata and
            add new metadata. Only use after you have uploaded the files

        Returns: it will check necessary files present or not and then will return all the commands necessary to upload
        the files for a single row

        """
        single_meta = single_meta.reset_index(level=0).dropna()
        single_meta.columns = ['units', 'value']
        cls.checking_folder(single_meta=single_meta, ifolder=ifolder, folder=folder)
        R1, R2 = cls.check_files(single_meta=single_meta, folder=folder)
        if upload:
            if meta:
                print("both meta and upload cant be True. Use either one of them at a time. If you want run all do "
                      "nothing. By default it will run the whole thing")
                sys.exit(1)
            commands, uploadfolder = cls.uploading_commands(R1=R1, R2=R2, ifolder=ifolder)

        else:
            upload_commands, uploadfolder = cls.uploading_commands(R1=R1, R2=R2, ifolder=ifolder)
            R1_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R1, ifolder=ifolder)
            R1_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R1, ifolder=ifolder)
            R1_special = cls.special_metadata(single_meta=single_meta, filepath=R1, ifolder=ifolder, read1=True)
            R2_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R2, ifolder=ifolder)
            R2_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R2, ifolder=ifolder)
            R2_special = cls.special_metadata(single_meta=single_meta, filepath=R2, ifolder=ifolder, read1=False)
            if meta:
                commands = R1_remove + R1_add_command + R1_special + R2_remove + R2_add_command + R2_special
            else:
                commands = upload_commands + R1_remove + R1_add_command + R2_remove + R2_add_command
        return uploadfolder, Misc.joinginglistbyspecificstring(commands, string="\n")

    @classmethod
    def checking_folder(cls, single_meta, ifolder, folder=None):
        """
        It will check also ifolder is not relative as iRods system has problem with relative path.
        Absolute path is recommended. It will check if the necessary folder exist in the local machine (the name of the
        folder will be derived from the metadata itself). If there are more than one lane for same library it will also
        complain as the proper code for multiple lane is not implemented yet. One library has run only for once.
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory

        Returns: It will return updated single_meta Series by adding lae info and remove all the NAs. It will also
        return the target folder which needs to be uploaded from local folder.

        """
        if not os.path.isabs(ifolder):
            print("Your ifolder is not absolute. Please use an absolute path to run it")
            #sys.exit(1)
        prefix = cls.prefix_call(single_meta)
        folder = os.path.abspath(folder or os.getcwd())
        if not os.path.isdir(f'{folder}/{prefix}/'):
            print(
                "no folder found for corresponding folder. Please check and update the excel sheet. if the folder does "
                "not exist please delete the row")
            print(f'expected folder: {folder}/{prefix}/')
            print(single_meta)
            sys.exit(1)

    @classmethod
    def prefix_call(cls,single_meta):
        """
        predicting the prefix of the file name from the single meta information
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx

        Returns: will return the prefix of the file name (with out R1_001.fastq.gz)

        """
        barcode = single_meta.loc['sample barcode', 'value'].replace("-DL", "-DS")
        library = single_meta.loc['library id', 'value']
        lane = single_meta.loc['flowcell lane', 'value']
        #sample_number = single_meta.loc['sample barcode', 'value'].split("-")[1][2:]
        prefix=f'{barcode}_{library}_{lane}'
        return prefix
    @classmethod
    def check_files(cls, single_meta, folder=None):
        """
        This will check specific files are present in the folder or not. Basically Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5, Read2.fastq.gz.md5
        Args:
            target_folder: The local folder which has to be uploaded

        Returns: it will check exact file names. If it has more or less number of files or the naming convention is
        different it will complain. If every thing is ok it will send the full path of R1_gzfile and R2_gzfile

        """
        if 'flowcell lane' not in single_meta.index:
            print("flowcell lane column is mandatory. Please add")
            sys.exit(1)
        prefix = cls.prefix_call(single_meta)
        folder = os.path.abspath(folder or os.getcwd())
        R1_gzfile = f'{folder}/{prefix}/{prefix}_R1_001.fastq.gz'
        R2_gzfile = f'{folder}/{prefix}/{prefix}_R2_001.fastq.gz'
        for file in [R1_gzfile,R2_gzfile]:
            if not os.path.isfile(file):
                print('Cant find the fastq file. Please check:', file)
                sys.exit(1)
            if not os.path.isfile(f'{file}.md5'):
                print("cant find the md5sum for the corresponding fastq gzfile")
                print(file)
                sys.exit(1)
        return R1_gzfile, R2_gzfile
    @classmethod
    def uploading_commands(cls, R1, R2, ifolder):
        """
        uploading files to irods commands. It uses irsync -K <local> i:<irods>. full path for irods is important
        Args:
            R1: R1.fastq.gz file path local
            R2: R2.fastq.gz file path local
            ifolder: irods uploading path full

        Returns: it will create commands for creating folder and uploading all the 4 files.

        """
        uploadfolder = R1.split("/")[-2]
        mkdir_command = f'imkdir -p {ifolder}/{uploadfolder}'
        upload_R1_command = f'irsync -K {R1} i:{ifolder}/{uploadfolder}'
        upload_R2_command = f'irsync -K {R2} i:{ifolder}/{uploadfolder}'
        upload_R1md5_command = f'irsync -K {R1}.md5 i:{ifolder}/{uploadfolder}'
        upload_R2md5_command = f'irsync -K {R2}.md5 i:{ifolder}/{uploadfolder}'
        commands = [mkdir_command, upload_R1_command, upload_R1md5_command, upload_R2_command, upload_R2md5_command]
        return commands, uploadfolder

    @classmethod
    def removing_metadata_commands(cls, single_meta, filepath, ifolder):
        """
        It will give commands to remove the metadata first. no point adding new metadata in case it already existed.
        imeta rmw -d <irods_file> <meta> % %
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: fastq.gz file path local
            ifolder: irods uploading path full

        Returns: will return all the commands which are needed to be removed before adding new metadata

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], "/")
        commands = [f'imeta rmw -d {ifolder}/{uploadfile} "{meta}" % %' for meta in single_meta.index]
        commands.append(f'imeta rmw -d {ifolder}/{uploadfile} "version" % %')
        return commands

    @classmethod
    def adding_metadata_commands(cls, single_meta, filepath, ifolder):
        """
        main point of all this. adding metadata to the uploaded irods file. imeta add -d <irods_file> <meta>
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: fastq.gz file path local
            ifolder:  irods uploading path full

        Returns: will return all the necessary commands which are needed to add the metadata to uploaded files.

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], "/")
        metainfo = list(('"' + single_meta.index + '" "' +
                         single_meta.loc[:, 'value'].astype(str) + '" ' +
                         single_meta.loc[:, 'units']).values)

        commands = [f'imeta add -d {ifolder}/{uploadfile} {meta}' for meta in metainfo]
        commands.append(f'imeta add -d {ifolder}/{uploadfile} "version" "v{__version__}" String')
        return commands

    @classmethod
    def special_metadata(cls, single_meta, filepath, ifolder, read1=True):
        """
        Special def for every Class. For example for fastq you need to add is this read1 or read2 of the file. if read1
        then add read1 true and it will add necessary commands to update the metadata so that you know this file is
        read1 or read2
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: fastq.gz file path local
            ifolder:  irods uploading path full
            read1: to tell that the files is either read1 or read2. read1=True for default.

        Returns: it will send two commands first to remove the metadata about pair_end_read and then will add the
        metadata stating is it Read1 or Read2

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], string="/")
        meta_remove = f'imeta rmw -d {ifolder}/{uploadfile} "pair_end_read" % %'
        if read1:
            meta_add = f'imeta add -d {ifolder}/{uploadfile} "pair_end_read" "Read1" String'
        else:
            meta_add = f'imeta add -d {ifolder}/{uploadfile} "pair_end_read" "Read2" String'
        commands = [meta_remove, meta_add]
        return commands


class UploadCram(UploadFastq):
    """
    This class will help to upload cram (and crai) files in the irods/yoda system
    """

    @classmethod
    def single_meta_commands(cls, single_meta, ifolder, folder=None, upload=False, meta=False):
        """
        commands necessary for a single row in the metadata to upload all the files and adding all the necessary
        metadata. for cram it means you need 4 files inside every folder. folder should be same prefix as cram files,
        which is generally the sample name. it will check if every folder has 4 files. Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5, Read2.fastq.gz.md5. Then it will give commands to start uploading the data irods and
        remove all the metadata first but then after removing the metadata it will update the new metadata
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where cram is present in locally. default is current working directory
            upload: By default it will return commands for upload and add the metadata. But you can run it separately.
            If upload=True is used it will only return upload commands. Good in case very big multiple files
            meta: By default it will return commands for upload and add the metadata. But you can run it separately.
            If meta=True is used it will return commands to remove the previously uploaded files metadata and
            add new metadata. Only use after you have uploaded the files

        Returns: it will check necessary files present or not and then will return all the commands necessary to upload
        the files for a single row

        """
        single_meta = single_meta.reset_index(level=0)
        single_meta.columns = ['units', 'value']
        single_meta, target_folder = cls.checking_folder(single_meta=single_meta, ifolder=ifolder, folder=folder)
        files = cls.check_files(target_folder)
        if 'fasta' not in single_meta.index:
            print("Could not find the fasta column in the excel. Please add the fasta file is used")
        if upload:
            if meta:
                print("both meta and upload cant be True. Use either one of them at a time. If you want run all do "
                      "nothing. By default it will run the whole thing")
                sys.exit(1)
            commands, uploadfolder = cls.uploading_commands(files=files, ifolder=ifolder)
        else:
            upload_commands, uploadfolder = cls.uploading_commands(files=files, ifolder=ifolder)
            cram_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=files[0], ifolder=ifolder)
            cram_add = cls.adding_metadata_commands(single_meta=single_meta, filepath=files[0], ifolder=ifolder)
            cram_special = cls.special_metadata(single_meta=single_meta, filepath=files[0], ifolder=ifolder)
            if meta:
                commands = cram_remove + cram_add + cram_special
            else:
                commands = upload_commands + cram_remove + cram_add + cram_special
        commands = Misc.joinginglistbyspecificstring(commands, string="\n")
        return uploadfolder, commands

    @classmethod
    def checking_folder(cls, single_meta, ifolder, folder=None):
        """
        It will check ifolder is not relative as iRods system has problem with relative path.Absolute path is
        recommended. It will check if the necessary folder exist in the local machine (the name of the folder will be
        derived from the metadata itself, i.e. sample name).
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory

        Returns: It will return updated single_meta Series by adding lae info and remove all the NAs. It will also
        return the target folder which needs to be uploaded from local folder.

        """
        if not os.path.isabs(ifolder):
            print("Your ifolder is not absolute. Please use an absolute path to run it")
            sys.exit(1)
        prefix = single_meta.loc['sample name', 'value']
        folder = os.path.abspath(folder or os.getcwd())
        target_folder = glob.glob(f'{folder}/{prefix}/')
        if len(target_folder) == 0:
            print(
                "no folder found for corresponding folder. Please check and update the excel sheet. if the folder does "
                "not exist please delete the row")
            print(f'expected folder: {folder}/{prefix}/')
            print(single_meta)
            sys.exit(1)
        else:
            target_folder = target_folder[0]
            return single_meta.dropna(), target_folder

    @classmethod
    def check_files(cls, target_folder):
        """
        This will check specific files are present in the folder or not. Basically samplename.cram, samplename.cram.crai
        samplename.cram.md5 and samplename.cram.crai.md5
        Args:
            target_folder: The local folder which has to be uploaded

        Returns: it will check exact file names. If every thing is ok it will send the full path of samplename.cram,
        samplename.cram.crai, samplename.cram.md5 and samplename.cram.crai.md5

        """
        samplename = os.path.basename(target_folder[:-1])
        if not os.path.exists(f'{target_folder}{samplename}.cram'):
            print("could not find the cram file. please check:", f'{target_folder}{samplename}.cram')
            sys.exit(1)
        if not os.path.exists(f'{target_folder}{samplename}.cram.md5'):
            print("could not find the cram.md5 file. please check:", f'{target_folder}{samplename}.cram.md5')
            sys.exit(1)
        if not os.path.exists(f'{target_folder}{samplename}.cram.crai'):
            print("could not find the crai file. please check:", f'{target_folder}{samplename}.cram.crai')
            sys.exit(1)
        if not os.path.exists(f'{target_folder}{samplename}.cram.crai.md5'):
            print("could not find the crai.md5 file. please check:", f'{target_folder}{samplename}.cram.crai.md5')
            sys.exit(1)
        files = [f'{target_folder}{samplename}.cram', f'{target_folder}{samplename}.cram.crai',
                 f'{target_folder}{samplename}.cram.md5', f'{target_folder}{samplename}.cram.crai.md5']
        return files

    @classmethod
    def uploading_commands(cls, files, ifolder):
        """
        uploading files to irods commands. It uses irsync -K <local> i:<irods>. full path for irods is important
        Args:
            files: list of files path (cram, cram.crai, cram.md5, cram.crai.md5)
            ifolder: irods uploading path full

        Returns: it will create commands for creating folder and uploading all the 4 files.

        """
        uploadfolder = files[0].split("/")[-2]
        mkdir_command = f'imkdir -p {ifolder}/{uploadfolder}'
        upload_cram_command = f'irsync -K {files[0]} i:{ifolder}/{uploadfolder}'
        upload_crai_command = f'irsync -K {files[1]} i:{ifolder}/{uploadfolder}'
        upload_crammd5_command = f'irsync -K {files[2]} i:{ifolder}/{uploadfolder}'
        upload_craimd5_command = f'irsync -K {files[3]} i:{ifolder}/{uploadfolder}'
        commands = [mkdir_command, upload_cram_command, upload_crai_command, upload_crammd5_command,
                    upload_craimd5_command]
        return commands, uploadfolder

    @classmethod
    def special_metadata(cls, single_meta, filepath, ifolder):
        """
        Special def for every Class. For cram you need to add is the read1 or read2 that was used to create cram file
        under pair_end_reads metadata
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: cram file path
            ifolder: irods uploading path full

        Returns: it will first remove pair_end_reads from the meta data and then will generate necessary fastq file
        names from excel sheet and add the pair_end_reads metadata. flowcell lane is important in this case. please
        add it in the excel sheet. add L001 format

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], string="/")
        meta_remove = f'imeta rmw -d {ifolder}/{uploadfile}  "pair_end_reads" % %'
        if 'flowcell lane' not in single_meta.index:
            print("flowcell lane column is mandatory. Please add")
            sys.exit(1)
        prefix = cls.prefix_call(single_meta)
        R1 = f'{prefix}_R1_001.fastq.gz'
        R2 = f'{prefix}_R2_001.fastq.gz'
        meta_add = f'imeta add -d {ifolder}/{uploadfile} "pair_end_reads" "{R1} {R2}" String'
        commands = [meta_remove, meta_add]
        return commands
