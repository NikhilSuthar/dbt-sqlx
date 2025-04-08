import os
import yaml
import glob
import click
import logging as logs
from pathlib import Path
from dotenv import load_dotenv
from dbt_sqlx.support import SUPPORTED_SQL_TYPES



def dbt_profile_name(dbt_project):
    """Fetches the dbt profile name from dbt_project.yml."""
    dbt_file = os.path.join(dbt_project, 'dbt_project.yml')
    if not os.path.exists(dbt_file):
        raise FileNotFoundError(click.style(f"dbt_project.yml not found in the specified path '{dbt_project}'. Either pass dbt Project path using option `--dbt-project` or run the command inside dbt project directory. Use `dbt-sqlx transpile --help` for more details.",fg='red',bold=True))
    
    with open(dbt_file, 'r') as file:
        data = yaml.full_load(file)
        return data.get('profile')

def dbt_source_sql_dialect(profile, dbt_profile='~/.dbt/profiles.yml'):
    """Fetches the SQL type from profiles.yml based on the given profile."""
    path = os.path.expanduser(dbt_profile)
    if not os.path.exists(path):
        raise FileNotFoundError(f"profiles.yml not found at {path}")
    
    with open(path, 'r') as file:
        data = yaml.full_load(file)
        profile_data = data.get(profile, {})
        target = profile_data.get("target")
        sql_type = profile_data.get("outputs", {}).get(target, {}).get("type")
        
        if sql_type and sql_type.lower() in SUPPORTED_SQL_TYPES:
            return sql_type
        raise ValueError(f"Invalid SQL Type found: {sql_type}, valid values are {SUPPORTED_SQL_TYPES}")

def list_dbt_models(dbt_project):
    """Returns the list of dbt model files."""
    model_dir = os.path.join(dbt_project, "models")
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"dbt models directory not found at {model_dir}")
    
    return glob.glob(os.path.join(model_dir, "**", "*.sql"), recursive=True)