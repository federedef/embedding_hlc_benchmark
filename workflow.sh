%launch_RARE_[baseline;justnet;justcom;justcom_lou;netcom;netcom_lou]){
	resources: -c 20 -m 100gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	source ~/dev_py/myenv/bin/activate
	export PATH=$code_path:$PATH
	# r for neigh 
	# m for comm
	# t for role
	if [ "(*)" == "justnet" ] ; then
		r=1
		m=0
		# t=0
	elif [ "(*)" == "justcom" -o "(*)" == "justcom_lou" ] ; then
		r=0
		m=1
		# t=0
	elif [ "(*)" == "juststr" ] ; then
		r=0
		m=0
		# t=1
	elif [ "(*)" == "netcom" -o "(*)" == "netcom_lou" ] ; then
		r=1
		m=1
		# t=0
	elif [ "(*)" == "baseline" ] ; then
		r=0
		m=0
		# t=0
	elif [ "(*)" == "new_tanimoto" ] ; then
		r="0.25"
		m=1
		# t=0
	fi
	echo [cpu]
	if [ "(*)" == "justcom_lou" -o "(*)" == "netcom_lou" ] ; then
		group_nodes=$input_path/clusters/louvain_$dataset
	else 
		group_nodes=$input_path/clusters/$dataset
	fi
	?
	netanalyzer -i $input_path/edges/$dataset -l 'nodes' -k "comm_aware" \
	--group_nodes $group_nodes \
	-u 'nodes' -K ./kernel_matrix_bin \
	--embedding_add_options "'workers':16, 'window':10, 'num_walks':10, \
	'neigh_w':$r, 'comm_w':$m, 'walk_length': 100, 'dimensions': 128, 'hs': 1, 'sg': 1, 'negative': 0" \
	--embedding_coords
	mv kernel_matrix_bin_rowIds embedding_matrix.lst
	mv kernel_matrix_bin.npy embedding_matrix.npy
	#CRARE.py --input $input_path/edges/$dataset --labels $input_path/clusters/$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
	#CRARE.py --input $input_path/edges/$dataset --labels $input_path/clusters/louvain_$dataset --output "./" --dataset "walks_(*)" -m $m -r $r -t $t > output_verbose
	#rm output_verbose
}

%get_spearman_corr){
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

%get_quality_from_external_[baseline;justnet;justcom;justcom_lou;netcom;netcom_lou]){
	resources: -c 20 -m 50gb -A exclusive
	source ~soft_bio_267/initializes/init_python
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
	echo -e "baseline;launch_RARE_baseline)/embedding_matrix,\
	justnet;launch_RARE_justnet)/embedding_matrix,\
	justcomm;launch_RARE_justcom)/embedding_matrix,\
	justcomm_lou;launch_RARE_justcom_lou)/embedding_matrix,\
	netcom;launch_RARE_netcom)/embedding_matrix,\
	netcom_lou;launch_RARE_netcom_lou)/embedding_matrix" > emb_data

	if [ -s $external_path ] ; then
		?
		report_quality.py -r relative_quality_metrics -i quality_metrics -t $template/quality.txt \
		--emb_pos `cat emb_data` \
		--communities "HLC;$input_path/clusters/$dataset,Louvain;$input_path/clusters/louvain_$dataset" \
		--external_groups $external_path -o "quality_metrics_$dataset"
	fi
}


