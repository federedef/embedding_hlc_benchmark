#!/usr/bin/env bash
export EXEC_PATH=$FSCRATCH/RARE_testing
export CODE_PATH=~/projects/RARE/src 
mkdir -p $EXEC_PATH
export INITIAL_PATH=`pwd`
export INPUT_PATH=$INITIAL_PATH/dataset
export REPORT_PATH=$INITIAL_PATH/report
datasets="human_STRING_900 human_STRING_700"
#datasets="human_STRING_700"


if [ "$1" == "d" ] ; then
    # Preparing the datasets
    source ~soft_bio_267/initializes/init_python
    # # get datasets
    # for dataset in $datasets ; do
    #     cp ~/projects/network_hlc_benchmark/dataset/$dataset ./dataset/edges/
    # done
    # # create translators
    # for dataset in $datasets ; do
    #     cut -f 1 ./dataset/edges/$dataset > tmp && cut -f 2 ./dataset/edges/$dataset >> tmp
    #     sort tmp | uniq | awk 'BEGIN{OFS="\t"}{print $1,NR}' > ./dataset/translators/$dataset
    #     rm tmp
    # done
    #get communities HLC
    # for dataset in $datasets ; do
    #     echo "$dataset"
    #     cp $FSCRATCH/network_hlc_benchmark/$dataset/test.py_0000/formated_cls ./dataset/clusters/
    #     awk 'BEGIN{OFS=" "}{print $2,$1}' ./dataset/clusters/formated_cls > ./dataset/clusters/$dataset
    #     rm ./dataset/clusters/formated_cls 
    # done

    # # get communities louvain
    # for dataset in $datasets ; do
    #     netanalyzer -i ./dataset/edges/$dataset -f "pair" -b "louvain" -s " " --output_build_clusters "./dataset/clusters/tmp_louvain_$dataset"
    #     awk 'BEGIN{OFS=" "}{print $2,$1}' ./dataset/clusters/tmp_louvain_$dataset > ./dataset/clusters/"louvain_$dataset"
    #     rm ./dataset/clusters/tmp_louvain_$dataset
    # done

    # translate datasets and communities
    for dataset in $datasets ; do
        #sed -i "s/\t/ /g" ./dataset/edges/$dataset
        #standard_name_replacer -i ./dataset/edges/$dataset -I ./dataset/translators/$dataset -c 1,2 -u -s " " > tmp && mv tmp ./dataset/edges/$dataset
        standard_name_replacer -i ./dataset/clusters/$dataset -I ./dataset/translators/$dataset -s " " -c 1 -u > tmp && mv tmp ./dataset/clusters/$dataset
    done

    # # get externals
    # wget https://reactome.org/download/current/Ensembl2Reactome.txt -O ./dataset/externals/reactome
    # for protein in "human_STRING_700" "human_STRING_900" ; do
    #     sed "s/9606.ENS/ENS/g" ./dataset/translators/"$protein" > tmp && mv tmp ./dataset/translators/"$protein"
    #     grep "ENSP" ./dataset/externals/reactome | grep "Homo sapiens" |
    #      awk 'BEGIN{OFS="\t";FS="\t"}{print $2,$1}' | standard_name_replacer -i - -I ./dataset/translators/"$protein" -c 2 -u > ./dataset/externals/"$protein"
    # done
    # for protein in "human_STRING_700" "human_STRING_900" ; do
    #     echo "$protein"
    #     standard_name_replacer -i ./dataset/externals/zampieri -I ./dataset/translators/"$protein" -c 2 -u > ./dataset/externals/"$protein"_zampieri
    #     standard_name_replacer -i ./dataset/externals/buphamalai -I ./dataset/translators/"$protein" -c 2 -u > ./dataset/externals/"$protein"_buphamalai
    # done
fi

if [ "$1" == "wf" ] ; then
    source ~soft_bio_267/initializes/init_autoflow
    mkdir -p $EXEC_PATH
    for dataset in $datasets ; do
        variables=`echo -e "
          \\$dataset=$dataset,
          \\$input_path=$INPUT_PATH,
          \\$template=$REPORT_PATH,
          \\$code_path=$CODE_PATH,
          \\$external_path=$INPUT_PATH/externals/${dataset},
          \\$scripts_code=$INITIAL_PATH/scripts
        " | tr -d [:space:]`
        AutoFlow -e -w ./workflow.sh -V $variables -o $EXEC_PATH/$dataset -m 20gb -t 3-00:00:00 -n cal -s 3 
    done
fi

if [ "$1" == "r" ] ; then
    echo "obtaining results"
    source ~soft_bio_267/initializes/init_python
    echo $EXEC_PATH
    #export EXEC_PATH=$FSCRATCH/custom_random
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