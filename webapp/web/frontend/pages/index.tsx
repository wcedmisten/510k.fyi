import { Col, Container, Navbar, Row } from 'react-bootstrap'
import style from './landing-page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from '../components/Navbar';
import { useState } from 'react';
import { useRouter } from 'next/router';

export const LandingPage = () => {
    const [queryValue, setQueryValue] = useState();
    const router = useRouter();
    return <>
        <NavBar/>
        <Container>
            <Row>
                <Col>
                    <h1 className={style.title}>Reveal new insights about medical devices</h1>
                </Col>
            </Row>
            <Row>
                <Col>
                    <div className={style.searchButtonWrapper}>
                        <form>
                            <input className={style.searchInput}
                                onChange={(e) => setQueryValue(e.target.value as any)}
                            />
                            <input
                                type="submit"
                                className={style.searchButton}
                                value="Search for a device"
                                onClick={(e) => {
                                    e.preventDefault()
                                    router.push(!!queryValue ? `/search?q=${queryValue}` : "/search")
                                }}
                            />
                        </form>
                    </div>
                </Col>
            </Row>
            <Row>
                <Col lg="4" sm="12">
                    <div className={style.questionWrapper}>
                        <b className={style.question}>What is a 510k?</b>
                        <p className={style.answer}>
                            The FDA's 510(k) program provides clearance for 99% of U.S. human medical devices.
                            The 510(k) clearance process allows medical device manufacturers to market their device as long as it is
                            "substantially equivalent" to a legally marketed device.
                            
                            <br /><br/>
                            <a href="https://www.fda.gov/medical-devices/device-approvals-denials-and-clearances/510k-clearances"
                                target="_blank">
                                Read more on fda.gov
                            </a>.
                        </p>
                    </div>
                </Col>
                <Col lg="4" sm="12">
                    <div className={style.questionWrapper}>
                        <b className={style.question}>Is this website affiliated with the FDA?</b>
                        <p className={style.answer}>
                            No, this website is not affiliated with the FDA.
                            All data on 510k.fyi is derived from the{' '}
                            <a href="https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm"
                            target="_blank">official FDA 510(k) database</a> independently.
                            This website is meant to be used as reference, but all information should be verified with the official FDA database.
                        </p>
                    </div>
                </Col>
                <Col lg="4" sm="12">
                    <div className={style.questionWrapper}>
                        <b className={style.question}>Does this website cost money to use?</b>
                        <p className={style.answer}>
                            This website can be used free of charge. All data from the FDA is public domain,
                            and the code for this website is licensed under an open source MIT license.
                        </p>
                    </div>
                </Col>
            </Row>
            {/* TODO: add screenshots */}
            {/* <Row>
                <Col>
                    <h3 className={style.featuresHeader}>Features</h3>
                </Col>
            </Row>
            <Row>
                <Col>
                    <p>Find device predicates</p>
                </Col>
                <Col>
                    <p>Improved search</p>
                </Col>
                <Col>
                    <p>Integrated recall information</p>
                </Col>
            </Row> */}
            
        </Container>
    </>
}

export default LandingPage
