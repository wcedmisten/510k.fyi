import React, { useCallback, useEffect, useRef, useState } from "react";

import dynamic from 'next/dynamic';

import style from './fda-510k.module.css'

const ForceGraph = dynamic(() => import('../components/ForceGraph'), {
    ssr: false,
})

const SearchInput = ({ onInputChange }: { onInputChange: (e: any) => void }) => {
    const [searchInput, setSearchInput] = useState("")

    useEffect(() => {
        const getData = setTimeout(() => {
            if (searchInput !== "") {
                onInputChange(searchInput)
            }
        }, 400)

        return () => clearTimeout(getData)
    }, [searchInput])

    return <input className={style.SearchInput} placeholder="Search for a device"
        onChange={e => setSearchInput(e.target.value)}
    />
}

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

export const DeviceGraph = () => {
    const [graphData, setGraphData] = useState<GraphData & { product_descriptions: any; }>(
        { links: [], nodes: [], product_descriptions: {} }
    );

    const [selectedNode, setSelectedNode] = useState<string>("K223649");
    const [selectedNodeData, setSelectedNodeData] = useState<NodeData | undefined>();

    const [searchResults, setSearchResults] = useState<NodeData[]>([])

    const [numExtraResults, setNumExtraResults] = useState(0);

    useEffect(() => {
        fetch(`/api/ancestry/${selectedNode}`).then(response => {
            const json = response.json()
            console.log("data", json)
            return json;
        }).then(data => {
            // expand the generic names out from the normalized json field
            const expandedNodeData = data.nodes.map((node: any) => {
                return { ...node, generic_name: data.product_descriptions[node.product_code] }
            })
            console.log("expandedNodeData", expandedNodeData)
            setGraphData({ ...data, nodes: expandedNodeData });
            setSelectedNodeData(findNode(data, selectedNode))
        }).catch(err => {
            // Do something for an error here
            console.log("Error Reading data " + err);
        });
    }, [selectedNode])

    const findNode = (graphData: GraphData, nodeId: string) => {
        return graphData.nodes.find((node: { id: string }) => node.id === nodeId)
    }

    const searchForNodes = (query: string) => {
        fetch(`/api/search?query=${query}`).then(response => {
            const json = response.json()

            return json;
        }).then(data => {
            // expand the generic names out from the normalized json field
            const nodes = data;
            console.log("nodes", nodes)
            if (nodes.length > 10) {
                setSearchResults(nodes.slice(0, 10))
                setNumExtraResults(nodes.length - 10)
            } else {
                setSearchResults(nodes)
            }
        }).catch(err => {
            // Do something for an error here
            console.log("Error Reading data " + err);
        });
    }

    const handleClick = useCallback((node: any) => {
        setSelectedNode(node.id)
        setSelectedNodeData(findNode(graphData, node.id))
    }, [graphData]);

    return <>
        <SearchInput onInputChange={(e) => {
            searchForNodes(e)
        }}></SearchInput>
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
        </div>

        {console.log("Rendering with", graphData)}

        <ForceGraph
            graphData={graphData as any}
            nodeLabel={(node: any) => `Name: ${node.name}<br>ID: ${node.id}<br>Date: ${node.date}<br>Category: ${node.product_code}`}
            nodeAutoColorBy="product_code"
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
                ctx.fillStyle = node.color;
                ctx.fill();

                if (node.id === selectedNode) {
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#003300';
                    ctx.stroke();
                }

                node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
            }}
        />
    </>
};

export default DeviceGraph
