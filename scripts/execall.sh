
cmd=$1
for i in `seq 1 10`; do
  sudo vzctl exec $i $cmd
done

