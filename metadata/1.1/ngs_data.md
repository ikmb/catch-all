![](../../images/logo.png)
# NGS Metadata standard, v1.1

## Sample sheet

NGS Metadata sample sheet [XLSX](CATCH-ALL_NGS_raw_data_1.1.xlsx)

### Submitter_Information
This tab will have the information of the person who has submitted the data for sequencing. It will also have the 
information on the color legend present in the Metadata tab.

### Project Info
This tab will have a short description on the project.

| Key            | Description                                                                                                                  |
|----------------|------------------------------------------------------------------------------------------------------------------------------|
| Title          | An appropriate human readable title of the project                                                                           |
| Key word(s)    | Key words so that it can be easily searchable in the yoda system                                                             |
| Short abstract | A short abstract about the project so that later if somebody reads the irods folder they can understand the context easily.  |

## Metadata
Main tab of the file. The row is input method of the column (for example string, integer, float etc). It is color coded. 
In case red the column is mandatory. Next row is the header (as presented as the key here). All the other rows are the 
information about the samples. 

## Descriptions 
A small description of the metadata keys in case it is not clear only by the name. 

| Key                                        | Description                                                                                                                                                 |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| library_id                                 | Unique identifier of a sequencing library. Usually, this will be part of the name of a sequence file.                                                       |
| sample_barcode                             | NGS Barcode of sample                                                                                                                                       |
| project_name                               | Name of a project                                                                                                                                           |
| external_id                                | An external ID linking to this data from another source, like an in-house database or public repository. To be used in combination with external_id_source. |
| external_id_source                         | Specifies the source an external id points to. This can be an in-house repository or a public database.                                                     |
| sample_name                                | Unique name or identifier of a biological sample.                                                                                                           |
| tax_id                                     | NCBI Taxon ID, such as 9606 for human or 10090 for mouse.                                                                                                   |
| scientific_name                            | Scientific species name                                                                                                                                     |
| common_name                                | Common species name                                                                                                                                         |
| collection_date                            | Date sample was collected                                                                                                                                   |
| phenotype                                  | Phenotype(s) as HPO terms                                                                                                                                   |
| experimental_factor                        | A specific experimental factor that was applied to this sample (e.g. low-calory diet)                                                                       |
| sample_volume_or_weight_for_dna_extraction | Total sample volume (ml) or weight (g) processed for DNA extraction                                                                                         |
| sample_alias                               | Alias name of a sample                                                                                                                                      |
| sample_sex                                 | Sex of a sample/individual                                                                                                                                  |
| sample_material_processing                 | Processing that was performed on sample                                                                                                                     |
| sample_collecting_device_or_method         | How a sample was collected                                                                                                                                  |
| source_material_identifier                 | Identifies a sample source material                                                                                                                         |
| sample_storage_duration                    | How long a sample was stored for in days                                                                                                                    |
| sample_storage_location                    | Location a sample was stored at                                                                                                                             |
| sample_storage_temperature                 | Temperature the sample was stored at                                                                                                                        |
| sample_description                         | Description of a sample                                                                                                                                     |
| library_construction_method                | Method or kit used for library construction                                                                                                                 |
| library_read_length                        | Length of sequence reads                                                                                                                                    |
| library_read_group_id                      | The unique read group ID of a set of reads.                                                                                                                 |
| flowcell_id                                | ID of flow cell                                                                                                                                             |
| flowcell_lane                              | Lane on flow cell                                                                                                                                           |
| nucleic_acid_extraction                    | Protocol used to extract DNA/RNA                                                                                                                            |
| nucleic_acid_amplification                 | Amplification protocol used, if any                                                                                                                         |
| library_sample_type                        | Sample type library was constructed from                                                                                                                    |
| library_screening_strategy                 | Strategy used to screen library                                                                                                                             |
| library_size                               | Size of library in bp                                                                                                                                       |
| library_vector                             | Vector used for library construction, if any                                                                                                                |
| sequencing_centre                          | Centre were sequencing was performed                                                                                                                        |
| sequencing_date                            | Date sequencing was performed                                                                                                                               |
| sequencing_method                          | Name of the sequencing technology (e.g. Illumina short-read sequencing)                                                                                     |
| sequencing_platform                        | Sequencing instrument                                                                                                                                       |
| library_reads_sequenced                    | Number of reads sequenced                                                                                                                                   |
| miscellaneous_parameter                    | further descriptions, if needed                                                                                                                             |
| investigation_type                         | Type of investigation performed                                                                                                                             |
| relevant_standard_operating_procedures     | Standard operating procedures used for data production                                                                                                      |
| comment                                    | A comment about the data                                                                                                                                    |

### Validation
This is for the prefilled values for certain columns. This table would have the information what are those prefilled 
drop down menu can have. For example: 
sequencing platform column can have values 

| sequencing platform |
|---------------------|
| NovaSeq 6000        |
| Sequel IIe          |
| Revio               |
| ....                |

for drop down menu. This information will be saved in the Validation tab. 