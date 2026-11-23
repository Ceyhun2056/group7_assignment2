# LifeQuest API prototype

LifeQuest helps students turn academic and personal tasks into quests. This
Assignment 2 prototype uses FastAPI and an in-memory quest store.

## Run locally

Use Python 3.10 or newer. In the repository root, create a virtual environment.

```bash
python -m venv .venv
```

Activate it in Windows PowerShell with `.venv\Scripts\Activate.ps1`, or on
macOS/Linux with `source .venv/bin/activate`. Then install the dependencies and
start the server.

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open the [greeting page](http://127.0.0.1:8000/api/v1/greeting) or
[Swagger UI](http://127.0.0.1:8000/docs). See the [API reference](docs/API.md)
for route details, mock tokens, and request and response examples.

The starting data contains four quests, two per regular user. Restarting the
server restores those four quests and clears all changes.

## Tests

```bash
python -m pytest -q
```

## Demo

**https://youtu.be/J4FtddvOsOA?si=pAUtmP7vDjnPyOOP**

## Contributions

| Member | Work |
|---|---|
| Jeyhun Naghiyev | API setup and foundation, quest schemas and mock data, authentication and ownership checks, quest listing and retrieval, and related tests |
| Mahammad Mammadli | Quest updates and deletion, public HTML greeting, API and greeting tests, and submission documentation |

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for student IDs and responsibilities.

### Git contribution history

Output of `git shortlog -sn --all` before this README refresh (`92eeb6f`):

```text
    18  Jeyhun Naghiyev
     7  mmahammad57
     1  Ceyhun2056
```
