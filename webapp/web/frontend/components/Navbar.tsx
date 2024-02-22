import { Container, Navbar } from "react-bootstrap"
import style from './NavBar.module.css'
import 'bootstrap/dist/css/bootstrap.min.css';


export const NavBar = () => {
    return <Navbar>
        <Container>
            <Navbar.Brand href="/"><span ></span>
            <div className={style.wrapper}>
                <div className={style.logo} >
                    <img src="/logo.png" width={50}></img>
                </div>
                <span className={style.title}>
                    510k.fyi
                </span>
            </div>
            </Navbar.Brand>
            <Navbar.Brand href="/about"><p className={style.about}>About</p></Navbar.Brand>
        </Container>
    </Navbar>
}