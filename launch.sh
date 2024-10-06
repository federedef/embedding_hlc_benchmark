#!/usr/bin/env bash
export EXEC_PATH=$FSCRATCH/RAREtesting
export CODE_PATH=~/projects/RARE/src
export INPUT_PATH=~/projects/RAREtesting/dataset

datasets="ecoli_STRING_700 ecoli_STRING_900 human_STRING_700 human_STRING_900"
if [ "$1" == "d" ] ; then
    # Preparing the datasets
    source ~soft_bio_267/initializes/init_python
    # get datasets
    cp ~/projects/network_hlc_benchmark/dataset/human_STRING_* ./dataset/edges/
    cp ~/projects/network_hlc_benchmark/dataset/ecoli_STRING_* ./dataset/edges/
    # create translators
    for dataset in $datasets ; do
        cut -f 1 ./dataset/edges/$dataset > tmp && cut -f 2 ./dataset/edges/$dataset >> tmp
        sort tmp | uniq | awk 'BEGIN{OFS="\t"}{print $1,NR}' > ./dataset/translators/$dataset
        rm tmp
    done
    # get communities
    for dataset in $datasets ; do
        echo "$dataset"
        cp $FSCRATCH/network_hlc_benchmark/$dataset/test.py_0000/formated_cls ./dataset/clusters/
        echo "#nodes labels" > ./dataset/clusters/$dataset
        awk 'BEGIN{OFS=" "}{print $2,$1}' ./dataset/clusters/formated_cls >> ./dataset/clusters/$dataset
        rm ./dataset/clusters/formated_cls 
    done
    # translate datasets and communities
    for dataset in $datasets ; do
        sed -i "s/\t/ /g" ./dataset/edges/$dataset
        standard_name_replacer -i ./dataset/edges/$dataset -I ./dataset/translators/$dataset -c 1,2 -u -s " " > tmp && mv tmp ./dataset/edges/$dataset
        standard_name_replacer -i ./dataset/clusters/$dataset -I ./dataset/translators/$dataset -s " " -c 1 -u > tmp && mv tmp ./dataset/clusters/$dataset
    done
fi

if [ "$1" == "wf" ] ; then
    for dataset in $datasets ; do
        variables=`echo -e "
          \\$dataset=$DATASET,
          \\$input_path=$INPUT_PATH,
          \\=,
          \\=,
          \\=
        " | tr -d [:space:]`
        AutoFlow -e -w ./workflow.sh -V $variables -o $EXEC_PATH/$dataset -m 20gb -t 3-00:00:00 -n cal -s 3 
    done
fi

if [ "$1" == "r" ] ; then
    echo "obtaining results"
fi

if [ "$1" == "check" ] ; then
  source ~soft_bio_267/initializes/init_autoflow
  echo "$EXEC_PATH"
  for folder in `ls $EXEC_PATH` ; do
    echo "$folder"
    flow_logger -w -e $EXEC_PATH/$folder -r all
  done
fi

if [ "$1" == "recover" ] ; then
  source ~soft_bio_267/initializes/init_autoflow
  for folder in `ls $EXEC_PATH` ; do
    flow_logger -w -e $EXEC_PATH/$folder --sleep 0.1 -l -p 
  done
fi