bin="$1"
echo Copying $bin scripts to all hosts
for i in `seq 1 10`; do
  sudo cp $bin /var/lib/vz/private/$i/bin
done

