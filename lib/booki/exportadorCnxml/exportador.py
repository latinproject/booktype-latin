'''
Testing and development of HTML to CNXML transformation.

Transforms HTML files to CNXML.
Validates the result with Jing Relax NG.

CNXML results and media files are saved as .cnxml in OUTPUT_DIR.

Jing Relax NG validation results are saved as .log in OUTPUT_DIR.
If there is no error during validation the .log file has zero bytes.

Created on 13.09.2011

@author: Marvin Reimer

*****Modificado por Valeria Gerling y Sebastian Scandolo para el proyecto Latin Project - Agosto 2013******
'''

import sys
import glob
import os
import subprocess
import datetime
import socket
import zipfile
import shutil
from htmlsoup2cnxml import htmlsoup_to_cnxml

OUTPUT_DIR = "cnxml_output"
#PATH = "/home/gcarrillo/workspace/mybooktype/booktype-latin-gladys/lib/booki/exportadorCnxml/"
PATH = "/var/wwww/booktype-latin/booktype-latin/lib/booki/exportadorCnxml/"
# IN_DIR = "testbed_html"

# SE NECESITA QUE TENGA JAVA INSTALADO

# Borra el contenido de una carpeta
def delete_all_contents_of_folder(folder):
    if os.path.isdir(folder):
        for root, dirs, files in os.walk(folder):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

# Jing validation and save log file
def jing_validate_file(xml_filename, log_filename):
    # build the java commandline string
    jing_jar_filename = os.path.join('jing', 'jing.jar')
    jing_rng_filename = os.path.join('jing', 'cnxml-jing.rng')
    java_cmd = 'java -jar %s %s %s' % (jing_jar_filename, jing_rng_filename, xml_filename)
    # validate XML and save log file
    jing_log_file = open(log_filename, 'w')
    try:
        p = subprocess.Popen(java_cmd, shell=True, stdout=subprocess.PIPE)
        jing_log, error_data = p.communicate()
        if not error_data:
            jing_log_file.write(jing_log)
        else:
            jing_log_file.write(error_data)
    finally:
        jing_log_file.close()

# converts all matching files in testbed input folder to CNXML output folder
def convertir(chapter_html):

    os.chdir(PATH)
    print "estoy adentro de la funcion convertir"
    print os.getcwd()
    
    #borrar el contenido de la carpeta de salida
    delete_all_contents_of_folder(OUTPUT_DIR)

    # html_file = os.path.join(IN_DIR, 'chapter_45 mod.html')
    # html_file = open(html_file, 'rb')
    # try:
    #     html = html_file.read()

    # finally:
    #     html_file.close()

    # transform
    cnxml,objects,title = htmlsoup_to_cnxml(chapter_html, bDownloadImages=True)
        
    # write testbed images
    for image_filename, image in objects.iteritems():
        image_filename = os.path.join(OUTPUT_DIR, image_filename)
        image_file = open(image_filename, 'wb') # write binary, important!
        try:
            image_file.write(image)
            image_file.flush()
        finally:
            image_file.close()        

    # write testbed CNXML output
    cnxml_filename = os.path.join(OUTPUT_DIR, 'index.cnxml')
    cnxml_file = open(cnxml_filename, 'w')
    try:
        cnxml_file.write(cnxml)
        cnxml_file.flush()
    finally:
        cnxml_file.close()


    # validate CNXML output with Jing Relax NG (lo comento porque no hace falta)
    # if len(sys.argv) > 1 and sys.argv[1] == '-noval':
    #     print "Validation skipped"
    # else:
    #     print "Validating..."
    #     jing_log_filename = os.path.join(OUTPUT_DIR, 'salida.log')
    #     jing_validate_file(cnxml_filename, jing_log_filename)   


    print "Terminoooo"

if __name__ == "__main__":
    convertir(chapter_html)
