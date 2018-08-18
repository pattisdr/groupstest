# groupstest
Nested Relationships w/ Django + Django Guardian + Django Groups Manager

### Setup Environment

```bash
virtualenv -p `which python3` env
source ./env/bin/activate
pip install -r requirements.txt
```

### Create/Reset the database

```bash
rm -f groupstest/migrations/0001_initial.py && python manage.py reset_db --noinput && python manage.py makemigrations && python manage.py migrate
```

### Run Tests

```bash
python manage.py test -v 2
```

