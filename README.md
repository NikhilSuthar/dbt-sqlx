# 🚀 dbt-sqlx  
*A CLI to convert SQL models across database dialects in your dbt projects.*

[![SQL Translator](https://img.shields.io/badge/dbt--sqlx-SQL%20Translator-blue.svg?style=flat-square)](https://pypi.org/project/dbt-sqlx/)  
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg?style=flat-square)](https://www.python.org/downloads/)

---

## 🔍 Why dbt-sqlx?

Tired of rewriting SQL logic every time your data platform changes?

Whether you're:

- Migrating from one SQL type to another type like Snowflake to Redshift and many more
- Porting models between versions such as oracle 11g to oracle 19c. 
- Maintaining compatibility across clouds  

**dbt-sqlx automates the hard part — letting you focus on insights, not syntax.**

---

## ✨ Features

✅ Translate dbt models across popular SQL dialects:  
 `Snowflake`, `Redshift`, `PostgreSQL`, `MySQL`, `Oracle`, `BigQuery`, `Spark-SQL`, `SQL Server`  
✅ Retains dbt Jinja templating: `{{ ref('...') }}`, `{{ var('...') }}`  
✅ Bulk model conversion support  
✅ Intuitive CLI: `dbt run -m`-like syntax  
✅ LLM-powered translation via `OpenAI`, `Groq`, `Anthropic`, etc.  
✅ Fully configurable through CLI or `.env`  
✅ SQL version-aware translation (e.g., Oracle 11g vs 19c)  
✅ Auto-detects source dialect from dbt metadata



## 📋 Pre-requisite

- Python **3.10+**
- A dbt project with models
- API key and model name for one of the following providers:

  - [Groq](https://console.groq.com/docs/quickstart) — *Free Tier* 
  - [OpenAI](https://platform.openai.com/) — *Paid*
  - [Anthropic](https://console.anthropic.com/) — *Paid*
  - [Google-GenAI](https://ai.google.dev/gemini-api/docs/rate-limits)-*Free Tier*
  - [MistralAI](https://docs.mistral.ai/getting-started/models/models_overview/)-*Free Tier*



# 🔧 CLI Commands

`dbt-sqlx` provide two main method `config` and `trasnpile`. Both method support multiple options. Below are the details:

```bash
  dbt-sqlx --help
```

## 1. `config`

Set or update default LLM provider, model and Key. It store configuration at `~/.dbt-sqlx/.env`. 

```bash
dbt-sqlx config --help
```


#### 🛠️ CLI Command Options (`config`)

|  **Option**     |**Required?** | **Description**                          |  **Default Value**       |
|-------------------|-------------------|---------------------------------------------|----------------------------|
| `--llm-provider`  | ⚪ **Optional**    | Set or update the default LLM provider      | Not set                    |
| `--llm-model`     | ⚪ **Optional**    | Set or update the default LLM model         | Not set                    |
| `--api-key`       | ⚪ **Optional**    | Provide or update your provider API key     | Not set                    |

📌 **Example:**

**Prompt**

```bash
dbt-sqlx config
```
*Output*
```bash  
Updating dbt-sqlx environment settings...
Select model provider:
  1. OpenAI
  2. Groq
  3. Anthropic
  4. Mistral
  5. Cohere
  6. Google
  7. Azure
Enter your choice (1 to 7): 1
Enter the model name (e.g., gpt-4o, mixtral-8x7b): gpt-4o
The provider OpenAI API Key already configured, Do you want to overwrite? [Y-Yes, N-No]: Y
Enter API key for OpenAI: 
Successfully configured below configuration:
Default Provider -> OpenAI
Default LLM Model -> gpt-4o
Default Provider API Key -> sk-proj-******************************ht4GS5YA
```

**Single Command**
```bash
dbt-sqlx config --llm-provider OpenAI --llm-model gpt-4o --api-key sk-xxxxxxxxxx
```

## 2. `transpile`

Convert dbt models to the target dialect. It create new directory named as *models_`target_sql`* in your dbt project to avoid unintentially overwrite existing models.

```bash
dbt-sqlx transpile --help
```
 #### Options

### 🛠️ CLI Command Options (`transpile`)

|  **Option**         |  **Required?** |  **Description**                                                  |  **Default Value**       |
|------------------------|-------------------|---------------------------------------------------------------------|----------------------------|
| `--target-sql`         | 🟢 **Required**    | Target SQL dialect (e.g., `oracle`, `snowflake`, `redshift`)       | —                          |
| `--target-sql-version` | ⚪ **Optional**    | Target SQL version (e.g., `11g`, `19c` for Oracle)                         | `latest`                   |
| `--source-sql`         | ⚪ **Optional**    | Source SQL dialect (auto-detected if omitted)                       | Auto-detected              |
| `--dbt-project`        | ⚪ **Optional**    | Path to your dbt project                                            | Current directory (`pwd`)  |
| `--models`             | ⚪ **Optional**    | Comma-separated list of specific dbt models to transpile                | All models                 |
| `--llm-provider`       | ⚪ **Optional**    | Override default LLM provider (e.g., OpenAI, Groq)                  | Configured provider        |
| `--llm-model`          | ⚪ **Optional**    | Override default LLM model                                          | Configured model           |
| `--verbose`            | ⚪ **Optional**    | Enable logging of LLM Provider and Model during execution                            | False                        |

📌 **Example:**

Below is the exmaple of transpile specific models `dim_customer` & `dim_order` of the dbt project named as `dbt-ecom` into **Oracle**.
```bash
dbt-sqlx transpile --target-sql oracle --dbt-project ~/dbt/dbt-ecom/ --models dim_customer,dim_order
```

---

## ⚡Quick Start

### 📦 Installation

Install the dbt-sqlx from PyPI.

```bash
pip install dbt-sqlx
```


### ✅ Verify Installation

```bash
dbt-sqlx --version
```

output
```bash
dbt-sqlx version x.x.x
```

### ⚙️ Configuration

Set up your default LLM provider, model, and API key:

```bash
dbt-sqlx config
```

You'll be prompted to enter:
- **LLM Provider** (e.g., OpenAI, Groq)
- **Model Name** (e.g., gpt-4, mixtral)
- **API Key** (input hidden for security)

Alternatively, you can use one line command to configure default Provider and Model:

```bash
dbt-sqlx config --llm-provider your-llm-provider --llm-model your-llm-model --api-key your-api-key
```

```bash
# Example 
dbt-sqlx config --llm-provider Groq --llm-model llama-3.3-70b-specdec  --api-key ] gsk_ob**********LhiB
```



### 🚀 Usage

Convert all dbt Project's models

```bash
dbt-sqlx transpile --target-sql your-sql-type --dbt-project /path/to/dbt-project
```

```bash
# Example
dbt-sqlx transpile --target-sql oracle --dbt-project /path/to/dbt-project
```

🎯 Convert Specific Models

```bash
dbt-sqlx transpile --target-sql snowflake --dbt-project /path/to/project --models model1,model2
```

## 🎥 Demo

Check out dbt-sqlx in action! 👇

[![dbt-sqlx in Action](http://i.ytimg.com/vi/tFpBSFq7OO8/hqdefault.jpg)](https://www.youtube.com/watch?v=tFpBSFq7OO8)


## 🎯 Use Cases

### 🧾 Input (Snowflake SQL):

```sql
SELECT
    user_id,
    first_name,
    CURRENT_TIMESTAMP AS refreshed_at
FROM {{ ref('dim_customers') }}
``` 

```bash
dbt-sqlx transpile --target-sql redshift --dbt-project your-dbt-project-path
```

### 🔁 Output (Redshift):

```sql
SELECT
    user_id,
    first_name,
    GETDATE() AS refreshed_at
FROM {{ ref('dim_customers') }}
```

---

### 🧾 Input (Snowflake SQL):

```sql
SELECT customer_id,
       LISTAGG(DISTINCT first_name, ', ') WITHIN GROUP (ORDER BY first_name) AS customers
FROM {{ ref('dim_customers') }}
GROUP BY customer_id;
```

```bash
dbt-sqlx transpile --target-sql oracle --target-sql-version 11g --dbt-project your-dbt-project-path
```

### 🔁 Output (Oracle 11g):

```sql
SELECT customer_id,
       RTRIM(XMLAGG(XMLELEMENT(e, first_name || ', ') ORDER BY first_name).EXTRACT('//text()'), ', ') AS customers
FROM (
    SELECT DISTINCT customer_id, first_name
    FROM {{ ref('dim_customers') }}
) 
GROUP BY customer_id;
```

```bash
dbt-sqlx transpile --target-sql oracle --target-sql-version 19c --dbt-project your-dbt-project-path
```

### 🔁 Output (Oracle 19c):

```sql
SELECT customer_id,
       LISTAGG(first_name, ', ') WITHIN GROUP (ORDER BY first_name) AS customers
FROM (
    SELECT DISTINCT customer_id, first_name
    FROM {{ ref('dim_customers') }}
) subquery
GROUP BY customer_id;
```


## Sample Configuration

Below are some sample configuration of LLM providers and models:


**Groq**
```
LLM_Provider = "Groq"
LLM_Name = 'llama-3.3-70b-versatile'
LLM_Provider_Key = 'gsk_*************************TLhiB'
```

**Open AI**
```
LLM_Provider = "OpenAI"
LLM_Name = 'gpt-4o'
LLM_Provider_Key = sk-proj-*****************************5YA
```
**Google GenAI**
```
LLM_Provider = "Google_Genai"
LLM_Name = 'gemini-2.0-flash'
LLM_Provider_Key = 'AI******************************7k'
```

**Mistral AI**
```
LLM_Provider = "MistralAI"
LLM_Name = 'mistral-small-latest'
LLM_Provider_Key = 'a2**************************ya0'
```


> **⚠️ Important Notes**
>- `dbt-sqlx` uses LLM models — do not use if your code is under strict data security policies.
>- Accuracy may vary depending on the LLM — always review and test translated code.
>- It **does not overwrite** original models. Output is stored in a direcotry named as models with suffix target SQL type 'models_<target_SQL>' like `models_oracle/`.

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](https://github.com/NikhilSuthar/dbt-sqlx/blob/main/LICENSE) file for details.


## 📬 Contact

👨‍💻 Author: [Nikhil Suthar](https://www.linkedin.com/in/nikhil-suthar/)  
📧 [Email](mailto:n.suthar.tech@gmail.com)
