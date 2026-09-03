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

Let's start by dissecting the following command

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html
```

MR Verify will query the XNAT installation `xnat` for the MR Session 
with the label `AB1234C`. It will automatically detect acquisition 
details such as the MRI scanner make, model, software version, 
receiver coil, and serial number.

Once MR Verify has resolved these acquisition details, it will begin by 
looking under the `./configs` directory for a configuration file that matches
those specific environment details. Once found, the configuration file should 
include all scans that should be checked (queried using `filters`), the acquisition 
parameters that should be checked, and their expected values. The generated 
report will be saved to `output.html`.

# Configuration files

MR Verify will attempt to locate a configuration file based on acquisition details 
including the MRI scanner make, model, software version, receiver coil, or the 
scanner's serial number for cases when you have a particular scanner that needs 
special treatment.

MR Verify will look for a configuration file within the directory the user passed in 
via the `-c|--configs-dir` argument.

Let's take a closer look a how this works, by dissecting the following command

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

If a configuration file could not be found at that location, MR Verify will work 
its way back up through the directory tree until it finds a match. In an ideal
situation, you only need to maintain a single configuration file that lives under 
`siemens`, because all scanners involved in your study happen to be 100% identical 
for the entire duration of the study. We can all dream, right?

For multisite studies, it is not at all unusual for a data collection site to 
only have access to a specific head coil. This may require subtle changes to the 
scanning protocol, which will lead to different MR Verify configuration files for 
sites that are using different head coils. You would support this by adding 
a sub-directory under the software version, like so

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

On the other hand, perhaps you've decided that using anything other than a
32-channel head coil is a protocol violation. In that case, you may choose to 
specify a configuration file at the software version level that checks the head 
coil

```console
./configs
└── siemens
    └── prisma
        └── ve11b
            └── mrverify.yaml
```

## device serial number
It is not uncommon to face a situation where you have a single scanner that is 
behaving differently from other scanners with nearly identical properties. In 
those situations, you may need a configuration file that targets that specific 
scanner. To do this, you can include a subdirectory at the root level of your
configuation file directory tree that targets the serial number of that scanner.
Within that subdirectory, you may (or may not) create any of the subdirectories 
described above. Maybe this scanner is upgraded to a new software version next 
month. You never know what could happen, but MR Verify has got your back

```console
./configs
└── 123456
    └── siemens
        └── prisma
            └── xa60
                └── head_32
                    └── mrverify.yaml
```

You can find example configuration files [here](https://github.com/harvard-nrg/mrverify/tree/main/example_configs).

# Operators

Fundamentally, MR Verify checks that acquisition parameters match _expected 
values_ that are specified within your customizable configuration file. 

Most of these "expected values" are expressed as simple scalar values, or 
a lists of values, which boils down to a simple equality check

```yaml
echo_time: 1.83
repetition_time: 8000
pixel_spacing: [4, 4]
coil_elements: HC1-7;NC1
```

However, MR Verify includes other ways to express expected values.

## regular expression 

Expected values may also be expressed as a _regular expression_

```yaml
orientation_string: regex(Sag>.*)
``` 

## range

Expected values may also be expressed as a _range_ of values

```yaml
abs_table_position: range(-1275, -1225)
```

# Notifications

Passing the `-n|--notify` argument to MR Verify will send an email 
notification, including the generated HTML report, to chosen recipients

```bash
mrcheck.py -a xnat -l AB1234C -c ./configs -o output.html -n
```

Some recipients may only want to be notified when a parameter check fails.
Others may want to receive reports that pass _or_ fail. Within each 
`mrverify.yaml` configuration file, you're able to specify recipients for 
reports that either `pass`, or `fail`, or both.

You can find example configuration files [here](https://github.com/harvard-nrg/mrverify/tree/main/example_configs).
