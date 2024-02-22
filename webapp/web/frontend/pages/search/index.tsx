import React, { useCallback, useEffect, useRef, useState } from "react";

import dynamic from 'next/dynamic';

import style from './fda-510k.module.css'

const ForceGraph = dynamic(() => import('../../components/ForceGraph'), {
    ssr: false,
})

import { useSearchParams } from 'next/navigation'
import { NavBar } from "../../components/Navbar";

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

    const searchParams = useSearchParams()

    const search = searchParams.get('q')

    useEffect(() => searchForNodes(search), [search])

    return <>
        <NavBar />
        <SearchInput onInputChange={(e) => {
            searchForNodes(e)
        }}>
        </SearchInput>
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
                <p>Recalls: {selectedNodeData?.recalls.map((recall) => <p key={recall.recall_id}>{recall.reason}</p>)}</p>}
        </div>
    </>
};

export default DeviceGraph
