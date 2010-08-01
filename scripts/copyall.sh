file="$1"
where="$2"
# Number of containers
n=`sudo vzlist -a -H | wc -l`
# default copies to root directory
echo Copying $file scripts to all hosts
for i in `seq 1 $n`; do
  sudo cp $file /var/lib/vz/private/$i/$where
done

