import React, { useCallback, useEffect, useRef, useState } from "react";

import dynamic from 'next/dynamic';

import style from './fda-510k.module.css'
import { NavBar } from "../../components/Navbar";
import { useSearchParams } from "next/navigation";
import { Spinner } from "react-bootstrap";

const ForceGraph = dynamic(() => import('../../components/ForceGraph'), {
    ssr: false,
})

interface NodeData {
    date: string;
    id: string;
    product_code: string;
    name: string;
    generic_name: string;
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

const findNode = (graphData: GraphData, nodeId: string) => {
    return graphData.nodes.find((node: { id: string }) => node.id === nodeId)
}

const PredicateGraph = ({graphData, selectedNode, setSelectedNode, setSelectedNodeData} : PredicateGraphProps) => {
    const handleClick = useCallback((node: any) => {
        setSelectedNode(node.id)
        setSelectedNodeData(findNode(graphData, node.id))
    }, [graphData]);

    return graphData?.links?.length > 0 ?
        <ForceGraph
            graphData={graphData as any}
            nodeLabel={(node: any) => `Name: ${node.name}<br>ID: ${node.id}<br>Date: ${node.date}<br>Category: ${node.product_code}<br>Recalls: ${node?.recalls?.length ? node.recalls.map((recall) => "<br>" + recall.reason) : "None"}`}
            // nodeAutoColorBy="product_code"
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            dagMode="zout"
            dagLevelDistance={20}
            nodeVal={(node: any) => node.id === selectedNode ? 10 : 1}
            onNodeClick={handleClick}
            nodeCanvasObject={(node: any, ctx: any, globalScale: any) => {
                const label = node.id;
                const fontSize = 12 / globalScale;
                ctx.font = `${fontSize}px Sans-Serif`;
                const textWidth = ctx.measureText(label).width;
                const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';

                ctx.beginPath();
                ctx.arc(node.x, node.y, node.id === selectedNode ? 10 : 5, 0, 2 * Math.PI, false);
                // color by recall status
                ctx.fillStyle = node.recalls.length > 0 ? "#e62525" : "#a8c2e3";
                // ctx.fillStyle = node.color;
                ctx.fill();

                if (node.id === selectedNode) {
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#003300';
                    ctx.stroke();
                }

                node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
            }}
        /> : <div className={style.missingPredicatesDisclaimerWrapper}>
            <p className={style.missingPredicatesDisclaimer}>No predicate devices could be found.</p>
            {/* TODO: add link to explanation here */}
        </div>
}

export const DeviceGraph = () => {
    const [graphData, setGraphData] = useState<GraphData & { product_descriptions: any; }>(
        { links: [], nodes: [], product_descriptions: {} }
    );

    const searchParams = useSearchParams()

    const [selectedNode, setSelectedNode] = useState<string | undefined>();


    useEffect(() => {
        setSelectedNode(searchParams.get("id"));
    }, [searchParams])

    const [selectedNodeData, setSelectedNodeData] = useState<NodeData | undefined>();

    const [searchResults, setSearchResults] = useState<NodeData[]>([])

    const [numExtraResults, setNumExtraResults] = useState(0);

    useEffect(() => {
        fetch(`/api/ancestry/${selectedNode}`).then(response => {
            return response.json();
        }).then(data => {
            // expand the generic names out from the normalized json field
            const expandedNodeData = data.nodes.map((node: any) => {
                return { ...node, generic_name: data.product_descriptions[node.product_code] }
            })
            setGraphData({ ...data, nodes: expandedNodeData });
            setSelectedNodeData(findNode(data, selectedNode))
        }).catch(err => {
            // Do something for an error here
            console.log("Error Reading data " + err);
        });
    }, [selectedNode])

    return <>
        <NavBar></NavBar>
        {searchResults.length > 0 && <div className={style.SearchResultsWrapper}>
            <div className={style.SearchResults}>
                {searchResults.map(node => {
                    return <div key={node.id} className={style.SearchResult} onClick={
                        (e: any) => {
                            setSelectedNode(node.id)
                            setSelectedNodeData(node)
                            setSearchResults([])
                            setNumExtraResults(0)
                        }
                    }>{node.id} - {node.name}</div>
                })}
                {numExtraResults > 0 &&
                    <div className={style.MoreResults}>
                        {numExtraResults} more results...
                    </div>}
            </div>

        </div>}
        <div className={style.InfoSection}>
            <p>Name: {selectedNodeData?.name}</p>
            <p>Device ID: <a href={`https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=${selectedNodeData?.id}`}
                target="_blank" rel="noopener noreferrer">{selectedNode}</a></p>
            <p>Date Recieved: {selectedNodeData?.date} </p>
            <p>Product Code: <a href={
                `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=${selectedNodeData?.product_code}`
            } target="_blank" rel="noopener noreferrer">
                {selectedNodeData?.product_code}
            </a>
            </p>
            {graphData?.product_descriptions && selectedNodeData &&
            <p>Generic Name: {graphData?.product_descriptions?.[selectedNodeData?.product_code]}</p>}
            {selectedNodeData?.recalls && selectedNodeData?.recalls.length > 0 &&
            <p>Recalls: {selectedNodeData?.recalls.map((recall) => <a href={`https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfres/res.cfm?id=${recall.recall_id}`} target="_blank">{recall.reason}</a>)}</p>}
        </div>

        {graphData.nodes.length ? <PredicateGraph
            graphData={graphData}
            selectedNode={selectedNode}
            setSelectedNode={setSelectedNode}
            setSelectedNodeData={setSelectedNodeData}
        /> : <div className={style.LoadingWrapper}>
        <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
        </Spinner>
    </div>}
      
    </>
};

export default DeviceGraph
