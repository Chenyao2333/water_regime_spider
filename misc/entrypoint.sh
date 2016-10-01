#! /bin/bash

FILE_PATH=$(readlink -f $0)
BASE_DIR=$(dirname $(dirname $FILE_PATH))
INITIAL_DB=$BASE_DIR/misc/test_01.db
DB=$BASE_DIR/databases/test_01.db

if [ ! -f $DB ]
then
    echo "Copying database file."
    cp $INITIAL_DB $DB
fi

/usr/bin/supervisord
