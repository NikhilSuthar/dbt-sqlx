import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values, set_key
import click
from dbt_sqlx.support import SUPPORTED_PROVIDERS, PROVIDER_API_KEY_PREFIX



ENV_PATH = os.path.expanduser("~/.dbt-sqlx/.env")
# Ensure env file exists
Path(os.path.dirname(ENV_PATH)).mkdir(parents=True, exist_ok=True)
if not os.path.exists(ENV_PATH):
    open(ENV_PATH, 'w').close()

def load_env():
    """Load existing environment variables."""
    if load_dotenv(ENV_PATH, override=True):
        return dotenv_values(ENV_PATH)
    else:
        return {}
        
def mask_key(key):
    t = len(key)
    m = int(t * 0.90)
    loop = m if m < 20 else 30
    mask_value =  ''.join([str('*') for x in range(loop)])
    key_mask = f"{key[:int((t-m)/2)]}{mask_value}{key[-int((t-m)/2):]}"
    return key_mask     

def save_env(key, value):
    """Save or update a key-value pair in the .env file."""
    set_key(ENV_PATH, key, value)

def validate_env(llm_provider=None, llm_model=None):
    """Ensure required environment variables are set."""
    env_vars = load_env()
    required_keys = ['MODEL_PROVIDER', 'MODEL_NAME']
    
    if ((llm_provider is not None) and (llm_model is not None)):
        provider_key =  f"{str(llm_provider).upper()}_API_KEY"
        # click.echo(f"Env - {env_vars}")
        if ((len(env_vars.keys()) > 0) and (provider_key in env_vars.keys())):
            api_key = env_vars[provider_key]
            if ((str(api_key).strip() == '') or (api_key is None)):
                raise click.ClickException(
                    click.style(f"\nThe Provider Key {api_key} in missing. Run `dbt-sqlx config` first to configure.", fg="red", bold=True))
            else:
                click.style(f"The Provider Key {api_key} found.", fg="green", bold=True)
                return {}
        else:
            raise click.ClickException(
                click.style(f"The Provider Key '{provider_key}' not found. Run `dbt-sqlx config` first to configure.", fg="red", bold=True)
            )
    for key in required_keys:
        if key not in env_vars.keys() or not env_vars[key]:
            raise click.ClickException(
                click.style(f"Missing Provider and LLM Model in environment. Run `dbt-sqlx config` first to configure.", fg="red", bold=True)
            )
    return env_vars

@click.command()
@click.option("--llm-provider", required=False, help=f"Update default Provider.Valid LLM Provider are {SUPPORTED_PROVIDERS}")
@click.option("--llm-model", required=False, help="Update default Provider Model.")
@click.option("--api-key", required=False, help="Update Provider API Key.")
def config(llm_provider=None,llm_model=None,api_key=None):
    if (llm_provider and not llm_model) or (llm_model and not llm_provider):
        raise click.UsageError(click.style("Both --llm-provider and --llm-model must be passed together.", fg="red", bold=True))
    
    """Update environment configuration."""
    click.echo(click.style("\nUpdating dbt-sqlx environment settings...", fg='blue', bold=True))
    
    if llm_provider is None:
        # Display provider options
        click.echo(click.style("Select model provider:", bold=True))
        for i, provider in enumerate(SUPPORTED_PROVIDERS, 1):
            click.echo(f"  {i}. {provider}")
        
        provider_index = click.prompt(click.style(f"Enter your choice (1 to {str(len(SUPPORTED_PROVIDERS))})",fg='cyan', bold=True), type=int)
        while (provider_index not in range(1, len(SUPPORTED_PROVIDERS) + 1)):
            click.echo(click.style(f"Invalid choice, please enter correct choice between (1 to {str(len(SUPPORTED_PROVIDERS))})", fg='red', bold=True))
            provider_index = click.prompt(click.style(f"Enter your choice (1 to {str(len(SUPPORTED_PROVIDERS))})",fg='cyan', bold=True), type=int)

        provider = SUPPORTED_PROVIDERS[provider_index - 1]
    elif llm_provider not in SUPPORTED_PROVIDERS:
        raise click.UsageError(click.style(f"Invalid Provider. Valid Provider are {SUPPORTED_PROVIDERS}", fg='red', bold=True))
    else:
        provider = llm_provider
    
    save_env('MODEL_PROVIDER', provider)
    if ((llm_model is None ) or (str(llm_model).strip() == '')):
        model_name = click.prompt(click.style("Enter the model name (e.g., gpt-4o, mixtral-8x7b)",fg='cyan', bold=True))
        while ((str(model_name) is None ) or (str(model_name).strip() == '')):
            click.echo(click.style(f"Model can be not be blank.", fg="red"))
            model_name = click.prompt(click.style("Enter the model name (e.g., gpt-4o, mixtral-8x7b)",fg='cyan', bold=True))
    else:
        click.echo(click.style(f"Provider {llm_provider} Model {llm_model} set as default.", fg='green', bold=True))
        model_name = llm_model
    
    save_env('MODEL_NAME', model_name)
    overwrite = True
    if str(provider).lower() in PROVIDER_API_KEY_PREFIX.keys():
        provider_api_key = f'{str(PROVIDER_API_KEY_PREFIX[str(provider).lower()]).upper()}_API_KEY'
    else:
        provider_api_key = f'{str(provider).upper()}_API_KEY'

    if ((api_key is None ) or (str(api_key).strip() == '')):
        env_vars = load_env()
        if provider_api_key in env_vars.keys() and not str(env_vars[provider_api_key]).strip() == '':
            choice = click.prompt(click.style(f"The provider {provider} API Key already configured, Do you want to overwrite? [Y-Yes, N-No]", fg="yellow", bold=True), hide_input=False)
            if str(choice).upper() in ['N','NO']:
                overwrite = False
            elif str(choice).upper() in ['Y','YES']:
                overwrite = True
            else:
                while (not str(choice).upper() in ['N','NO','Y','YES']):
                    click.echo(click.style(f"Invalid choice, pass 'Y' for Yes and 'N' for No.", fg="red"))
                    choice = click.prompt(click.style(f"The provider {provider} API Key already configured, Do you want to overwrite? [Y-Yes, N-No]", fg="yellow", bold=True), hide_input=False)
                    if str(choice).upper() in ['N','NO']:
                        overwrite = False
        if overwrite:
            api_key = click.prompt(click.style(f"Enter API key for {provider}",fg='cyan', bold=True), hide_input=True)
            while ((str(api_key) is None ) or (str(api_key).strip() == '')):
                click.echo(click.style(f"API key can not be blank", fg="red"))
                api_key = click.prompt(click.style(f"Enter API key for {provider}",fg='cyan', bold=True), hide_input=True)
            
            save_env(provider_api_key, api_key)
    else:
        save_env(provider_api_key, api_key)
    
    click.echo(click.style("Successfully configured below configuration:", fg='blue', bold=True))
    click.echo(click.style(f"Default Provider -> {provider}", fg='magenta', bold=True))
    click.echo(click.style(f"Default LLM Model -> {model_name}", fg='magenta', bold=True))
    if overwrite:
        click.echo(click.style(f"Default Provider API Key -> {mask_key(api_key)}", fg='magenta', bold=True))

