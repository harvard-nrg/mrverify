Mr. Verify: Verify those scan parameters
========================================

Mr. Verify (or "MR verify") is a configurable command line tool to verify scan 
parameters within DICOM images, generate fancy HTML reports, and send notifications 
when there are verification issues.

# Table of contents

1. [Installation](#installation)
3. [Usage](#usage)
2. [Configuration files](#configuration-files)

# Installation

Just `pip`

```bash
python -m pip install mrverify
```

# Usage

Let's dissect the following command

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html
```

MR Verify will query the XNAT installation `xnat` for the MR Session 
with the label `AB1234C`. It will automatically detect acquisition 
details such as the scanner make, model, software version, and coil. 

Once MR Verify has resolved those details, it will attempt to load a 
configuration file for that specific environment. The configuration file 
includes all of the scans that should be checked, the scan parameters 
that should be checked, with their expected values.

# Configuration files

MR Verify will attmpe to load a configuration file based on acquisition 
site details such as the scanner make, model, software version, and coil. 

It will start by looking for a configuration file at the most specific 
location possible within the directory passed in via the `-c|--configs-dir` 
argument.

Let's dissect the following command

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html
```

Let's assuming session `AB124C` was captured on a Siemens Prisma scanner, 
running VE11B, and the scanner operator used a 32-channel head coil. MR Verify 
will begin by looking for a configuration file at the following location

```
configs
└── siemens
    └── prisma
        └── ve11b
            └── head_32
                └── mrverify.yaml
```

If a configuration file could not be found at this location, MR Verify will 
work its way back through the directory tree until it finds one.

This approach offers a great deal of flexibility, especially when suporting 
multi-site research studies that may need to support many unique combinations 
of scanner make, model, software version, and coil.

You can find example configuration files [here](https://github.com/harvard-nrg/mrverify/tree/main/example_configs).

