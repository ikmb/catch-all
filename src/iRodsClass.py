import glob
import os
import sys

import pandas

import Misc


class UploadFastq():
    """
    This class will help to upload fastq files in the irods/yoda system
    """

    @classmethod
    def main(cls, metadata, ifolder, folder=None, upload=False, meta=False):
        """
        The main wrapper function for uploading the the fastq files with all the necessary checks. given a metaddata
        csv file. It will read it, guess the folder names from the metadata and search it in the <folder>. Every row
        in the metadata should have corresponding folder. folders should be same prefix as fastq files, without
        _R1_001.fastq.gz or _R2_001.fastq.gz. Fastq naming system are automatically created from the cluster. So does
        not need much attention. it will check if every folder has 4 files. Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5sum, Read2.fastq.gz.md5sum. Then it will give commands to start uploading the data irods and
        remove all the metadata first but then after removing the metadata it will update the new metadata

        Args:
            metadata: Path of the metadata info excel sheet that is generated. check
            https://github.com/ikmb/data-management/scripts/metadata_set_table_from_lims.rb for more information on
            excel sheet. Mainly it will read Metadata sheet in excel file. Metadata sheet should have information in
            rows. first row is units, second row attribute name and everything else is values needed for irods to be
            uploaded. <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory
            upload: By default it will return commands for upload and add the meta data. But you can run it separately.
            If upload=True is used it will only return upload commands. Good in case very big multiple files
            meta: By default it will return commands for upload and add the meta data. But you can run it separately.
            If meta=True is used it will return commands to remove the previously uploaded files metadata and
            add new meta data. Only use after you have uploaded the files

        Returns: it will check necessary files present or not and then will return all the commands necessary to upload
        it. It will not run it. For running use os.system(list(dict_commands.values())) or check Submit_iRods.py

        """
        metadf = pandas.read_excel(metadata, sheet_name="Metadata", header=[0, 1]).transpose()
        commands = [
            cls.single_meta_commands(single_meta=single_meta, ifolder=ifolder, folder=folder, upload=upload, meta=meta)
            for index, single_meta in metadf.items()]
        name, commands = zip(*commands)
        dict_commands = dict(zip(name, commands))
        return dict_commands

    @classmethod
    def single_meta_commands(cls, single_meta, ifolder, folder=None, upload=False, meta=False):
        """
        commands neccesary for a single row in the metadata to upload all the files and adding all the necessary
        metadata. for fastq it means you need 4 files inside every folder. folder should be same prefix as fastq files,
        without _R1_001.fastq.gz or _R2_001.fastq.gz. Fastq naming system are automatically created from the cluster.
        So does not need much attention. it will check if every folder has 4 files. Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5sum, Read2.fastq.gz.md5sum. Then it will give commands to start uploading the data irods and
        remove all the metadata first but then after removing the metadata it will update the new metadata
        Args:
            single_meta: single row of Metadata sheet from <metadata>.xlsx
            ifolder: The abs path of irods folder. Please do not upload relative path
            folder: The path of the folder where fastq is present in locally. default is current working directory
            upload: By default it will return commands for upload and add the meta data. But you can run it separately.
            If upload=True is used it will only return upload commands. Good in case very big multiple files
            meta: By default it will return commands for upload and add the meta data. But you can run it separately.
            If meta=True is used it will return commands to remove the previously uploaded files metadata and
            add new meta data. Only use after you have uploaded the files

        Returns: it will check necessary files present or not and then will return all the commands necessary to upload
        the files for a single row

        """
        single_meta = single_meta.reset_index(level=0)
        single_meta.columns = ['units', 'value']
        single_meta, target_folder = cls.checking_folder(single_meta=single_meta, ifolder=ifolder, folder=folder)
        R1, R2 = cls.check_files(target_folder=target_folder)
        if upload:
            if meta:
                print ("both meta and upload cant be True. Use either one of them at a time. If you want run all do "
                       "nothing. By default it will run the whole thing")
                sys.exit(1)
            commands, uploadfolder = cls.uploading_commands(R1=R1, R2=R2, ifolder=ifolder)

        elif meta:
            _, uploadfolder = cls.uploading_commands(R1=R1, R2=R2, ifolder=ifolder)
            R1_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R1, ifolder=ifolder,
                                                       read1=True)
            R1_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R1, read1=True,
                                                          ifolder=ifolder)
            R2_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R2, ifolder=ifolder,
                                                       read1=False)
            R2_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R2, read1=False,
                                                          ifolder=ifolder)
            commands = R1_remove + R1_add_command + R2_remove + R2_add_command
        else:
            upload_commands, uploadfolder = cls.uploading_commands(R1=R1, R2=R2, ifolder=ifolder)
            R1_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R1, ifolder=ifolder,
                                                       read1=True)
            R1_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R1, read1=True,
                                                          ifolder=ifolder)
            R2_remove = cls.removing_metadata_commands(single_meta=single_meta, filepath=R2, ifolder=ifolder,
                                                       read1=False)
            R2_add_command = cls.adding_metadata_commands(single_meta=single_meta, filepath=R2, read1=False,
                                                          ifolder=ifolder)
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

        Returns: It will retrun updated single_meta Series by adding lae info and remove all the NAs. It will also #
        return the target folder which needs to be uploaded from local folder.

        """
        if not os.path.isabs(ifolder):
            print("Your ifolder is not absolute. Please use an absolute path to run it")
            sys.exit(1)
        prefix = single_meta.loc['sample_barcode', 'value'].replace("-DL", "-DS") + '_' + single_meta.loc[
            'library_id', 'value']
        folder = os.path.abspath(folder or os.getcwd())
        target_folder = glob.glob(f'{folder}/{prefix}*/')
        if len(target_folder) > 1:
            print("currently not implemented for more than one lane. please update the code ")
            sys.exit(1)
        elif (len(target_folder) == 0):
            print(
                "no folder found for corresponding folder. Please check and update the excel sheet. if the folder does "
                "not exist please delte the row")
            print(f'expected folder: {folder}/{prefix}*/')
            print(single_meta)
            sys.exit(1)
        else:
            target_folder = target_folder[0]
            single_meta.loc['flowcell_lane', 'value'] = Misc.filename_manipulate.gettingfilename(target_folder[:-1]).split("_")[-1][1:]
            return single_meta.dropna(), target_folder

    @classmethod
    def check_files(cls, target_folder):
        """
        This will check specific files are present in the folder or not. Basically Read1.fastq.gz, Read2.fastq.gz,
        Read1.fastq.gz.md5sum, Read2.fastq.gz.md5sum
        Args:
            target_folder: The local folder which has to be uploaded

        Returns: it will check exact file names. If it has more or less number of files or the naming convention is
        different it will complain. If every thing is ok it will send the full path of R1_gzfile and R2_gzfile

        """
        files = Misc.filename_manipulate.folder_vs_list_single(target_folder)
        if len(files) != 4:
            print(
                "Expected number of files in the folder is expected to be 4. Read1, Read2, Read1.md5sum and "
                "Read2.md5sum. did not find all of them. please check")
            print(files)
            sys.exit(1)
        md5files = [file for file in files if file[-6:] == 'md5sum']
        gzfiles = [file for file in files if file[-6:] != 'md5sum']
        for gzfile in gzfiles:
            if not gzfile + '.md5sum' in md5files:
                print("cant find the md5sum for the corresponsing gzfile")
                print(gzfile)
                sys.exit(1)
        R1_gzfile, R2_gzfile = cls.R1_R2_file(gzfiles)
        return R1_gzfile, R2_gzfile

    @classmethod
    def R1_R2_file(cls, gzfiles):
        """
        given a list of two gzfiles, it will decide which one is Read1 and which one is Read2.
        Args:
            gzfiles: gzfiles both Read1.fastq.gz, Read2.fastq.gz in a list format

        Returns: will return Read1, Read2 fastq zipped path.

        """
        Read = Misc.filename_manipulate.filenamewithoutextension_checking_zipped(gzfiles[0]).split("_")[-2]
        if Read == 'R1':
            R1_gzfile = gzfiles[0]
            R2_gzfile = gzfiles[1]
        else:
            R2_gzfile = gzfiles[0]
            R1_gzfile = gzfiles[1]
        return R1_gzfile, R2_gzfile

    @classmethod
    def uploading_commands(cls, R1, R2, ifolder):
        """
        uploading files to irods commands. It uses irsync -K <local> i:<irods>. full path for irods is important
        Args:
            R1: R1.fastq.gz file path local
            R2: R2.fastq.gz file path local
            ifolder: irods upladoing path full

        Returns: it will create commands for creating folder and uploading all the 4 files.

        """
        uploadfolder = R1.split("/")[-2]
        mkdir_command = f'imkdir -p {ifolder}/{uploadfolder}'
        upload_R1_command = f'irsync -K {R1} i:{ifolder}/{uploadfolder}'
        upload_R2_command = f'irsync -K {R2} i:{ifolder}/{uploadfolder}'
        upload_R1md5_command = f'irsync -K {R1}.md5sum i:{ifolder}/{uploadfolder}'
        upload_R2md5_command = f'irsync -K {R2}.md5sum i:{ifolder}/{uploadfolder}'
        commands = [mkdir_command, upload_R1_command, upload_R1md5_command, upload_R2_command, upload_R2md5_command]
        return commands, uploadfolder

    @classmethod
    def removing_metadata_commands(cls, single_meta, filepath, ifolder, read1=True):
        """
        It will give commands to remove the metadata first. not point adding new metadata in case it already existed.
        imeta rmw -d <irods_file> <meta> % %
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: fastq.gz file path local
            ifolder: irods upladoing path full
            read1: telling the file if it is R1=True or R2=False. Needed to added R1 or R2 in the metadata (or remove in
            this case

        Returns: will return all the commands which are needed to be removed before adding new metadata

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], "/")
        commands = [f'imeta rmw -d {ifolder}/{uploadfile} {meta} % %' for meta in single_meta.index]
        if read1:
            read_info = f'imeta rmw -d {ifolder}/{uploadfile}  pair_end_read % %'
        else:
            read_info = f'imeta rmw -d {ifolder}/{uploadfile} pair_end_read % %'
        commands.append(read_info)
        return commands

    @classmethod
    def adding_metadata_commands(cls, single_meta, filepath, ifolder, read1=True):
        """
        main point of all this. adding metadata to the uploaded irods file. imeta add -d <irods_file> <meta>
        Args:
            single_meta: single_meta: single row of Metadata sheet from <metadata>.xlsx. with added Lane info and
            removed blank lines
            filepath: fastq.gz file path local
            ifolder:  irods upladoing path full
            read1: telling the file if it is R1=True or R2=False. Needed to added R1 or R2 in the metadata (or remove in
            this case

        Returns: will return all the necessary commands which are needed to add the metadata to uplaoded files.

        """
        uploadfile = Misc.joinginglistbyspecificstring(filepath.split("/")[-2:], "/")
        metainfo = list((single_meta.index + ' "' +
                         single_meta.loc[:, 'value'].astype(str) + '" ' +
                         single_meta.loc[:, 'units']).values)
        if read1:
            read_info = f'pair_end_read "Read1" String'
        else:
            read_info = f'pair_end_read "Read2" String'
        metainfo.append(read_info)
        commands = [f'imeta add -d {ifolder}/{uploadfile} {meta}' for meta in metainfo]
        return commands
