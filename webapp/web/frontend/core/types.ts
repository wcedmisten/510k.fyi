interface Recall {
    recall_id: string;
    reason: string;
}

interface NodeData {
    date: string;
    id: string;
    product_code: string;
    name: string;
    generic_name: string;
    recalls: Recall[];
}

interface GraphData {
    nodes: NodeData[];
    links: any[];
}

interface PredicateGraphProps {
    graphData: GraphData;
    selectedNode: any;
    setSelectedNode: any;
    setSelectedNodeData: any;
}
