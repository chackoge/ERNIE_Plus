import time

import click
import networkit as nk

from utils import mapping_to_dict


@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="The tsv edgelist representing a network")
@click.option("--label-mapping", required=False, type=click.Path(exists=True), help="Label mapping for the input nodes")
def get_num_components(network, label_mapping):
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    print(f"there are {graph.numberOfNodes()} nodes in the graph")
    cc = nk.components.ConnectedComponents(graph)
    cc.run()
    num_components = cc.numberOfComponents()
    print(f"there are {num_components} components")
    print(f"the component sizes are {cc.getComponentSizes()}")
    node_id_to_true_id_dict = None
    if(label_mapping is not None):
        node_id_to_true_id_dict = mapping_to_dict(label_mapping)
    for component_num,component in enumerate(cc.getComponents()):
        if(len(component) < 100):
            if(label_mapping is not None):
                translated_component = [node_id_to_true_id_dict[int(node_id)] for node_id in component]
                print(f"{component_num}: {translated_component}")
            else:
                print(f"{component_num}: {component}")


if __name__ == "__main__":
    get_num_components()
