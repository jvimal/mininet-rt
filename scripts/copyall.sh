file="$1"
where="$2"
# default copies to root directory
echo Copying $file scripts to all hosts
for i in `seq 1 10`; do
  sudo cp $file /var/lib/vz/private/$i/$where
done

