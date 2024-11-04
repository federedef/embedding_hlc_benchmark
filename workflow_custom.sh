launch_RARE_[net;com]){
	resources: -c 20 -m 100gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$code_path:$PATH
	?
	jumpwalk.py --input $input_path/edges/$dataset --labels $input_path/clusters/$dataset --output "./" > output_verbose
}

get_spearman_corr){
	resources: -c 20 -m 20gb -A exclusive
	source ~soft_bio_267/initializes/init_python
	export PATH=$template:$PATH
	echo [cpu]
	# With a simple comparison in angles
	?
    report_corr.py -R launch_RARE_net)/embedding_matrix.npy -G launch_RARE_com)/embedding_matrix.npy -r launch_RARE_net)/embedding_matrix.lst -g launch_RARE_com)/embedding_matrix.lst -t $template/corr.txt -o "net_com_$dataset"
}

get_quality_from_external_[net;com]){
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
			awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' quality_metrics > tmp && mv tmp quality_metrics
			#awk -v exectype="$exectype" 'BEGIN{FS="\t";OFS="\t"}{print exectype,$0}' relative_pos > tmp && mv tmp relative_pos
		fi
	fi
}

report_quality){
	source ~soft_bio_267/initializes/init_python
	PATH=$template:$PATH
	cat !get_quality_from_external_!/quality_metrics > quality_metrics
	# cat !get_quality_from_external_!/relative_pos > relative_pos
	if [ -s $external_path ] ; then
		?
		report_quality.py -i quality_metrics -t $template/quality.txt -o "quality_metrics_$dataset"
	fi
}

