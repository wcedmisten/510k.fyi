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
                    <h1 className={style.subTitle}>TODO: Add about page</h1>
                </Col>
            </Row>
        </Container>
    </>
}

export default LandingPage
