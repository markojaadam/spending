#!/usr/bin/env bash
# deploy_db.sh

# Default values
REBUILD=0
DATABASE="spending"
HOST="localhost"
TARGET="api"
USERNAME="test"
PASSWORD="test"
HELP_TXT="Command line tool to deploy/rebuild spending database.

OPTIONS:
	-r/--rebuild: drop the existing schemas and rebuild (default: 0)
	-d/--database=your_database_name: target PostgreSQL database (default: spending)
	-h/--host=database host (default: localhost)
	-t/--target=api/all: choose between rebuild/deploy everything or only api schema and functions
	-u/--username: username for the database (default: meh)
	-p/--password: password for the database (default: meh)"

for arg in "$@"
do
    case $arg in
        -r|--rebuild)
        REBUILD=1
        shift
        ;;
        -d=*|--database=*)
        DATABASE="${arg#*=}"
        shift
        ;;
        -h=*|--host=*)
        HOST="${arg#*=}"
        shift
        ;;
        -t=*|--target=*)
		if [[ "${arg#*=}" != "api" ]] && [[ "${arg#*=}" != "all" ]]; then
			echo "Invalid target: \"${arg#*=}\"! choose from all/api!"
			exit 1
		fi
        TARGET="${arg#*=}"
        shift
        ;;
        -u=*|--username=*)
        USERNAME="${arg#*=}"
        shift
        ;;
        -p=*|--password=*)
        PASSWORD="${arg#*=}"
        shift
        ;;
		-h|--help)
		echo "$HELP_TXT"
		exit 0
		shift
		;;
		*)
		echo "Invalid option: ${arg%%=*}"
		exit 1
        shift
        ;;
    esac
done

execute_query() {
	echo "Running PGPASSWORD=$PASSWORD psql -h $HOST -U $USERNAME -d $DATABASE -f $1"
	PGPASSWORD=${PASSWORD} psql -h ${HOST} -U ${USERNAME} -d ${DATABASE} -f $1
	echo $'\n'
}

echo "# Rebuild: $REBUILD"
echo "# Database: $DATABASE"
echo "# Host: $HOST"
echo "# Target: $TARGET"
echo "# Username: $USERNAME"
echo "# Password: $PASSWORD"
echo $'\n'

if [[ "$TARGET" == "all" ]]; then
	if [[ ${REBUILD} == 1 ]]; then
		execute_query drop_all.sql
	fi
	for sql_script in tbl.sql api.sql static/*.sql;	do
		execute_query ${sql_script}
	done
elif [[ "$TARGET" == "api" ]]; then
	if [[ ${REBUILD} == 1 ]]; then
		execute_query drop_api.sql
	fi
	for sql_script in api.sql static/*.sql; do
			execute_query ${sql_script}
	done
fi
exit 0
