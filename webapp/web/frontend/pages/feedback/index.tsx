import React, { useEffect, useState } from "react";

import style from './feedback.module.css'

import { NavBar } from "../../components/Navbar";


export const DeviceGraph = () => {
    const [submitted, setSubmitted] = useState(false);


    function handleSubmit(event: any) {
        const formData = new FormData(event.currentTarget);
        event.preventDefault();

        let data: {
            [key: string]: string
        } = {}
        for (let [key, value] of formData.entries() as any) {
            data[key] = value;
        }

        event.currentTarget.reset();

        fetch(`/api/submit_feedback`,
            {
                method: "POST", body: JSON.stringify(data), headers: {
                    "Content-Type": "application/json",
                    // 'Content-Type': 'application/x-www-form-urlencoded',
                },
            }
        ).then(response => {
            setSubmitted(true);
        }).catch(err => {
            // Do something for an error here
            console.log("Error Reading data " + err);
            // setIsLoading(false);
        });
    }

    return <>
        <NavBar />

        <h1 className={style.Header}>Feedback</h1>
        <h3 className={style.SubHeader}>Comments? Suggestions? Criticism? I want to hear it!</h3>
        <div className={style.SearchResultsWrapper}>
            <div className={style.SearchInput}>
                <form onSubmit={handleSubmit}>

                    <div className={style.FormItem}>
                        <label htmlFor="name">Name</label>
                        <input id="name" name="name" type="text" />
                    </div>

                    <div className={style.FormItem}>
                        <label htmlFor="email">Email</label>
                        <input id="email" name="email" type="text" />
                    </div>

                    <div className={style.FormItem}>
                        <label htmlFor="message">Message *</label>
                        <textarea id="message" name="message" />
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Submit
                    </button>
                </form>
                {submitted && <p>Feedback submitted! Thanks! 🎉</p>}
            </div>
        </div>
    </>
};

export default DeviceGraph
