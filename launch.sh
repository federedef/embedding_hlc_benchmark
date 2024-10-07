#!/usr/bin/env bash
export EXEC_PATH=$FSCRATCH/RARE_testing
export CODE_PATH=~/projects/RARE/src
export INPUT_PATH=~/projects/RARE_testing/dataset
export REPORT_PATH=~/projects/RARE_testing/report

datasets="ecoli_STRING_700 karate_club lesmis"
datasets="karate_club lesmis ecoli_STRING_700"
datasets="human_STRING_900 human_STRING_700"
if [ "$1" == "d" ] ; then
    # Preparing the datasets
    source ~soft_bio_267/initializes/init_python
    # get datasets
    for dataset in $datasets ; do
        cp ~/projects/network_hlc_benchmark/dataset/$dataset ./dataset/edges/
    done
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
    source ~soft_bio_267/initializes/init_autoflow
    mkdir -p $EXEC_PATH
    for dataset in $datasets ; do
        variables=`echo -e "
          \\$dataset=$dataset,
          \\$input_path=$INPUT_PATH,
          \\$template=$REPORT_PATH,
          \\$code_path=$CODE_PATH
        " | tr -d [:space:]`
        AutoFlow -e -w ./workflow.sh -V $variables -o $EXEC_PATH/$dataset -m 20gb -t 3-00:00:00 -n cal -s 3 
    done
fi

if [ "$1" == "r" ] ; then
    echo "obtaining results"
    source ~soft_bio_267/initializes/init_python
    mkdir -p results
    for dataset in $datasets ; do
        for report in `find $EXEC_PATH/$dataset -type f -name "*.html" -printf "%p\n"`; do
            report_name=`basename $report`
            cp $report results/$report_name
        done
    done
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