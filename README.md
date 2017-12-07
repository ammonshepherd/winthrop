# Setup
- To see the examples, run a local web server. The easiest is with Python.
  - `python3 -m http.server`
  - `python -m SimpleHTTPServer 8000`
  - The pages are now viewable at `http://localhost:8000`


# Setting up the Django site
## Creating the virtual environment
- Documentation on the site is a bit messed up; multiple commands are on the same line. Should have each command on a different line and different text.
- had trouble figuring out how to install an older version of python3, I have python3.6.3, so going to try with that.
- Using the new python3.6 way of creating a virtual environment instead of old, virtualenv, or the now depricated pyvenv
- see https://docs.python.org/3/library/venv.html
- activated virtualenv with
  - `python3 -m venv winthrop`
  - `source winthrop/bin/activate`

## Django setup
- set allowed host in local_settings to '127.0.0.1'
- run `python3 manage.py migrate` to set up the database.
- used this site for help understanding what to do: https://tutorial.djangogirls.org/en/django_start_project/

## After this, everything is up and running. Just need a local account...
  - checked commands available with `python3 manage.py help` and found the `createsuperuser` command which works nicely.
  - `python3 manage.py createsuperuser`


## I'm a dufus... The CSV has more fields than just id and text... so, don't really need this Django app up and running now do I.

