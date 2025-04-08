import os
import click
import logging as logs
import re
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

ENV_PATH = os.path.expanduser("~/.dbt-sqlx/.env")

def sql_converter(source_sql, target_sql, target_sql_version, dbt_model_name, env_path = '~/.dbt-sqlx/.env', LLM_Provider=None,LLM_Name=None,verbose=False):
    load_dotenv(os.path.expanduser(env_path))
    """Converts SQL models from source to target SQL dialect."""
    with open(dbt_model_name, 'r') as file:
        model_code = file.read().strip()
      
    system_prompt = (
        "You are an expert in SQL dialect and version translation.\n"
        "Your task is to translate SQL code from one dialect to another, accurately and safely, considering differences between SQL dialects and versions.\n"
        "\n"
        "**STRICT RULES TO FOLLOW:**\n"
        "- Use only official, version-compliant syntax for the **target SQL dialect and version**.\n"
        "- If the target SQL version does not support a function or feature, replace it with supported equivalent logic.\n"
        "- Do NOT invent new functions. Use only official alternatives.\n"
        "- Preserve all DBT Jinja templating syntax exactly as-is (e.g., {{ ref('...') }}, {{ var('...') }}).\n"
        "- Do NOT change variable names, indentation, or any existing comments.\n"
        "- At the **top of the translated model**, insert a comment: `-- Converted to {target_sql} (<version that you are using to convert>)`\n"
        "- If **any change** is made to a function, syntax, or logic, insert a comment directly **above** the changed line explaining what was changed and also make sure you change\n"
        "- At the **end of the model**, add a single summary comment if necessary, starting with `-- NOTE:`.\n"
        "- Output only the translated SQL code. No explanation or markdown formatting."
    )


    if target_sql_version is None:
        target_sql_version = "latest"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", 
        "Convert the SQL code below from {source_sql} to {target_sql}.\n"
        "Target SQL version: {target_version}\n\n"
        "{model_code}")
    ])
    if LLM_Name is None:
        LLM_Name = os.getenv('MODEL_NAME')
    if LLM_Provider is None:
        LLM_Provider = os.getenv('MODEL_PROVIDER')
    LLM_Provider_Key = os.getenv(f"{str(LLM_Provider).upper()}_API_KEY")
    if verbose:
        click.echo(click.style(f"Using LLM Model {LLM_Name} of the provider {LLM_Provider}.", fg=240, bold=True))
    llm = init_chat_model(model=LLM_Name, model_provider=LLM_Provider,temperature=0, api_key=LLM_Provider_Key)
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"model_code": model_code, "source_sql": source_sql, "target_sql":target_sql, "target_version": target_sql_version})
    result = result.strip().replace("```sql", "").replace("```", "").strip()
    
    
    if target_sql_version and target_sql_version.strip().lower() != "latest":
        safe_version = re.sub(r'[^a-zA-Z0-9]+', '_', target_sql_version.strip().lower())
        target_model_path = f"models_{target_sql.replace('-','_').lower()}_{safe_version}/"
    else:
        target_model_path = f"models_{target_sql.replace('-','_').lower()}/"

    
    target_path = dbt_model_name.replace("models/",target_model_path)
    if verbose:
        click.echo(click.style(f"Writing converted Model into {target_path}.", fg=240, bold=True))

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    with open(target_path, "w") as file:
        file.write(result)
    
    model_path = dbt_model_name.split("/models/")[1]
    click.echo(click.style(f"✅ Model {model_path} converted to {str(target_sql).title()} v{target_sql_version}.", fg="green"))
