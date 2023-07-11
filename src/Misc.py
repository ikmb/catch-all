#!/usr/bin/python
"""
This file is for miscellaneous def. as i am lazy not going to write def again and again
"""
import os
def args_valid_file(parser, arg):
    """
    This will check with in the argparse and report if the file exist or not. should be used in the argparse command
    parser.add_argument('file',type=lambda x: Misc.args_valid_file(parser, x))
    Args:
        parser: argparse.ArgumentParser which is the main for argparse command
        arg: the path of the command itself

    Returns: if the file exist it will return the path if not it will print an error message

    """
    if arg:
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
    return arg

def joinginglistbyspecificstring(listinput, string=" "):
    """
    It join a list with the given string
    :param listinput: the input list
    :param string: the string with which it has to join. by default is space
    :return: the joined string
    """
    listinput = [x for x in listinput if x is not None]  ##to remove none
    listinput = list(map(str, listinput))
    return string.join(listinput)

class filename_manipulate:
    @classmethod
    def gettingfilename(cls, filepath):
        """
            It wil give back the name of the file from the filepath
        :return:    Name of the file
        """
        if "/" in filepath:
            words = filepath.split("/")
            filename = words[len(words) - 1]
            return filename
        else:
            return filepath

    @classmethod
    def folder_vs_list_single(cls, input=None, extension=""):
        """
        This definition is specifically meant when we give a input folder or a single file or a list of file in a text file
         and it will return the file list choosing which is appropiate between them
        :param input: Can either be folder or single file path or a list of files inside a text file. default is none
        meaning current folder
        :param extension: the last 4 element of the file. It should match, thus not giving all the files in that folder
        :return: the file list which have the desired extensions
        """
        import glob, os.path, sys
        files = []
        if input is None:
            files = glob.glob("*" + extension)
        elif input[-1] == "/":
            if os.path.exists(input):
                files = glob.glob(input + "*" + extension)
            else:
                print("The folder do not exist", input)

        elif input[-len(extension):] == extension:

            if os.path.exists(input):
                files.append(input)
            else:
                print("The file do not exist", input)

        elif isinstance(input, list):
            files = input
            for file in files:
                if not os.path.exists(file):
                    print("file do not exist:", file)
                    sys.exit(1)
        else:
            if os.path.isdir(input):
                files = glob.glob(input + '/' + "*" + extension)
            elif os.path.isfile(input):
                tempfiles = cls.reading_bylines_small(input)
                for file in tempfiles:
                    if file[-len(extension):] == extension:
                        if os.path.exists(file):
                            files.append(file)
                        else:
                            print("The file do not exist", file)
                            sys.exit(1)

        return files

    @classmethod
    def reading_bylines_small(cls, filepath):
        """
        Will return a list where every element is a line. Very basic and can only be done on small files
        :param filepath: The file to be read
        :return: The list to be returned
        """
        with open(filepath, 'r') as fileread:
            lines = fileread.readlines()
        lines = [line.strip("\n") for line in lines]
        return lines

    @classmethod
    def filenamewithoutextension_checking_zipped(cls, filepath):
        """
        As the name suggest it is like filename without extension but it will check if the file is zipped (end with gz) and
        then run it twice to remove double extension. name.vcf.gz/name.vcf will give name
        :param filepath: the whole path of the file
        :return: will return the name with out the extension
        """
        filename = cls.filenamewithoutextension(filepath)
        if filepath[-2:] == 'gz':
            filename = cls.filenamewithoutextension(filename)
        return filename

    @classmethod
    def filenamewithoutextension(cls, filepath):
        """
        As the name sugges it will remove the file extension from the full filename. Addtionally if its in a path it will
        remove the path as well. IF it has multiple dot will only remove the first one (i.e. bla.vcf.gz will give bla.vcf)
        :param filepath: The file path
        :return: will give only file name without extension.
        """
        filename = cls.gettingfilename(filepath)
        extension = cls.gettingextension(filepath)
        if len(extension) > 0:
            return filename[:-(len(extension) + 1)]
        else:
            return filename

    @classmethod
    def gettingextension(cls, filepath):
        """
        As the name suggest from the filepath it will give the file extension. Remember if the filename do not have dot (.)
        it will give back the whole filename
        :param filepath: The whole file path of the file whose extension we wanted to get
        :return:the extension itself
        """
        import re
        filename = cls.gettingfilename(filepath)
        if re.search(".", filename):
            splitfilename = filename.split(".")
            return splitfilename[len(splitfilename) - 1]
        else:
            return ""


def creatingfolders(specificfolder: str) -> str:
    """
    As the name suggest it will create a folder if the folder do not exist. As simple as that. it will also check if
    the end is '/' as important to work later. it will return the folder it created

    :param specificfolder: The folder needs to be created
    :return: will not return anything. Either it will create if the folder do not exist or not return anything
    """
    import os
    if specificfolder != '':
        if specificfolder[-1] != '/':
            specificfolder = specificfolder + '/'

        specificfolder = os.path.expanduser(specificfolder)
        if not os.path.exists(specificfolder):
            os.makedirs(specificfolder)
    return specificfolder

def writing_bylines4mlist(mylist, output='out.txt'):
    with open(output, 'w') as f:
        for item in mylist:
            f.write("%s\n" % item)
    return output
