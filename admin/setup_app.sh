# Setting up the application
if [ $# -eq 1 ]
  then
    cd $1
else
    echo "Application directory is not specified. Using current directory!"
fi
echo "source venv-metadb/bin/activate" >> ~/.bashrc
virtualenv -p python3 ../venv-metadb
source ../venv-metadb/bin/activate
pip install -r requirements
pip install -r requirements_dev
python manage.py init_db
python manage.py init_test_db
