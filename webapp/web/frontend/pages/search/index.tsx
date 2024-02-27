import React, { useCallback, useEffect, useRef, useState } from "react";

import dynamic from 'next/dynamic';

import style from './fda-510k.module.css'

const ForceGraph = dynamic(() => import('../../components/ForceGraph'), {
    ssr: false,
})

import { useSearchParams } from 'next/navigation'
import { NavBar } from "../../components/Navbar";
import { useRouter } from "next/router";

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
    const router = useRouter();

    const [searchResults, setSearchResults] = useState<NodeData[]>([])

    const [numExtraResults, setNumExtraResults] = useState(0);

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

    useEffect(() => {if (!!search) {searchForNodes(search)}}, [search])

    return <>
        <NavBar />
        <SearchInput onInputChange={(e) => {
            searchForNodes(e)
        }}>
        </SearchInput>
        {searchResults.length > 0 ? <div className={style.SearchResultsWrapper}>
        <div className="table-responsive">
            <table className="table table-striped table-hover">
                <thead>
                    <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Device Name</th>
                    <th scope="col">Date Received</th>
                    <th scope="col">Product Code</th>
                    </tr>
                </thead>
                <tbody>
                    {searchResults.map(node => {
                        return <tr className={style.tableRow} onClick={
                            (e: any) => {
                                e.preventDefault()
                                router.push(`/devices?id=${node.id}`)
                            }}>
                            <th scope="row">{node.id}</th>
                            <td>{node.name}</td>
                            <td>{node.date}</td>
                            <td>{node.product_code}</td>
                        </tr>
                    })}
                </tbody>
            </table>
            {numExtraResults > 0 &&
            <p>
                {numExtraResults} more results...
            </p>}
        </div></div> : <p>No results found.</p>}
    </>
};

export default DeviceGraph
