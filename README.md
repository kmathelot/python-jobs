# Python Job

I like to have batch jobs to do almost every repetitive things. Started from RDS postgres log analysis to github action consumption. It store the results in a dedicated db for further analysis / dashboard

2 possible actions : 
aws : get logs from an AWS RDS instance (not stream logs.)
github : get workflow runs from github

## Usage guide (UNIX users)
```sh
$ python reports.py [--config config_name] [--date reference_date] {fetch,db,stats}

fetch {github,...}
  - Github: get actions usage from api.

db {init,clean}
  - Init : Init database : create schema and tables
  - CLean : Delete old or unused entries
  
stats {compute,...}
  - compute : parse and calculate query stats (schema and table identification, joins)
```

### Requirements
* Python 3.9+ (tested: `3.10.8`)
* Python modules as listed in [`requirements.txt`](requirements.txt)
* Github Access token

### Generic recomandations
Consider usage of [`pyenv`](https://github.com/pyenv/pyenv) to manage multiple python installation.
### Installation guide (Linux)

<details>
<summary>Details</summary>

* Install Python 3.9+ from your preferred package manager.
* preferably, use a venv `python -m venv name_of_your_venv` and `. ./ name_of_your_venv/bin/activate`
* Install the PIP modules with the following command `pip install -r requirements.txt`. (It's possible depending on your installation to have to call pip3 instead of pip.)
* Jobs are using env variables (such as db user etc). To override them you need to create a json config file and pass the arg --config 
* Run `python reports.py` with the appropriate arguments
</details>

### configuration
Right now the job only work with a postgres DB.  

There is 6 environment variables to configure : 
- DB_HOST
- DB_USER
- DB_PASS
- DB_NAME
- DB_PORT
- GH_TOKEN

These variables are made to store the results in a dedicated DB. You can override them with a dedicated json file in the src/config folder :
```
{
  "db_host": "your-amazing-db-host",
  "db_user": "awesome-user",
  "db_pass": "incredible_password",
  "db_port": 5432,
  "db_name": "marvelous_db",
  "gh_token": "Crazy-token"
}
```

### Docker image
The dockerfile provide a way to build an image

### kubernetes cronjob
There is a template to deploy the jobs in a Kubernetes cluster, to make it work you have to add some secret

## Todo : 
[] Create a dedicated postgres analysis tool (like pgbadger) with UI  
[] Create a dedicated Github analysis tool with UI  
[] Add organization name in either config or argument  
[] Add variable db instance identifier
[] DB cleaner 
[] Make it more Generic
[] Add stream log features
