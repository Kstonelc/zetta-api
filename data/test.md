## Install Package

```python
pip install -r requirements
```

## Run server

```python
uvicorn main:app --reload
```

## Export Third Party Package

```
pip freeze > requirements.txt
```

## DB Auto Generate
```bash
alembic revision --autogenerate -m <description>
alembic upgrade head
```

