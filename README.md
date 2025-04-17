# Voyager SDK

Voyager SDK is a developer toolkit for integrating pipelines into the Voyager platform using modular components called Operators. It enables researchers and engineers to define pipeline-specific logic in a reusable, testable format—supporting both CWL and Nextflow workflows—without modifying the core Voyager codebase.

## Getting Started

Prerequisites:
- Python >= 3.x
- Voyager platform instance
    - https://github.com/mskcc/beagle/
    - https://github.com/mskcc/ridgeback/

## Usage

Usage: voyager-sdk [OPTIONS] COMMAND [ARGS]...

Options:<br/>
  --help  Show this message and exit.

Commands:<br/> 
  login<br/> 
  logout<br/> 
  operator<br/> 

### Login

In order to start development of the operator you need to authenticate to Voyager platform

### Logout

In case you want to authenticate with a different user you can logout from the Voyager platform

### Operator

Operator subcommand contains all commands needed to start developing Operator

Usage: voyager-sdk operator [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:<br/>
  create<br/>
  register<br/>
  run<br/>

### Operator Create

Operator create command bootstrap the Operator project. It creates the operator_class file together with configuration files which contains the information about Pipeline for which Operator will be developed and input schema of the pipeline.

Usage: voyager-sdk operator create [OPTIONS]

Options:
  --name TEXT                     Operator class name (example:
                                  PipelineXOperator)<br/>
  --pipeline_github TEXT          Pipeline github repository<br/>
  --pipeline_github_version TEXT  Pipeline github version (tag or branch)<br/>
  --pipeline_entrypoint TEXT      Pipeline script (cwl or nf)<br/>
  --format [CWL|NF]               Pipeline script format (CWL or NF)<br/>
  --help                          Show this message and exit.

### Operator Run

Operator run command instantiate the Operator class and calls the get_jobs() function.

Usage: voyager-sdk operator run [OPTIONS]

Options:<br/>
  --request-id TEXT  Run Operator based on metadata key igoRequestId<br/>
  --pairs TEXT       Run Operator based on T/N Pairs (path to file)<br/>
  --help             Show this message and exit.