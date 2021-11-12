#!/usr/bin/env python

import os
import sys
import yaml
import json
import yaxil
import shutil
import logging
import argparse as ap
from urllib.parse import urlparse
from mrverify.report import Report
from mrverify.scanner.siemens.skyra import Skyra
from mrverify.scanner.siemens.prisma import Prisma
from mrverify.notifications.email import Mailer

logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.ERROR)

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('-l', '--label', required=True)
    parser.add_argument('-p', '--project')
    parser.add_argument('-n', '--notify', action='store_true')
    parser.add_argument('-a', '--xnat-alias')
    parser.add_argument('--xnat-host')
    parser.add_argument('--xnat-user')
    parser.add_argument('--xnat-pass')
    parser.add_argument('--keep-cache', action='store_true')
    parser.add_argument('--cache-dir', default='~/.cache/mrverify')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    with open(args.config) as fo:
        config = yaml.load(fo, Loader=yaml.FullLoader)

    auth = yaxil.auth2(args.xnat_alias)
    hostname = urlparse(auth.url).netloc
    logger.info(f'xnat hostname is {hostname}')
    args.cache_dir = os.path.expanduser(args.cache_dir)
    cache_dir = os.path.join(args.cache_dir, hostname)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    report = Report()
    logger.info('querying for experiment from xnat')
    experiment = next(yaxil.experiments(auth, label=args.label, project=args.project))
    logger.info('querying for scans from xnat')
    for scan in yaxil.scans(auth, experiment=experiment):
        scan_id = scan['id']
        scanner_model = scan['scanner_model']
        series_description = scan['series_description']
        if Prisma.check_model(scanner_model):
          checker = Prisma(config)
        elif Skyra.check_model(scanner_model):
          checker = Skyra(config)
        else:
          logger.warning(f'no checker matched scan={scan_id}, model={scanner_model}')
          continue
        if not checker.needs_checking(scan):
            continue
        logger.info('checking scan %s (%s)', scan['id'], series_description)
        project = scan['session_project']
        session = scan['session_label']
        subject = scan['subject_label']
        accession_id = scan['session_id']
        scan_id = scan['id']
        basename = f'{project}_{session}_{scan_id}'
        dicom_dir = os.path.join(cache_dir, basename)
        if not os.path.exists(dicom_dir):
            logger.info(f'downloading scan data to {dicom_dir}')
            yaxil.download(auth, session, [scan_id], out_dir=dicom_dir)
        else:
            logger.info(f'found cached copy {dicom_dir}')
        checker.check_dir(dicom_dir)
        if not args.keep_cache:
            shutil.rmtree(dicom_dir)
        report.add(scan, checker)
    meta = {
        'project': project,
        'subject': subject,
        'session': session
    }
    report.add_meta(meta)
    saveas = f'{experiment.label}.html'
    logger.info(f'saving {saveas}')
    report.generate_html(saveto=saveas)
    if report.has_errors and args.notify:
        logger.info('report has errors, sending notification')
        notifier = Mailer(config)
        notifier.add_meta(meta)
        notifier.add_report(saveas)
        notifier.send()

if __name__ == '__main__':
    main()
