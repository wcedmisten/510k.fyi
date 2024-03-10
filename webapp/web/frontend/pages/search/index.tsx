import React, { useEffect, useState } from "react";

import style from './search.module.css'

import { useSearchParams } from 'next/navigation'
import { NavBar } from "../../components/Navbar";
import { useRouter } from "next/router";
import { Button } from "react-bootstrap";

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

export const DeviceGraph = () => {
    const router = useRouter();

    const [offset, setOffset] = useState(0);
    const limit = 10


    const [searchValue, setSearchValue] = useState<string | undefined>()
    const [searchResults, setSearchResults] = useState<NodeData[]>([])

    const [numTotalResults, setNumTotalResults] = useState(0);

    const searchForNodes = (query: string, offset: number, limit: number) => {
        fetch(`/api/search?query=${query}&offset=${offset}&limit=${limit}`).then(response => {
            const json = response.json()

            return json;
        }).then(data => {
            setSearchResults(data.data)
            setNumTotalResults(data["total_count"])
        }).catch(err => {
            // Do something for an error here
            console.log("Error Reading data " + err);
        });
    }

    const searchParams = useSearchParams()

    useEffect(() => {
        if (searchParams.has('q')) {
            const q = searchParams.get('q')
            searchForNodes(q || "", offset, limit)
            setSearchValue(q || undefined)
        }
    }, [searchParams])

    return <>
        <NavBar />
        <SearchInput onInputChange={(e) => {
            setSearchValue(e)
            searchForNodes(e, offset, limit)
        }}>
        </SearchInput>
        <div className={style.SearchResultsWrapper}> {searchResults.length > 0 ?
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
                            return <tr key={node.id} className={style.tableRow} onClick={
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
                {numTotalResults > limit &&
                    <span>
                        {<Button
                            disabled={offset === 0}
                            className="btn-secondary"
                            onClick={() => {
                                const newOffset = Math.max(0, offset - 10)
                                searchForNodes(searchValue || "", newOffset, limit)
                                setOffset(newOffset)
                            }}>Previous
                        </Button>}{' '}
                        {numTotalResults - offset - limit > 0 && <span>{numTotalResults - offset - limit} more results... </span>}
                        {<Button
                            disabled={numTotalResults - limit < offset}
                            className="btn-secondary"
                            onClick={() => {
                                const newOffset = offset + 10;
                                searchForNodes(searchValue || "", newOffset, limit)
                                setOffset(newOffset)
                            }}>Next
                        </Button>}
                    </span>}
            </div> : searchParams.has('q') && <p>No results found.</p>}
        </div>
    </>
};

export default DeviceGraph
