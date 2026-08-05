# Virtual Environment Setup

Use this guide to create a Python virtual environment, install the project dependencies, and run the app.

The dependency file in this project is named `requirements.txt`.

## Windows PowerShell

From the project folder:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python app.py
```

Open this URL in your browser:

```text
http://127.0.0.1:5050
```

If PowerShell blocks activation scripts, run this once and try activating again:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You can also install without activating by using the venv Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

## macOS or Linux

From the project folder:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Open this URL in your browser:

```text
http://127.0.0.1:5050
```

## Stop or Exit

Stop the running Flask app with `Ctrl+C`.

Deactivate the virtual environment:

```bash
deactivate
```
