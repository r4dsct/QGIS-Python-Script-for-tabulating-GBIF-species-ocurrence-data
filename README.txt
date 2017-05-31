The BDScript is QGIS Python code to extract and summarize geocoded Global Biodiversity Information Facility (GBIF) species ocurrence data for a set 
of zonal spatial features. For example, say you created a point spatial layer with the location of species occurrences. You also have a layer with
zonal data, such as protected areas. This script will extract the GBIF species occurrence data for each of the features (polygons) of the zonal data
and summarize the taxonomic information. In summary, this script will:

- Using a spatial intersect, create individual files (shapefiles) for the zonal data
- Individual files (shapefiles) for the GBIF species occurrence data
- Individual tables (CSV format) with full taxonomic records, frequecies and IUCN status for each zonal feature




Intructions 

Data requirments:

1) All input data must be in a shapefile format. 
2) The GBIF layer should have full taxonomic records: species, genus, family, order, class, phylum and kingdom
3) The zonal layer should have a field in the attribute table that include unique names for each feature.
4) Copy the script and your input data in the same directory. This will be your main directory.
5) Once you download the script, you have to open the BDScript.py and modify the first section. 
6) The TestData.zip contains the IUCNRedList.csv table. You need to extract it and paste it in your working directory. Otherwise the script won't work. 
5) When you are ready to run the script, do it from the within the QGIS Python console. 


Additional notes:

At this point the script does not include error handling capabilities.


