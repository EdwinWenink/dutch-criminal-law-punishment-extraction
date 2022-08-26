# Dutch criminal law punishment extraction

Project for extracting punishment vectors from Dutch criminal law.

Set up as a Hydra pipeline with configurable components.
By default all components run as a sequential pipeline.

On repeated runs, skipping certain components can save a lot of  time.
After the first run, you almost certainly want to skip querying and downloading all cases again (unless you change the query parameters in `config/query/default.yaml`):

`python main.py skip_query=true`.

Parsing the xml of the downloaded cases also does not have be repeated.

`python main.py caseparser.skip=true`.


