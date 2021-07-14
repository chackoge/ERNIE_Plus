import json

import click

@click.command()
@click.option("--modsoft-output", required=True, type=click.Path(exists=True), help="Modsoft clustering output")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output cluster file prefix")
@click.option("--threshold", required=True, type=float, help="Minimum threshold for cluster membersihp")
def threshold_clustering(modsoft_output, output_prefix, threshold):
    with open(output_prefix, "w") as fw:
        with open(modsoft_output, "r") as f:
            for line_number,current_line in enumerate(f):
                current_line_arr = current_line[1:len(current_line) - 2].split(",")
                current_line_tuple_arr = []
                highest_membership = None
                for element in current_line_arr:
                    current_element_arr = element.split(":")
                    current_tuple = (current_element_arr[0].strip(), float(current_element_arr[1]))
                    if(highest_membership is None or current_tuple[1] > highest_membership[1]):
                        highest_membership = current_tuple
                    if(float(current_element_arr[1]) > threshold):
                        current_line_tuple_arr.append(current_tuple)

                # if(len(current_line_tuple_arr) == 0):
                #     current_line_tuple_arr.append(highest_membership)

                if(len(current_line_tuple_arr) > 0):
                    current_line_tuple_arr.sort(key=lambda element: element[1], reverse=True)
                    fw.write(str(line_number) + " ")
                    for cluster_tuple in current_line_tuple_arr:
                        fw.write(str(cluster_tuple[0]) + " ")
                    fw.write("\n")

if __name__ == "__main__":
    threshold_clustering()
