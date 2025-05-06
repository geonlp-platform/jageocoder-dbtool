# jageocoder-dbcreator

日本語の説明は [README(日本語版)](README_ja.md)
を参照してください。

# About this software
Jageocoder-dbtool (this software) is software that creates an address database for [Jageocoder](https://jageocoder.info-proto.com/) from map data.

## Target users
If you want to analyze general addresses or obtain corresponding longitude and latitude, you do not need to use this software to create an address database.
Ready-made address databases are available for download at [Jageocoder Data File List](https://www.info-proto.com/static/jageocoder/latest/).

The distributed data files are created from open data published by national agencies, so they might not be as accurate or comprehensive as commercially available map data.
If you have commercial map data or map data that you have created through your own research and want to create an address database corresponding to that map, please use this software.
 
## Target operating environment
To run this software, you need an environment that supports Python 3.10, 3.11, or 3.12. It does not currently work with 3.13 or later.
It has been tested on Windows Command Prompt, various Linux distributions, and macOS.

## Target Map Data
This software creates an address database for Jageocoder from map data in the GeoJSON format (https://geojson.org/).
If the map data you wish to use is not in GeoJSON format, please use GIS software such as [QGIS](https://qgis.org/) to import the map data and export it in GeoJSON format.

There are various types of GeoJSON data, but this software supports "lists of Features with Point, Polygon, or Multipolygon as geometry" (JSONL format files containing one object per line) or "FeatureCollections with Point, Polygon, or Multipolygon as geometry." Data with LineString geometry (e.g., road data) cannot be used. 
The coordinate reference system for GeoJSON data must be WGS84 (RFC7946), and the character encoding must be UTF-8 (RFC8259). If the map data you wish to use has a different coordinate reference system or character encoding, please convert it using GIS software or another method.

# Installation procedure

## Creating a Python 3.x virtual environment
If you are unsure how to install Python 3.x or create a virtual environment, please refer to the website or other resources. This document does not cover how to create a Python environment. The Python versions that this software runs on are 3.10, 3.11, and 3.12.

## Installing this software
This software can be downloaded and installed from [PyPI](https://pypi.org/), the official Python software repository. With the virtual environment enabled, execute the following command.
```
(.venv) pip install jageocoder-dbtool
```
Once installed, you will be able to execute the "dbtool" command. When executed, a simple help message will be displayed.
> Please note that the package name to install is "jageocoder-(hyphen)dbtool" and the command to execute is "dbtool".
```
(.venv) dbtool
Usage:
  dbtool ( -h | --help )
  dbtool ( -v | --version )
  dbtool check [-d] [--output=<file>] [--codekey=<codekey>] [--code=<attrs>] [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  dbtool geojson2db [-d] [--text-dir=<dir>] [--db-dir=<dir>] [--id=<id>] [--title=<title>] [--url=<url>] [--codekey=<codekey>] [--code=<attrs>] [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  dbtool geojson2text [-d] --text-dir=<dir> [--id=<id>] [--title=<title>] [--url=<url>] [--codekey=<codekey>] [--code=<attrs>] [--pref=<attrs>] [--county=<attrs>] [--city=<attrs>] [--ward=<attrs>] [--oaza=<attrs>] [--aza=<attrs>] [--block=<attrs>] [--bld=<attrs>] <geojsonfile>...
  
dbtool text2db [-d] [--db-dir=<dir>] (--text-dir=<dir>|<textfile>...)
```

## Uninstalling this software
If you no longer wish to use this software, disable the virtual environment and delete the ".venv" directory.
On Linux and MacOSX, use "rm -r" to delete the directory and its contents.
```
(.venv) deactivate
rm -r .venv
```
On Windows cmd.com, use "rmdir /S" to delete the directory and its contents.
```
(.venv) deactivate
> rmdir /S .venv
```

# Command list
The following functions and commands are available in this software.
- "dbtool geojson2db ..."
  Creates a Jageocoder address database from map data in GeoJSON format (https://geojson.org/). 
- "dbtool check ..."
  Checks the parameters and conversion results when converting GeoJSON to address data. Outputs a Point-format GeoJSON (JSONL) file with the coordinates of representative points as geometry.
- "dbtool geojson2text ..."
  Creates text-format data for the Jageocoder address database from GeoJSON-format map data. "Text-format data" is equivalent to a database dump and cannot be used directly with Jageocoder, but with this text-format data, you can create an address database.
- "dbtool text2db ..."
  Creates an address database from the text-format data.
  By converting multiple text format data files into an address database, you can create an address database that supports unified search. 

# Address Level Assignment Options
The "geojson2db", "check", and "geojson2text" commands require you to assign attributes contained in GeoJSON map data to address elements such as prefectures and municipalities. This section explains the options used for address level assignment that are common to these commands.

Jageocoder manages addresses at the following levels:
1. Pref: Prefecture (e.g., "北海道")
2. County: District, branch office, or island (e.g., "幌泉郡", "八丈島")
3. City: Municipality or special ward (e.g., "室蘭市", "千代田区")
4. Ward: Ward of a designated city (e.g., "青葉区", "天王寺区")
5. Oaza: Large district (e.g., "市場町切幡")
6. Aza: Small district name (e.g., "字古田")
7. Block: Block number (e.g., "1番" or "201番地")
8. Bld: House number (e.g., "1号" or "24")
For example, Jageocoder devides the address of the Erimo Town Hall in Hokkaido, "北海道幌泉郡えりも町字本町206番地" into;
```
{"pref":"北海道", "county":"幌泉郡", "city":"えりも町", "oaza":"字本町", "block":"206番地"}
```
and the address of the Aoba Ward Office in Sendai City, Miyagi Prefecture, "宮城県仙台市青葉区国分町3丁目7番1号" into;
```
{"pref":"宮城県", "city":"仙台市", "ward":"青葉区", "oaza":"国分町", "aza":"3丁目", "block":"7番", "bld":"1号"}
```

There are no fixed rules for how to divide Japanese addresses or the name of the levels, so there are various ways of writing them depending on the map data. Therefore, in this software, you need to specify which attributes in the map data correspond to which address levels in Jageocoder using optional parameters. 

Specify optional parameters in the format "parameter name=attribute name". Prepend "--" to the parameter names listed above, such as "pref" or "county". For example, to map the "block" attribute in the map data to the "aza" level, use "--aza=block". 

If the attribute corresponding to the map data does not exist, the option can be omitted. For example, if the map data only covers Chiyoda Ward, attributes corresponding to "county" or "ward" may not exist. In such cases, do not specify "--county" or "--ward".
Attributes corresponding to prefectures or municipalities may also be omitted and not exist, but omitting "--pref" or "--city" will prevent addresses written as "東京都千代田区..." from being parsed. In such cases, specify the fixed values by placing two equal signs, like "--pref==東京都 --city==千代田区".

There may also be cases where attributes corresponding to map data exist but the suffix is omitted. For example, if there is an attribute named "chome" with only the number ‘1’ recorded, it must be registered as "1丁目" as an address element. In such cases where you want to append a string to the attribute value, you can replace the attribute value by enclosing the attribute name in "{}". To add the string "丁目" after the value of the "chome" attribute and assign it to the aza level, specify "--aza={chome}丁目". 

There may be multiple attributes corresponding to a specific address level in the map data. For example, if there are attributes "gaiku" and "chiban" and both need to be assigned to the block level, list the attribute names separated by commas. In this case, specify "--block=gaiku,chiban". Additionally, if "gaiku" and "chiban" only contain block codes or numbers, and you want to add "番" and "番地" respectively, specify "--block={gaiku}番,{chiban}番地".

Note that Jageocoder does not support address levels more detailed than "bld", such as apartment or condominium names.

# License

[The 2-Clause BSD License](https://licenses.opensource.jp/BSD-2-Clause/BSD-2-Clause.html)

# Acknowledgements

This software is supported by [Research and Development Promotion Project for DX in the Humanities and Social Sciences](https://codh.rois.ac.jp/dihuco/) 
and [ROIS-DS CODH (Center for Open Data in the Humanities)](http://codh.rois.ac.jp/).
