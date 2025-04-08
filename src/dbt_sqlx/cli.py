import os
import click
from dbt_sqlx.config import config, validate_env
from dbt_sqlx.translator import sql_converter
from dbt_sqlx.support import SUPPORTED_SQL_TYPES
from dbt_sqlx.dbt_utils import dbt_profile_name, dbt_source_sql_dialect, list_dbt_models
from dbt_sqlx import __version__

@click.group()
@click.version_option(
    version=__version__,
    prog_name="dbt-sqlx",
    message="%(prog)s version %(version)s",
)
def cli():
    """dbt-sqlx: A CLI tool to convert SQL models between SQL dialects."""
    pass

@cli.command()
@click.option("--target-sql", required=True, help="Target SQL dialect (e.g., --target-sql postgres).")
@click.option("--target-sql-version", required=False, help="Target SQL dialect version, default is 'latest'. (e.g. --target-sql oracle --target-sql-version 21.1.0).")
@click.option("--source-sql", required=False, help="Existing SQL dialect (e.g., --source-sql snowflake).")
@click.option("--dbt-project", default=os.getcwd(), help="Path to DBT project where the 'dbt_project.yml' file exist.")
@click.option('--models', type=str ,required=False, default=None, help="Specify one or more dbt models to transpile (e.g., --model model1,model2)."
)
@click.option("--llm-provider", required=False, help="Name of the provider (e.g., OpenAI, Groq)")
@click.option("--llm-model", required=False, help="LLM Model name for the provider(e.g., gpt-4o).")

@click.option("--verbose", default=False, help="To log the model name and provider being use.")

def transpile(target_sql,target_sql_version =None, source_sql=None, dbt_project=os.getcwd(), models = None, llm_provider=None, llm_model=None, verbose=False):

    if (llm_provider and not llm_model) or (llm_model and not llm_provider):
        raise click.UsageError(click.style("Both --llm-provider and --llm-model must be passed together.", fg="red", bold=True))
    
    """Translate DBT models to a target SQL dialect."""
    validate_env(llm_provider, llm_model)  # Ensure environment is set up
   
    if target_sql.lower() not in SUPPORTED_SQL_TYPES:
        raise click.ClickException(click.style(f"Invalid target SQL: {target_sql}. Only {SUPPORTED_SQL_TYPES} are allowed.", fg="red"))
    
    if source_sql is None:
        profile_name = dbt_profile_name(dbt_project)
        source_sql = dbt_source_sql_dialect(profile_name)
        click.echo(click.style(f"Source SQL dialect found is -> {str(source_sql).title()}",fg="yellow", bold=True))
    else:
        click.echo(click.style(f"Input source SQL dialect is -> {str(source_sql).title()}",fg="yellow", bold=True))
    
    if source_sql.lower() == target_sql.lower() and target_sql_version is None:
        raise click.ClickException(click.echo(click.style(f"Your DBT Models are already with SQL dialect {str(source_sql).title()}. Please pass --target-sql-version if you want to change the version of current dialect.",fg="red", bold=True)))
    
    all_models = list_dbt_models(dbt_project)
    
    if models is None:
        models_to_be_convert = all_models
    else:
        input_models = [f"{str(x).strip()}.sql" for x in str(models).split(",")]
        models_to_be_convert = [str(x) for x in all_models if x.rsplit("/",1)[1] in input_models]
    # click.echo(f"All models {all_models} and processing {models_to_be_convert} and input models {models}")
    
    click.echo(click.style(f"\n Total {str(len(all_models))} dbt models found. Converting {len(models_to_be_convert)} models.", fg="blue", bold=True))
    if target_sql_version:
        click.echo(click.style(f"\n Translating the Model into {str(target_sql).title()} with version {target_sql_version}", fg="blue", bold=True))
    else:
        click.echo(click.style(f"\n Translating the Model into {str(target_sql).title()}", fg="blue", bold=True))
    for model in models_to_be_convert:
        sql_converter(source_sql=source_sql, target_sql=target_sql, target_sql_version=target_sql_version, dbt_model_name=model,LLM_Provider=llm_provider, LLM_Name=llm_model,verbose=verbose)

    click.echo(click.style(f"\n🎉 Successfully converted input dbt models to {str(target_sql).title()}!", fg="green", bold=True))

cli.add_command(config)

if __name__ == "__main__":
    cli()
