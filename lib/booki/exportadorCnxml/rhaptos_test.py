import requests
from string import Template
import zipfile
import os


def create_metadata(metadata):
  xml = """<?xml version="1.0"?>
  <entry xmlns="http://www.w3.org/2005/Atom"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:oerdc="http://cnx.org/aboutus/technology/schemas/oerdc">

      <!-- The atom title, author, and summary are informational and will not be used to populate the module. They can be left out. -->
      <title>$title</title>
      <author><name>$author</name></author>
      <summary type="text">$summary</summary>

      <!-- The metadata below is used to initialize the module -->
      <dcterms:title>$title</dcterms:title>
      <dcterms:abstract>$summary</dcterms:abstract>
      <dcterms:creator oerdc:id="$username"></dcterms:creator> 
      <oerdc:maintainer oerdc:id="$username" /> 
      <dcterms:rightsHolder oerdc:id="$username" />

      <oerdc:oer-subject>$subject</oerdc:oer-subject>  <!-- Vocabulary-controlled Connexions specific subject categorization -->
      <!-- <dcterms:subject>php</dcterms:subject> Unconstrained author-supplied keywords <md:keyword> 
      <dcterms:subject>avanzado</dcterms:subject> -->
      <dcterms:language xsi:type="ISO639-1">$language</dcterms:language>
      <oerdc:analyticsCode>UA-4688042-1</oerdc:analyticsCode>
  </entry>
  """

  template = Template(xml)
  mets =  template.safe_substitute(metadata)
  return mets

def upload_to_rhaptos(server,zip_file, metadata):
  username = metadata['username']
  password = metadata['password']
  file_zip = open(zip_file, 'rb')
  filezip_content = file_zip.read()
  headers_zip = {'Content-type': 'application/zip', 'In-Progress': 'true'}
  resp = requests.post(server, data=filezip_content, auth=(username, password), headers=headers_zip)
  print(resp.status_code)
  if resp.status_code == 201:
    resource_url = resp.headers['location']
    filexml_content = create_metadata(metadata)
    print(filexml_content)
    headers_xml = {'Content-type': 'application/atom+xml;type=entry', 'In-Progress': 'true'}
    resp_xml = requests.post(resource_url, data=filexml_content, auth=(username, password), headers=headers_xml)
    print(resp_xml.status_code)
    
    if resp_xml.status_code == 200:
      print "Subido a rhaptos exitosamene"
    else:
      print "Problema al subir los metadatos"
  else:
    print "No se pudo subir el zip"


def zip_directory(directory):
  zf = zipfile.ZipFile("upload.zip", "w")
  for dirname, subdirs, files in os.walk(directory):
      for filename in files:
          print os.path.join(dirname, filename)
          zf.write(os.path.join(dirname, filename))
  zf.close()


def zip_and_updload_files(server, directory, metadata):

  zip_directory(directory)
  upload_to_rhaptos(server, "upload.zip", metadata)




