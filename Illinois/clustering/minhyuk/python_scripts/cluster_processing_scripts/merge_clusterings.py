import glob

import click

from python_scripts.utils.utils import file_to_dict,write_new_sorted_cluster_dict


@click.command()
@click.option("--clustering-folder", required=True, type=click.Path(exists=True), help="Folder containing all clusterings to be merged")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def merge_clusterings(clustering_folder, output_prefix):
    '''This is the main function that will take in a folder
    and merge all clusterings, which are represeting by files with a .clustering suffix
    '''
    merged_cluster_to_id_dict = {}
    cluster_id = 0
    for clustering_filename in glob.glob(f"{clustering_folder}/*.clustering"):
        current_cluster_to_id_dict = file_to_dict(clustering_filename)["cluster_to_id_dict"]
        for _,cluster_member_arr in current_cluster_to_id_dict.items():
            merged_cluster_to_id_dict[cluster_id] = cluster_member_arr
            cluster_id += 1

    write_new_sorted_cluster_dict(merged_cluster_to_id_dict, [], f"{output_prefix}/merged")


if __name__ == "__main__":
    merge_clusterings()
