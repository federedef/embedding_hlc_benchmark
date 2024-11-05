launch_RARE_[baseline;justnet;justcom;juststr;netcom;new_tanimoto]){
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
	elif [ "(*)" == "juststr" ] ; then
		r=0
		m=0
		t=1
	elif [ "(*)" == "netcom" ] ; then
		r=1
		m=1
		t=0
	elif [ "(*)" == "baseline" ] ; then
		r=0
		m=0
		t=0
	elif [ "(*)" == "new_tanimoto" ] ; then
		r="0.25"
		m=1
		t=0
	fi
	echo [cpu]
	# Obtaining embedding model coords
	if [ "(*)" == "ori_louvain" ] ; then
		?
		CRARE.py --input $input_path/edges/$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
	else 
		CRARE.py --input $input_path/edges/$dataset --labels $input_path/clusters/$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
	fi
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

get_quality_from_external_[baseline;justnet;justcom;juststr;netcom;new_tanimoto]){
	resources: -c 20 -m 50gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	source ~/dev_py/myenv/bin/activate
	PATH=$scripts_code:$PATH
	exectype=(*)
	# Now we obtain results for external groups
	if [ -s $external_path ] ; then
		?
		get_quality_by_external_group.py --input $input_path/edges/$dataset -m !launch_RARE_*!/embedding_matrix.npy -l !launch_RARE_*!/embedding_matrix.lst --external_groups $external_path
		# Add tags to group and metrics
		if [ -s quality_metrics ] ; then
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' quality_metrics > final_quality_metrics
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' relative_quality_metrics > final_relative_quality_metrics
			#awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' relative_pos > tmp && mv tmp relative_pos
		fi
	fi
}

report_quality){
	source ~soft_bio_267/initializes/init_python
	PATH=$template:$PATH
	cat !get_quality_from_external_!/final_quality_metrics > quality_metrics
	cat !get_quality_from_external_!/final_relative_quality_metrics > relative_quality_metrics
	if [ -s $external_path ] ; then
		?
		report_quality.py -r relative_quality_metrics -i quality_metrics -t $template/quality.txt -o "quality_metrics_$dataset"
	fi
}


