import { Col, Container, Row } from 'react-bootstrap';
import style from './about.module.css';
import { NavBar } from '../../components/Navbar';

export const LandingPage = () => {
    return <>
        <NavBar/>
        <Container>
            <Row>
                <Col>
                    <h1 className={style.subTitle}>About 510k.fyi</h1>

                    <img className={style.avatar} src="/images/william.jpg"></img>

                    <p className={style.text}>
                        Hello! My name is William Edmisten, and I'm the software engineer who built 510k.fyi.
                        You can read more about me on my <a href="https://wcedmisten.fyi/about/">blog</a>.
                    </p>
                    
                    <p className={style.text}>    
                        I built 510k.fyi to help consumers, device manufacturers, and the FDA better understand the predicate device ancestry
                        of devices cleared through the 510k process.

                    </p>
                    <p className={style.text}>
                        As of February 2024, the FDA's 510k database does not directly show the predicates used for each device.
                        The only way to find the predicates for  510k is to manually examine the PDF summary of each 510k application.
                        This makes any systematic review of predicate device ancestry difficult.</p>

                    <p className={style.text}>
                        I collected all of the available 510k PDF summaries and used OCR to
                        find the predicates mentioned for each application, in order to simplify 
                        the data, and help show the relationship between recalled devices and 
                        currently marketed ones.
                    </p>
                    
                    <p className={style.text}>
                        Please submit any feedback to <a href="mailto:wcedmisten@gmail.com">wcedmisten@gmail.com</a>  
                    </p>
                </Col>
            </Row>
        </Container>
    </>
}

export default LandingPage
