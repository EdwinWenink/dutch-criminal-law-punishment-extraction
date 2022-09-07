# Dutch criminal law punishment extraction

Project for extracting punishment vectors from Dutch criminal law.

Set up as a Hydra pipeline with configurable components.
By default all components run as a sequential pipeline.

The required dependencies can be installed via the [requirements.txt file](./requirements.txt).

## Running the code

When running the pipeline, a query will be submitted to the ECLI-index of rechtspraak.nl.
This returns an atom XML feed with European Case Law Identifiers (ECLI) of cases matching the query.
A large set of queries are then submitted to retrieve the case transcriptions in XML format.
*This may take a while depending on your query!*

The raw XML files will be stored in a data directory that is automatically created.
The `CaseParser` consequently parses the XML files, extracts information, and stores the results in a CSV file.
This CSV can be used for several downstream AI, data science, and machine learning applications.

By default, a data set is created on the section level, where each section is annotated with its role in the overall case transcription.
For sections where the role is "beslissing" (i.e. the case decision) we additionally extract all punishments that are imposed in that decision section, *including their height*, as a multidimensional vector.

TODO explain logging.

## Configuration

The [config](./config) folder holds the relevant configuration parameters for the Hydra pipeline.
By default the configuration reproduces the setup of the corresponding paper.
You can override configurations dynamically on the command line, see below for an example.

On repeated runs, skipping certain components can save a lot of time.
After the first run, you almost certainly want to skip querying and downloading all cases again (unless you change the query parameters in `config/query/default.yaml`):

`python main.py skip_query=true`.

Parsing the xml of the downloaded cases also does not have be repeated unless changes to the parser are made.

`python main.py caseparser.skip=true`.

These options can be freely combined:

`python main.py skip_query=true caseparser.skip=true`.

TODO explain debug mode.


## Used regular expressions

See the [supplementary materials](./docs/supplementary.tex) for an explanation of the used regular expressions, a walkthrough of several test cases, and a brief failure analysis.


## Evaluation

The performance of the punishment extraction is manually evaluated on the following randomly selected cases from 2021:

```
ECLI:NL:RBAMS:2021:2514, ECLI:NL:RBAMS:2021:7026, ECLI:NL:RBAMS:2021:765, ECLI:NL:RBGEL:2021:2304, ECLI:NL:RBGEL:2021:3033, ECLI:NL:RBGEL:2021:4518, ECLI:NL:RBGEL:2021:6569, ECLI:NL:RBGEL:2021:6833, ECLI:NL:RBLIM:2021:5488, ECLI:NL:RBLIM:2021:5570, ECLI:NL:RBMNE:2021:5182, ECLI:NL:RBNNE:2021:2888, ECLI:NL:RBOVE:202, ECLI:NL:RBOVE:2021:1784, ECLI:NL:RBOVE:2021:2379, ECLI:NL:RBOVE:2021:3523, ECLI:NL:RBOVE:2021:3609, ECLI:NL:RBOVE:2021:4172, ECLI:NL:RBOVE:2021:4354, ECLI:NL:RBOVE:2021:4510, ECLI:NL:RBOVE:2021:606, ECLI:NL:RBOVE:2021:643, ECLI:NL:RBOVE:2021:75, ECLI:NL:RBROT:2021:1932, ECLI:NL:RBROT:2021:2039, ECLI:NL:RBROT:2021:4354, ECLI:NL:RBROT:2021:7766, ECLI:NL:RBROT:2021:8751, ECLI:NL:RBROT:2021:8814, ECLI:NL:RBROT:2021:8835, ECLI:NL:RBROT:2021:9086, ECLI:NL:RBROT:2021:9706, ECLI:NL:RBZWB:2021:3656, ECLI:NL:RBZWB:2021:3658, ECLI:NL:RBZWB:2021:6216
```

TODO

- The manual evaluation results can be found [here TOOD](TODO).
- How to run test cases (make a proper test file)
