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


## TODO Explanation of the case parser

- Parsing steps and rules
- Extended explanation of the used regular expressions
    * Render a separate PDF of the appendix and refer to it here
- How to run test cases (make a proper test file)
