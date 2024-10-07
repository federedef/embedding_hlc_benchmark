launch_RARE_[justnet;justcom;netcom]){
	resources: -c 20 -m 100gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	if [ "(*)" == "justnet" ] ; then
		r=1
		m=0
		t=0
	elif [ "(*)" == "justcom" ] ; then
		r=0
		m=0
		t=1
	elif [ "(*)" == "netcom" ] ; then
		r=1
		m=1
		t=0
	fi
	echo [cpu]
	?
	CRARE.py --input $input_path/edges/$dataset --labels $input_path/clusters/$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
}

get_spearman_corr){
	resources: -c 20 -m 20gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$template:$PATH
	echo [cpu]
	?
    report_corr.py -R launch_RARE_justnet)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -t $template/corr.txt -o "justnet_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -t $template/corr.txt -o "justcom_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justnet)/embedding_matrix.npy -t $template/corr.txt -o "justcom_justnet_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justcom)/embedding_matrix.npy -t $template/corr.txt -o "justcom_justcom_$dataset"
}
