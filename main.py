import json
import os
import click
import getpass
from config import Config
from auth.auth import Authenticator
from voyager_sdk.configuration import OperatorConfiguration
from voyager_sdk.protocols import ProtocolType
from voyager_sdk.bootstrap import OperatorBootstrapper
from voyager_sdk.operator.operator_runner import OperatorRunner
from voyager_sdk.operator.operator_factory import OperatorFactory
from exceptions.auth_exceptions import InvalidCredentialsException, FailedToLoginException

config = Config()


@click.command("login")
def login():
    """

    :return: list

    """
    if Authenticator.verify():
        print(f"User {config.email} already logged in")
    else:
        while True:
            username = input("Username: ")
            if not username:
                print("Username needs to be specified")
                continue
            password = getpass.getpass("Password: ")
            if not password:
                print("Password needs to be specified")
                continue
            if password and username:
                break
        try:
            Authenticator.login(username, password)
        except InvalidCredentialsException as e:
            print("Failed to authenticate. Invalid credentials")
        except FailedToLoginException as e:
            print("Service unavailable.")


@click.command("logout")
def logout():
    email = config.email
    config.auth_token = ""
    config.refresh_token = ""
    config.email = ""
    print(f"User {email} logged out")


@click.group("operator")
def operator():
    pass


@operator.command("create")
@click.option("--name", help="Operator class name (example: PipelineXOperator)")
@click.option("--pipeline_name", help="Pipeline name (example: Pipeline 1.0.0)")
@click.option("--pipeline_github", help="Pipeline github repository")
@click.option("--pipeline_github_version", help="Pipeline github version (tag or branch)")
@click.option("--pipeline_entrypoint", help="Pipeline script (cwl or nf)")
@click.option('--format',
              type=click.Choice(['CWL', 'NF'], case_sensitive=False), help="Pipeline script format (CWL or NF)")
def create_operator(name, pipeline_name, pipeline_github, pipeline_github_version, pipeline_entrypoint, format):
    print(f"Bootstrapping Operator {name} for Pipeline")
    current_dir = os.getcwd()
    if format == "CWL":
        pipeline_format = ProtocolType.CWL
    elif format == "NF":
        pipeline_format = ProtocolType.NEXTFLOW
    else:
        exit(1)
    try:
        OperatorBootstrapper.initialize(name,
                                        current_dir,
                                        pipeline_name,
                                        pipeline_github,
                                        pipeline_github_version,
                                        pipeline_entrypoint,
                                        pipeline_format)
    except Exception as e:
        print(e)


@operator.command("run")
@click.option("--request-id", help="Run Operator based on metadata key igoRequestId")
@click.option("--pairs", help="Run Operator based on T/N Pairs (path to file)")
@click.option("--dry-run",  is_flag=True)
def run_operator(request_id, pairs, dry_run):
    current_path = os.getcwd()
    operator_runner = OperatorRunner(current_path)
    jobs = operator_runner.run(request_id, pairs)
    if dry_run:
        print(json.dumps(jobs, indent=4))
        exit(0)
    else:
        operator_configuration = OperatorConfiguration.load()
        if not operator_configuration.pipeline["pipeline_id"]:
            print("Need to run voyager-sdk pipeline register before submitting runs to voyager")
            exit(1)
        operator_runner.submit_runs(jobs)


@operator.command("register")
def register_operator():
    current_path = os.getcwd()
    jobs = OperatorRunner(current_path).register()
    print("Operator Register")


@click.group("pipeline")
def pipeline():
    pass


@pipeline.command("register")
def register_pipeline():
    current_path = os.getcwd()
    OperatorRunner(current_path).register_pipeline()


@click.group()
def main():
    pass


main.add_command(login)
main.add_command(logout)
main.add_command(operator)
main.add_command(pipeline)


if __name__ == "__main__":
    main()
