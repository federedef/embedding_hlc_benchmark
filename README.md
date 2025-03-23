# Automatic Workflow: HLC embedding benchmarking

This repository contains a Bash script for managing datasets, running workflows, and obtaining results in a benchmarking for hlc embedding. The script supports dataset preparation, workflow execution, result collection, and pipeline recovery.

## Features

- **Dataset Preparation**: Prepares datasets by generating clusters, creating translators, and downloading external data (e.g., Reactome data).
- **Workflow Execution**: Automates the execution of workflows for specified datasets using AutoFlow.
- **Result Collection**: Collects and organizes the results of workflow executions.
- **Pipeline Monitoring and Recovery**: Includes options to monitor and recover workflows.

## Prerequisites

- **Environment Setup**:
  - The script depends on specific initialization files (`~soft_bio_267/initializes/init_python` and `~soft_bio_267/initializes/init_autoflow`).
  - Ensure the required environment variables and software tools (python library: `py_cmdtabs`, `netanalyzer`, ruby gem: `AutoFlow`) are available.
- **Datasets**:
  - Input datasets must be located or prepared as per the defined paths in the script.

## Usage

### Command-Line Arguments

The script accepts the following arguments to specify the operation mode:

1. **Dataset Preparation (`d`)**:
   Prepares the datasets for processing, including generating clusters, creating translators, and downloading external resources.
   ```bash
   ./launch.sh d
   ```

2. **Workflow Execution (`wf`)**:
   Executes workflows for each dataset using AutoFlow.
   ```bash
   ./launch.sh wf
   ```

3. **Result Collection (`r`)**:
   Gathers the results from workflow executions and copies them to a `results/` directory.
   ```bash
   ./launch.sh r
   ```

4. **Workflow Monitoring (`check`)**:
   Monitors the progress of workflows using `flow_logger`.
   ```bash
   ./launch.sh check
   ```

5. **Workflow Recovery (`recover`)**:
   Recovers failed or incomplete workflows using `flow_logger`.
   ```bash
   ./launch.sh recover
   ```

## Directory Structure

- `dataset/`: Contains the input datasets, edges, clusters, translators, and external resources.
- `report/`: Stores generated reports.
- `results/`: Consolidated results after workflow execution.

## Configuration

### Environment Variables

- `EXEC_PATH`: Path for storing workflow execution files.
- `CODE_PATH`: Path to the code directory.
- `INPUT_PATH`: Path to the input datasets.
- `REPORT_PATH`: Path for saving reports.
- `EDGES_PATH`: Path for networks.
- `HLC_CLUSTER_PATH`: Path for hlc clustering for each network.

### Supported Datasets

By default, the script works with:
- `human_STRING_900`: The human interactome from STRING database with a cutoff of 900.
- `human_STRING_700`: The human interactome from STRING database with a cutoff of 700.

You can modify the `datasets` variable to include additional datasets.

## Workflow Execution Example

To run the workflow:
1. Prepare datasets:
   ```bash
   ./launch.sh d
   ```
2. Execute workflows:
   ```bash
   ./launch.sh wf
   ```
3. Collect results:
   ```bash
   ./launch.sh r
   ```

## Troubleshooting

- **Monitoring Workflows**: Use the `check` argument to inspect the status of workflows.
- **Recovering Workflows**: Use the `recover` argument to resume workflows that may have failed or stopped.

## Acknowledgments

This script leverages tools like AutoFlow, `netanalyzer`, and `flow_logger` for pipeline automation and workflow management.


