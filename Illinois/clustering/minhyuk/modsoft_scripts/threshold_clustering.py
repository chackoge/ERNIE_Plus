import json

import click

@click.command()
@click.option("--modsoft-output", required=True, type=click.Path(exists=True), help="Modsoft clustering output")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output cluster file prefix")
@click.option("--threshold", required=True, type=float, help="Minimum threshold for cluster membersihp")
def threshold_clustering(modsoft_output, output_prefix, threshold):
    ''' This is the main function that takes in a modsoft output and
    writes a thresholded overlaping cluster matrix where the rows are nodes and
    the columns are clusters where row i contains all the cluster numbers that i
    has probability greater than the input threshold of belonging in.
    '''
    with open(output_prefix, "w") as fw:
        with open(modsoft_output, "r") as f:
            for line_number,current_line in enumerate(f):
                current_line_arr = current_line[1:len(current_line) - 2].split(",")
                current_line_tuple_arr = []
                for element in current_line_arr:
                    current_element_arr = element.split(":")
                    current_tuple = (current_element_arr[0].strip(), float(current_element_arr[1]))
                    if(float(current_element_arr[1]) > threshold):
                        # this is the array that gets output on every line where current_tuple contains
                        # the cluster number and probability in that order
                        current_line_tuple_arr.append(current_tuple)
                if(len(current_line_tuple_arr) > 0):
                    current_line_tuple_arr.sort(key=lambda element: element[1], reverse=True)
                    fw.write(str(line_number) + " ")
                    for cluster_tuple in current_line_tuple_arr:
                        fw.write(str(cluster_tuple[0]) + " ")
                    fw.write("\n")

if __name__ == "__main__":
    threshold_clustering()
