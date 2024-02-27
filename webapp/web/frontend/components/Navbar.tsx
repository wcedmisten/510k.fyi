import { Container, Nav, Navbar } from "react-bootstrap"
import style from './NavBar.module.css'

import { useState } from "react";
import Link from "next/link";


export const NavBar = () => {
    // return <Navbar>
    //     <Container>
    //         <Navbar.Brand href="/"><span ></span>
    //         <div className={style.wrapper}>
    //             <div className={style.logo} >
    //                 <img src="/logo.png" width={50}></img>
    //             </div>
    //             <span className={style.title}>
    //                 510k.fyi
    //             </span>
    //         </div>
    //         </Navbar.Brand>
    //         <Navbar.Brand href="/search"><p className={style.about}>Search</p></Navbar.Brand>
    //         <Navbar.Brand href="/about"><p className={style.about}>About</p></Navbar.Brand>
    //         <Navbar.Toggle
    //                 onClick={() => setExpanded(!expanded)}
    //                 aria-controls="basic-navbar-nav" />
    //             <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
    //                 <div className="d-flex justify-content-end">
    //                     <Nav activeKey="/" onSelect={() => setExpanded(false)}>
    //                         <Link href="/" passHref>
    //                             <Nav.Link>Posts</Nav.Link>
    //                         </Link>
    //                         <Link href="/about" passHref>
    //                             <Nav.Link>About</Nav.Link>
    //                         </Link>
    //                         <Link href="/projects" passHref>
    //                             <Nav.Link>Projects</Nav.Link>
    //                         </Link>
    //                         <Link href="/talks" passHref>
    //                             <Nav.Link>Talks</Nav.Link>
    //                         </Link>
    //                     </Nav>
    //                 </div>
    //             </Navbar.Collapse>
    //     </Container>

        const [expanded, setExpanded] = useState(false);

    return (
        <Navbar className={style.Navbar} expand="lg" expanded={expanded}>
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
                <Navbar.Toggle
                    onClick={() => setExpanded(!expanded)}
                    aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
                    <div className="d-flex justify-content-end">
                        <Nav activeKey="/" onSelect={() => setExpanded(false)}>
                            <Navbar.Brand href="/search"><p className={style.search}>Search</p></Navbar.Brand>
                            <Navbar.Brand href="/about"><p className={style.about}>About</p></Navbar.Brand>
                        </Nav>
                    </div>
                </Navbar.Collapse>
            </Container>
        </Navbar>)
    // </Navbar>
}