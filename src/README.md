# Scripts
This folder holds all the necessary scripts to handel  CATCH-ALL - data management repository.

## Getting started
### Installation
First clone the repository in your machine
```bash
git clone https://github.com/ikmb/catch-all.git
cd catch-all
```
Before running the codes (which is mainly written in python), you need to install some dependencies to run it properly.
Best way is use conda to solve the dependencies [anaconda](https://www.anaconda.com/distribution/). After installation
of conda
```shell script
conda env create -f src/requirements.yml 
conda activate catch-all
```
if you already have an environment and wants to update it
```shell script
conda env update -f src/requirements.yml
conda activate catch-all
```
### Running Commands
#### Fastq upload to irods
To upload fastq files from local to irods system you can use Submit.py

```shell script
python src/Submit_iRods.py --help
```
It will give necessary information how to upload the fastq files to the irods. 
One example of such upload
```shell script
python src/Submit_Metadata.py fastq <input.xlsx>  --ifolder /catchZone/home/upload/fastq
```