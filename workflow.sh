launch_RARE_[justnet;justcom;netcom]){
	resources: -c 20 -m 100gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	# r for neigh 
	# m for comm
	# t for role
	if [ "(*)" == "justnet" ] ; then
		r=1
		m=0
		t=0
	elif [ "(*)" == "justcom" ] ; then
		r=0
		m=1
		t=0
	elif [ "(*)" == "netcom" ] ; then
		r=1
		m=1
		t=0
	fi
	echo [cpu]
	# Obtaining embedding model coords
	?
	CRARE.py --input $input_path/edges/$dataset --labels $input_path/clusters/$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
}

get_spearman_corr){
	resources: -c 20 -m 20gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$template:$PATH
	echo [cpu]
	# With a simple comparison in angles
	?
    report_corr.py -R launch_RARE_justnet)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -r launch_RARE_justnet)/embedding_matrix.lst -g launch_RARE_netcom)/embedding_matrix.lst -t $template/corr.txt -o "justnet_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_netcom)/embedding_matrix.lst  -t $template/corr.txt -o "justcom_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justnet)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_justnet)/embedding_matrix.lst -t $template/corr.txt -o "justcom_justnet_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justcom)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_justcom)/embedding_matrix.lst -t $template/corr.txt -o "justcom_justcom_$dataset"
}

get_quality_from_external_[justnet;justcom;netcom]){
	source ~soft_bio_267/initializes/init_python
	PATH=$scripts_code:$PATH
	exectype=(*)
	# Now we obtain results for external groups
	if [ -s $external_path ] ; then
		?
		get_quality_by_external_group.py -m !launch_RARE_*!/embedding_matrix.npy -l !launch_RARE_*!/embedding_matrix.lst --external_groups $external_path
		# Add tags to group and metrics
		if [ -s quality_metrics ] ; then
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' quality_metrics > tmp && mv tmp quality_metrics
		fi
	fi
}

report_quality){
	source ~soft_bio_267/initializes/init_python
	PATH=$template:$PATH
	cat !get_quality_from_external_!/quality_metrics > quality_metrics
	if [ -s $external_path ] ; then
		?
		report_quality.py -i quality_metrics -t $template/quality.txt -o "quality_metrics_$dataset"
	fi
}

