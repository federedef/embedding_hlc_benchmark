launch_RARE_[clust;all]){
	resources: -n "$node_type" -m "$memory" -c "$cpu" -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	?
	CRARE.py $input_path/edges/$dataset $input_path/clusters/$dataset # flags
}

get_spearman_corr){
	resources: -n "$node_type" -m "$memory" -c "$cpu" -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	?
    report_corr.py 
}
