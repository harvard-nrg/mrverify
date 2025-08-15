import re
import sys
import yaxil
import pydicom
import logging
import requests
import warnings
from io import BytesIO
from pydicom.tag import Tag
from collections import namedtuple
from mrverify.dicom.mr import ImageCreator
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from nibabel.nicom import csareader

logger = logging.getLogger(__name__)

Scanner = namedtuple('Scanner', ['manufacturer', 'model', 'software', 'coil', 'dicom_format'])

def get_scanner_details(auth, experiment):
    for scan in scans(auth, experiment):
        return Scanner(
            squash(scan.manufacturer),
            squash(scan.manufacturer_model_name),
            squash(scan.software_versions),
            squash(scan.coil),
            scan.dicom_format
        )

def squash(s):
    s = re.sub(r'\s+', '_', s)
    return s.lower()

def match(filter, scans):
    for scan in scans:
        match = True
        for key,expected in iter(filter.items()):
            actual = scan.get(key, '')
            #logger.info(f'{scan.series_number} comparing actual={actual} equals expected={expected}')
            equality = actual == expected
            match = match and equality
        if match:
            yield scan

def scans(auth, experiment):
    for scan in yaxil.scans(auth, experiment=experiment):
        ds,count = fetch_dicom_file(auth, scan)
        image = ImageCreator(ds).create()
        image.num_files = count
        yield image

def fetch_dicom_file(auth, scan):
    baseurl = auth.url.rstrip('/')
    project = scan['session_project']
    subject = scan['subject_label']
    session = scan['session_label']
    scanid = scan['id']
    url = f'{baseurl}/data/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scanid}/files'
    r = requests.get(
        url,
        auth=yaxil.basicauth(auth),
        cookies=auth.cookie
    )
    if r.status_code != requests.codes.ok:
        raise ResponseError(f'response not ok ({r.status_code}) from {r.url}')
    js = r.json()
    files = js['ResultSet']['Result']
    path = files[0]['URI'].lstrip('/')
    r = requests.get(
        f'{baseurl}/{path}',
        auth=yaxil.basicauth(auth),
        cookies=auth.cookie
    )
    if r.status_code != requests.codes.ok:
        raise ResponseError(f'response not ok ({r.status_code}) from {r.url}')
    ds = pydicom.dcmread(BytesIO(r.content))
    return ds,len(files)

class ResponseError(Exception):
    pass
