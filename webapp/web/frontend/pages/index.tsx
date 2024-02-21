import { Col, Container, Row } from 'react-bootstrap'
import style from './landing-page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';

export const LandingPage = () => {
    return <>
        <Container>
            <Row>
                <Col>
                    <h1 className={style.title}>510k.fyi</h1>
                    <h2 className={style.subTitle}>An open source remix of the FDA's official 510(k) database.</h2>
                </Col>
            </Row>
            <Row>
                <Col>
                    <div className={style.deviceLinkWrapper}>
                        <a className={style.deviceLink} href="/devices">Search for a device</a>
                    </div>
                </Col>
            </Row>
            <Row>
                <Col lg="4" sm="12">
                    <b className={style.question}>What is a 510k?</b>
                    <p className={style.answer}>The FDA's 510(k) clearance process allows medical device manufacturers to market their device as long as it is
                        "substantially equivalent" to a legally marketed device.
                        99% of human medical devices are cleared through the 510(k) program.
                        <br /><br/>
                        <a href="https://www.fda.gov/medical-devices/device-approvals-denials-and-clearances/510k-clearances"
                            target="_blank">
                            Read more on fda.gov
                        </a>.
                    </p>
                </Col>
                <Col lg="4" sm="12">
                    <b className={style.question}>Is this website affiliated with the FDA?</b>
                    <p className={style.answer}>
                        No, this website is not affiliated with the FDA.
                        All data on 510k.fyi is derived from the{' '}
                        <a href="https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm"
                           target="_blank">official FDA 510(k) database</a>.
                        This website is meant to be used as reference, but all information should be verified with the official FDA database.
                    </p>
                </Col>
                <Col lg="4" sm="12">
                    <b className={style.question}>Does this website cost money to use?</b>
                    <p className={style.answer}>
                        This website can be used free of charge. All data from the FDA is public domain,
                        and the code for this website is licensed under an open source MIT license.
                    </p>
                </Col>
            </Row>
        </Container>
    </>
}

export default LandingPage
