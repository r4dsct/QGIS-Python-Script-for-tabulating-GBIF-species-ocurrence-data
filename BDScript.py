# Description:
# This script tabulates species ocurrences and calculate frequencies contained in a spatial data layer for a particular
########################################################################################3
# zone. The species ocurrence should be in ESRI shapefile format. To use other formats you should be able to easily 
# modify the script. The spatial data defining the zones should also be on a ESRI shapefile format.

# In the species ocurrence layer, each feature should have full taxonomic information: kingdom, phylum, class, order, family, genus, species, and full scientific name

# In the zonal layer, each feature should have a name/unique code stored in an attribute.

#The script was designed to run QGIS in QGIS 2.18 / Python 2.7. The script should be run from within the QGIS python console.



#Instructions:
# To properly run this script, you should only modify the "Input parameters", everything else remaining the same.


# Expected outputs:
# This script will do the following:
# Three folders: One with the individual zonal features. Another folder with the individual species ocurrence features 
# for each zone. A third folder containing csv files with the tabulated species ocurrence data. 
# Create a field in the zonal data with a simplified name of the zonal feature. Non-ASCII characters are removed
 



###1. Input Parameters. This is the only section of the script that you should modify. Current values are provided so you see the format of the input

##Defining the folders and directories
main_directory = "C:/Users/sebas/Documents/Antioch2017/BiodiversityMap/Python2017/TestData"     #path to directory containing layers


# Information on the Zone layer
intersect_shpname = "PCSelect.shp"  #Layer to be used as and intersect

inter_fieldname = "NAME_0"      #name of field with the intersect layer's name


# Information on the point layer containing taxonomic data
bd_shpname= "HNBSelect.shp"     #Name of the the biodiversity layer
bd_sciencenamefieldname =  "scientific"       #name of the field containing the species name
bd_specfieldname =  "species"       #name of the field containing the species name
bd_genusfieldname =  "genus"        #name of the field containing the species nam
bd_famifieldname = "family"         #name of the field containing the the specie's family
bd_orderfieldname = "order_"        #name of the field containing the specie's order
bd_classfieldname = "class"         #name of the field containing the specie's class

bd_phylumfieldname= "phylum"        #name of the field containing the specie's phylum

bd_kingdomfieldname = "kingdom"     #name of the field containing the specie's kingdom


#IUCN data
csv_name ="IUCNRedList.csv"

csv_namelong ='file:///'+ main_directory + '/'+csv_name+'?delimiter=,'




#Data provider information
labtype  = "ogr"       #data provider. OGR is for shapefiles


# Importing necessary modules. You 
from qgis.core import QgsProject
from PyQt4.QtCore import QFileInfo
from PyQt4.QtCore import QVariant
import processing
import os
import unicodecsv as csv



### 2 Loading the zone layer in memory and the layer panel in QGIS 

inter_shpmemory = iface.addVectorLayer(main_directory + "/" + intersect_shpname,"Zone layer",labtype)


if not inter_shpmemory:
    print "Layer failed to load"


# 2 Adding a field with a simplified name of the layer. This to reduce the length and remove non-ASCII characters that might iterfere with proper names of a shapefile



# First creates a function to modify the zone feature's name

def prepares_names(your_string):
    
    import re
    
    some_string = re.sub(r'\W+', '', your_string)    
    
    if len(some_string) > 25:
        final_string = some_string[:25]
        return final_string
    else: 
        final_string = some_string
        return final_string




###Adds a field to the zone layer
caps = inter_shpmemory.dataProvider().capabilities()

if caps & QgsVectorDataProvider.AddAttributes:
    res = inter_shpmemory.dataProvider().addAttributes([QgsField("simp_name",QVariant.String)])



### updating the value of the new field
    
inter_shpmemory.startEditing()
features = inter_shpmemory.getFeatures()

for feat in features:
    print(prepares_names(feat['NAME_0']))
    
    inter_shpmemory.changeAttributeValue(feat.id(), inter_shpmemory.fieldNameIndex("simp_name"),prepares_names(feat['NAME_0']))
   
inter_shpmemory.commitChanges()
inter_shpmemory.updateFields()




### 3 the GBIF data to the memory and layer panel

specieslayer_mem = iface.addVectorLayer(main_directory + "/" + bd_shpname,"GBIF layer",labtype)
QgsMapLayerRegistry.instance().addMapLayer(specieslayer_mem)



