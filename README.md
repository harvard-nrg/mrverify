Mr. Verify: Verify those scan parameters
========================================

Mr. Verify (or "MR verify") is a configurable command line tool to verify MRI 
acquisition parameters read from DICOM images, generate fancy HTML reports, 
and send notifications when there are verification issues.

# Table of contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration files](#configuration-files)
4. [Operators](#operators)
5. [Notifications](#notifications)

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
details such as the MRI scanner make, model, software version, and 
receiver coil. 

Once MR Verify has resolved scan acquisition details, it will look for a 
parameter check configuration file for that specific type of environment
under the `./configs` directory. These configuration files should include 
all scans that should be checked, the acquisition parameters that should 
be checked, and their expected values. The generated report will be saved
to `output.html`.

# Configuration files

MR Verify will attempt to load a configuration file based on scan acquisition 
details including the MRI scanner make, model, software version, and receiver 
coil. 

It will look for a configuration file within the directory the user passed in 
via the `-c|--configs-dir` argument.

Let's take a closer look by dissecting the following command

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html
```

Let's assume session `AB124C` was captured on a Siemens Prisma scanner, running 
VE11B software, and the scanner operator used a 32-channel head coil. MR Verify 
will begin by looking for a configuration file at the following location

```console
./configs
└── siemens
    └── prisma
        └── ve11b
            └── head_32
                └── mrverify.yaml
```

If a configuration file could not be found at that location, MR Verify will 
proceed by working its way back through the directory tree until it finds one.

For multisite studies, it is not unusual for a data collection site to only 
have access to a 64-channel head coil which may require subtle changes to the 
scanning protocol, leading to different MR Verify configuration files

```console
./configs
└── siemens
    └── prisma
        └── ve11b
            ├── head_32
            │   └── mrverify.yaml
            └── headneck_64
                └── mrverify.yaml
```

On the other hand, perhaps the use of anything other than a 32-channel head 
coil is a mistake. In that case, you may choose to specify a configuration file 
at the software version level that checks the head coil that was used

```console
./configs
└── siemens
    └── prisma
        └── ve11b
            └── mrverify.yaml
```

You can find example configuration files [here](https://github.com/harvard-nrg/mrverify/tree/main/example_configs).

# Operators

Fundamentally, MR Verify checks that acquisition parameters match _expected 
values_ that are specified within a customizable configuration file. 

Most of these "expected values" are expressed as simple scalar values, or 
a list of scalars, which boils down to a simple equality check

```yaml
echo_time: 1.83
repetition_time: 8000
pixel_spacing: [4, 4]
coil_elements: HC1-7;NC1
```

However, MR Verify includes a few other ways to express expected values.

## regular expression 

Expected values may need to be expressed as a _regular expression_

```yaml
orientation_string: regex(Sag>.*)
``` 

## range

Expected values may need to be expressed as a _range_ of values

```yaml
abs_table_position: range(-1275, -1225)
```

# Notifications

Passing the `-n|--notify` argument to MR Verify will send an email 
notification including the generated HTML report to chosen recipients

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html -n
```

Some recipients may only want to be notified when a parameter check fails.
Others may want to receive reports that pass _or_ fail. Within each 
`mrverify.yaml` configuration file, you're able to specify recipients for 
reports that `pass`, `fail`, or both.

You can find example configuration files [here](https://github.com/harvard-nrg/mrverify/tree/main/example_configs).
