launch_RARE_[baseline;justnet;justcom;justcom_lou;netcom;netcom_lou]){
	resources: -c 20 -m 100gb
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	# r for neigh 
	# m for comm
	# t for role
	if [ "(*)" == "justnet" ] ; then
		r=1
		m=0
	elif [ "(*)" == "justcom" -o "(*)" == "justcom_lou" ] ; then
		r=0
		m=1
	elif [ "(*)" == "juststr" ] ; then
		r=0
		m=0
	elif [ "(*)" == "netcom" -o "(*)" == "netcom_lou" ] ; then
		r=1
		m=1
	elif [ "(*)" == "baseline" ] ; then
		r=0
		m=0
	elif [ "(*)" == "new_tanimoto" ] ; then
		r="0.25"
		m=1
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
}

get_spearman_corr){
	resources: -c 20 -m 20gb 
	source ~soft_bio_267/initializes/init_python
	export PATH=$template:$PATH
	echo [cpu]
	?
    report_corr.py -R launch_RARE_justnet)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -r launch_RARE_justnet)/embedding_matrix.lst -g launch_RARE_netcom)/embedding_matrix.lst -t $template/corr.txt -o "justnet_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_netcom)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_netcom)/embedding_matrix.lst  -t $template/corr.txt -o "justcom_netcom_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justnet)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_justnet)/embedding_matrix.lst -t $template/corr.txt -o "justcom_justnet_$dataset"
	report_corr.py -R launch_RARE_justcom)/embedding_matrix.npy -G launch_RARE_justcom)/embedding_matrix.npy -r launch_RARE_justcom)/embedding_matrix.lst -g launch_RARE_justcom)/embedding_matrix.lst -t $template/corr.txt -o "justcom_justcom_$dataset"
}

get_quality_from_external_[baseline;justnet;justcom;justcom_lou;netcom;netcom_lou]){
	resources: -c 20 -m 50gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	PATH=$scripts_code:$PATH
	exectype=(*)
	if [ -s $external_path ] ; then
		?
		get_quality_by_external_group.py --input $input_path/edges/$dataset -m !launch_RARE_*!/embedding_matrix.npy -l !launch_RARE_*!/embedding_matrix.lst --external_groups $external_path
		# Add tags to group and metrics
		if [ -s quality_metrics ] ; then
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' quality_metrics > final_quality_metrics
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' relative_quality_metrics > final_relative_quality_metrics
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' group_distance > final_group_distance
		fi
	fi
}

ranking_groups_[baseline;justnet;justcom;justcom_lou;netcom;netcom_lou]){
	resources: -m 50gb 
	source ~soft_bio_267/initializes/init_python
	text2binary_matrix -i $input_path/edges/$dataset -t pair -O bin -o adj_matrix
	text2binary_matrix -i !launch_RARE_*!/embedding_matrix.npy -t "bin" -O "bin" --coords2kernel "dotProduct" -o kernel --cosine_normalization
	exectype=(*)
	aggregate_column_data -i $external_path -x 1 -a 2 > seeds
	?
	ranker -k kernel.npy -n !launch_RARE_*!/embedding_matrix.lst --adj_matrix adj_matrix.npy --seed_nodes seeds \
		--score2pvalue "logistic" --representation_seed_metric "bayesian" -t 20 --seed_presence "remove"
	# ranker -k kernel.npy -n !launch_RARE_*!/embedding_matrix.lst --adj_matrix adj_matrix.npy --seed_nodes seeds --representation_seed_metric "mean" -t 5 --seed_presence "remove"
	if [ -s ranked_genes_all_candidates ] ; then
		awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' ranked_genes_all_candidates > final_ranked_genes_all_candidates
	fi
}

report_quality){
	source ~soft_bio_267/initializes/init_python
	PATH=$template:$PATH
	cat !get_quality_from_external_!/final_quality_metrics > quality_metrics
	cat !get_quality_from_external_!/final_relative_quality_metrics > relative_quality_metrics
	cat !get_quality_from_external_!/final_group_distance > final_group_distance
	cat !ranking_groups_!/final_ranked_genes_all_candidates > final_ranked_genes_all_candidates
	echo -e "baseline;launch_RARE_baseline)/embedding_matrix,\
	justnet;launch_RARE_justnet)/embedding_matrix,\
	justcom;launch_RARE_justcom)/embedding_matrix,\
	justcom_lou;launch_RARE_justcom_lou)/embedding_matrix,\
	netcom;launch_RARE_netcom)/embedding_matrix,\
	netcom_lou;launch_RARE_netcom_lou)/embedding_matrix" > emb_data
	echo -e "baseline;get_quality_from_external_baseline)/distance_matrix,\
	justnet;get_quality_from_external_justnet)/distance_matrix,\
	justcom;get_quality_from_external_justcom)/distance_matrix,\
	justcom_lou;get_quality_from_external_justcom_lou)/distance_matrix,\
	netcom;get_quality_from_external_netcom)/distance_matrix,\
	netcom_lou;get_quality_from_external_netcom_lou)/distance_matrix" > dist_data

	if [ -s $external_path ] ; then
		?
		report_quality.py -r relative_quality_metrics -i quality_metrics -t $template/quality.txt \
		--emb_pos `cat emb_data` \
		--communities "HLC;$input_path/clusters/$dataset,Louvain;$input_path/clusters/louvain_$dataset" \
		--external_groups $external_path -o "quality_metrics_$dataset" \
		--external_group_description "$external2description_path" \
		--group_distance final_group_distance \
		--embedding_distances `cat dist_data` \
		--gene_names_ens $name_nodes \
		--gene_names_symbol $name_nodes_symbol \
		--prioritization final_ranked_genes_all_candidates
	fi
}


