if [ $# -ne 2 ]; then
  echo "illegal number of parameters: $#"
else
  curl -X POST -F "login=$1" -F "password=$2" localhost:8080/users
fi