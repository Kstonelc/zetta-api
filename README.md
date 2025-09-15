## Create Python Virtual Environment(Python 3.11.9: recommended)

```bash
conda create -n zetta-api python=3.11.9
```

## Install Package

```bash
pip install -r requirements
```

## Run server

```bash
uvicorn main:app --reload
```

## DB Auto Generate
```bash
alembic revision --autogenerate -m <description>
alembic upgrade head
```