# Joining the IUCN layer

UICNcsv = QgsVectorLayer(csv_namelong, 'UICN Red list', 'delimitedtext')

QgsMapLayerRegistry.instance().addMapLayer(UICNcsv)



###produces the join

shpField='species'
csvField='species_full'
joinObject = QgsVectorJoinInfo()
joinObject.joinLayerId = UICNcsv.id()
joinObject.joinFieldName = csvField
joinObject.targetFieldName = shpField
joinObject.memoryCache = True
specieslayer_mem.addJoin(joinObject)

print([field.name() for field in specieslayer_mem.pendingFields() ])

### 4 Create folders to safe all stuff. If the 
newfolder_zones = main_directory + "/" + "Zonal_GBIF"
newfolder_bd = main_directory + "/" + "GBIF_Ocurrences"
newfolder_tables = main_directory + "/" + "GBIF_TablesbyZones"

if not os.path.exists(newfolder_zones) or not os.path.exists(newfolder_bd):
    os.makedirs(newfolder_bd)
    os.makedirs(newfolder_zones)
    

if not os.path.exists(newfolder_tables):
    os.makedirs(newfolder_tables)


### 5 Clipping the GBIF point data using the zones. In QGIS its hard to use selected layers in the processing alg. Therefore you have to select zone layer and save it into a new .shp.

#Iterator over features
features = inter_shpmemory.getFeatures()

#Creates a list that will contain the names of the zone layers
names_zonelayer = []


for feature in features:
    
    inter_shpmemory.setSelectedFeatures([feature.id()])
    QgsVectorFileWriter.writeAsVectorFormat(inter_shpmemory,newfolder_zones + '\\' + feature['simp_name'] +'.shp',"utf-8",None,"ESRI Shapefile", True)

    zone_iter = iface.addVectorLayer(newfolder_zones + '\\' + feature['simp_name'] +'.shp',"Zone iteration",labtype)

    processing.runalg('qgis:clip', specieslayer_mem, zone_iter, newfolder_bd + '\\' + feature['simp_name'] +'BDD.shp')  
    
    inter_shpmemory.setSelectedFeatures([])

    QgsMapLayerRegistry.instance().removeMapLayer(zone_iter.id())

    names_zonelayer.append(feature['simp_name']+'BDD.shp')
    



### Creates a tabulated list with taxonomic information and number of ocurrences. Than it saves it into a unicode-enabled CSV. Therefore when you open it in a spreadsheet program, choose the encoding at "UTF-8".
    
for bdzonesnames in names_zonelayer:
    bdzone = QgsVectorLayer(newfolder_bd + "/" + bdzonesnames,"Zone layer",labtype)
    features = bdzone.getFeatures()
    bdz = []
    table_name= newfolder_tables+"/"+bdzonesnames[0:len(bdzonesnames)-7]+'.csv'
    
    for feature in features:
        species_order = feature[bd_specfieldname]
        #print(species_order)
        
        if not bdz:
            bdz.append([feature[bd_kingdomfieldname],feature[bd_phylumfieldname],feature[bd_classfieldname],feature[bd_orderfieldname],feature[bd_famifieldname],feature[bd_genusfieldname], feature[bd_specfieldname],feature[bd_sciencenamefieldname], feature['UICN Red17'], 1])
                 
        spe_list = [item[6] for item in bdz]
        
        
        if species_order in spe_list:
            ind_sp = spe_list.index(species_order)
            nums = bdz[ind_sp][9]
            bdz[ind_sp][9] = nums+1
        else:
            bdz.append([feature[bd_kingdomfieldname],feature[bd_phylumfieldname],feature[bd_classfieldname],feature[bd_orderfieldname],feature[bd_famifieldname],feature[bd_genusfieldname], feature[bd_specfieldname],feature[bd_sciencenamefieldname], feature['UICN Red17'] , 1])
                
    bdz =  [['Kingdom', 'Phylum', 'Class','Orden', 'Family', 'Genus', 'Species', 'Scientific name', 'IUCN status','Count']]+ bdz[0:len(bdz)]
    
    with open(table_name, 'wb') as csvfile:
        a= csv.writer(csvfile,delimiter=',',encoding ='utf-8')  
        a.writerows(bdz)    
            
    
    

    
    
        