
# Overview 
This document outlines the data management and release policy for the clinical research unit (CRU) “CATCH ALL – towards a cure for all adults and children with Acute Lymphoblastic Leukemia (ALL)”. The goal of this document is to provide instructions on how data is to be stored, described, accessed and disseminated.  
Within this document, the term “data” is primarily used to refer to patient data  as well as their corresponding sequencing data (both genome and RNA level) generated as part of research projects within the CRU. Additional data types may be adequately covered by the general instructions below. If existing rules seem unsuitable for a given type of data, amendments to this document under Section 3 shall be made in dialogue with the INF project.   
# Roles and responsibilities 
The following roles and associated responsibilities are currently defined: 
## Medical faculty/IMIS at Kiel University
The Medical Faculty, and therein the Institute for Medical Informatics and Statistics (IMIS), at Kiel University provides the IT infrastructure required for the CRC data management. This data management system is referred to as “medFDM”.  
The IMIS ensures that services are maintained and expanded as required by “CATCH-ALL”.   
## CATCH-ALL INF project
The INF project is responsible for implementing data life cycles and workflows. Most of the “primary” data will be handled by the INF project and processed according to the guidelines outlined in the present data policy (Section 3 and 4). 
## Data producers / PIs
Principal investigators within the CRU are responsible for communicating their data generation plans to the INF project to ensure that all data can be captured in the data management system of the CRU.  
The INF project, where possible, shall be designated a data recipient for all sequencing projects. 
PIs must ensure that metadata is captured prior to e.g. sequencing and passed on to the INF project. The INF project can provide appropriate forms for standard applications.  
The choice of metadata to include lies (primarily) with the data producers but shall be in accordance with “FAIR” principles (i.e. third parties must be able to (re-)use the data given the annotated metadata). 
## All users
All users of the data management system must comply with data access and release policies outlined in Section 4. 
# Storage and annotation 
## iRODS archive storage
All raw (sequencing) data (both genome and RNA) generated within the CRU (i.e. financed through CRU funds) must be deposited in the data management solution medFDM.  
If sequencing is not coordinated with the INF project for automatic data delivery/archiving, it is the users’ responsibility to ensure that data is deposited with all relevant metadata (Section 3.2). 
Analytical results based on these raw data may be submitted to the data management system, together with a description on how this information was generated. For further details regarding data types, see Section 3.    
Data not generated as part of the CRUs’ activities must not be deposited  in the “medFDM” system, unless specifically authorised by the INF project.  
Individual data sets consisting of multiple files should be combined into one “tar” archive and uploaded as a single object. A thusly created tar archive shall represent a given state within the research project (e.g. raw data or analytical results). Different data stages may not be mixed into one tar object (e.g. data and results) but should reference each other via metadata keys.  
Data shall be deposited in the iRODS folder of the corresponding research project the data was generated for.  
Data access shall be set in accordance with guidelines described under Section 4.  
Data will be stored within the “medFDM” system for the lifetime of the CRU, but at minimum 3 years from initial submission into the system.  
Storage beyond this time should be sought through publication to international data repositories (Section 4.2).   
## Metadata annotation
All data submitted to the data management system must be annotated with relevant metadata to enable data discovery across projects within the CRU, help with submission to downstream repositories and enable third parties to reuse the data at a later point. The current metadata standard you can [here](https://github.com/ikmb/catch-all/blob/main/metadata/1.0/metadata.md).  
These specifications are based on the [EBI MIxS standard](http://www.ebi.ac.uk/ena/submit/mixs-checklists). Metadata keys not covered by this specification should be used only after consulting with the INF project so they can be added to the metadata vocabulary.  
## Clinical data
Clinical (patient) data will be managed by the Z1 project. All digital data subject to this data policy shall be anonymised and include no metadata directly enabling identification of individuals. Specifically, no identifying information, such as a patient ID or name, shall be stored.  Connecting clinical data with digital/omics data shall only be possible by the Z1 project - using information about the relationship of probant identities (Z1) and e.g., sequencing library identifiers (INF). All data will be stored securely in the medFDM system, which employs controlled access policies to prevent unauthorised access. 
## cBioPortal
Select bioinformatic analyses will be uploaded to cBioportal into existing patient profiles (created/provided by Z1/Z2). cBioportal can be securely accessed from within the clinical network and serves as a graphical interface within the context of a molecular tumour board (MTB). Only clinicians  who are part of the MTB can access the data. 
# Data types 
 ## Short read files (fastq or ORA)
Short reads generated on e.g. the Illumina platform of machines are the primary data type within the CRU.  
Short reads shall be deposited within the medFDM in their raw form (no trimming, no filtering), with their original file name as given by the sequencing provider intact.  
For efficient usage of the storage system, read files shall be compressed using one of two algorithms. If possible, the Illumina ORA format shall be used. Instructions for this will be provided separately by the INF project. If ORA compression is not available, the GZIP algorithm shall be used - following the naming convention “.fastq.gz”. 
Compressed raw data must be accompanied by an md5sum to enable data integrity checks.  
Where multiple read files belong to one sample (i.e. paired-end reads), the compressed files shall be grouped into one tar archive. The tar archive shall be named after the sequencing library (usually the common root of the filenames to be grouped).  
The tar archive shall contain the corresponding fastqc statistics (one statistics file per sequence file).  
## Analytical results (generic) 
Finalised analyses (tabular counts or similar) may only be stored in the “medFDM” if the analysis process is included with the data so that any user may be able to accurately reproduce the workflow. Analysis and the “analysis trace” shall be submitted together as tar archive and must be annotated with appropriate metadata. Specifically, it must be clear which raw data was used in the analysis by reference to the sample or library name(s) within “medFDM".  
The format of the analytical result must be discussed with the INF project prior to submission to help identify common standards and develop best practices.  
# Access and release 
## Data sharing within the CATCH-ALL
Data and metadata from the individual projects shall be readable by all CRU members to aid in data discovery.  
Data shall only be writable by members of the respective projects (the data owner).  
Data belongs to the user it was generated for, as indicated by the mandatory metadata key “MAIN\_CONTACT\_NAME”.  
Any use of the data prior to its publication needs permission by the owner.   
## Release of data into the public domain
Data generated within the CRU shall be made available to the public upon publication.  
Data shall be published through upload into suitable, widely accepted repositories (e.g. NCBI or EBI archives).  
Data published to international repositories shall be annotated within the CRC iRODS using the resulting digital object identifier (DOI) in the remote database, if possible/applicable.  
# Revision history 
Draft 1 generated in January 2023. 
Release 0.1 generated in .  
