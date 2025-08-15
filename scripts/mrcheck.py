#!/usr/bin/env python

import sys
import json
import yaxil
import logging
import mrverify
import requests_cache
import argparse as ap
from pathlib import Path
from urllib.parse import urlparse
from mrverify.config import Config
from mrverify.report import Report
from mrverify.validator import Validator
from mrverify.notifications.gmail import Notifier

logger = logging.getLogger('mrcheck')

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('-c', '--configs-dir', type=Path, required=True)
    parser.add_argument('-l', '--label', required=True)
    parser.add_argument('-p', '--project')
    parser.add_argument('-n', '--notify', action='store_true')
    parser.add_argument('-a', '--xnat-alias')
    parser.add_argument('-o', '--output-file', type=Path)
    parser.add_argument('--xnat-host')
    parser.add_argument('--xnat-user')
    parser.add_argument('--xnat-pass')
    parser.add_argument('--keep-cache', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    requests_cache.install_cache('xnat')

    auth = yaxil.auth2(args.xnat_alias)
    hostname = urlparse(auth.url).netloc
    logger.info(f'xnat hostname is {hostname}')

    report = Report()
    logger.info('querying for experiment from xnat')
    experiment = next(yaxil.experiments(auth, label=args.label, project=args.project))
    logger.info('querying for scans from xnat')

    logger.info('getting scanner details')
    scanner = mrverify.get_scanner_details(auth, experiment)
    logger.info(f'scanner details: {scanner}')

    # load configuration file for scanner
    conf = Config.load(
        args.configs_dir,
        scanner
    )

    cache_dir = conf.query('$.Storage.cache_dir')
    cache_dir = Path(cache_dir, hostname).expanduser()

    logger.info(f'requesting complete scan listing for {experiment.label}')
    scans = list(mrverify.scans(auth, experiment))

    for verify in conf.query('$.Verification'):
        required = verify.get('required', False)
        filter = verify.get('filter')
        params = verify.get('params')
        logger.info(f'looking for a match on {filter}')
        for scan in mrverify.match(filter, scans):
            series = scan.series_number
            logger.info(f'found matching scan {series}')
            validator = Validator()
            validator.validate(scan, params)
            report.add(scan, validator)

    meta = {
        'project': experiment.project,
        'subject': experiment.subject_label,
        'session': experiment.label
    }
    report.add_meta(meta)
    saveas = Path(f'{experiment.label}.html')
    if args.output_file:
        saveas = args.output_file.expanduser()
    logger.info(f'saving {saveas}')
    report.generate_html(saveto=saveas)
    if report.has_errors and args.notify:
        logger.info('report has errors, sending notification')
        notifier = Notifier(conf)
        notifier.add_meta(meta)
        notifier.add_report(saveas)
        notifier.send()

if __name__ == '__main__':
    main()
