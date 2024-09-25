## Install and Run
1. Clone the repository
2. Create virtual environment
```bash
python3 -m venv .venv
```
3. Activate the virtual environment
```bash
.venv\Scripts\activate
```
4. Run the following command to install the dependencies
```bash
pip install -r requirements.txt
```
5. Run the command to make migrations and migrate
```bash
python manage.py makemigrations
```
6. Run the command to run the server
```bash
python manage.py runserver
```
