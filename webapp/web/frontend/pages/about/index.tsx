import { Col, Container, Row } from 'react-bootstrap'
import style from './landing-page.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from '../../components/Navbar';

export const LandingPage = () => {
    return <>
        <NavBar/>
        <Container>
            <Row>
                <Col>
                    <h1 className={style.subTitle}>About 510k.fyi</h1>
                    <p>
                        510k.fyi is an open source website developed by <a href="https://wcedmisten.fyi/about/">William Edmisten</a>.
                        The website is meant to help consumers, device manufacturers, and the FDA better understand the predicate device ancestry
                        of cleared devices.
                        As of February 2024, the FDA's 510k database does not directly show the predicates used for each device.
                        The only way to find the predicates for a 510k is to manually examine a PDF summary of the 510k application.
                        This makes any systematic review of predicate device ancestry difficult.</p>

                    <p>
                        To make systematic review more feasible, I collected all 
                        of the available 510k PDF summaries and used OCR to find the predicates mentioned for each application.
                        I collected this data into the database which powers this website.
                    </p>
                    
                    <p>
                        Please submit any feedback to <a href="mailto:wcedmisten@gmail.com">wcedmisten@gmail.com</a>  
                    </p>
                </Col>
            </Row>
        </Container>
    </>
}

export default LandingPage
