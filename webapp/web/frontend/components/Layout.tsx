
import Head from 'next/head';
import React from 'react'

interface OpenGraph {
    title: string;
    image: string;
    type: string;
    url: string;
    description: string;
}

interface LayoutProps {
    children: React.ReactNode;
    opengraph: OpenGraph | undefined;
}

const defaultMeta = {
    title: '510k.fyi',
    description: 'Reveal new insights about medical devices. A comprehensive database of 510k medical device clearances and recalls.',
    image: '/images/DeviceGraphScreenshot.png'
}

const Layout: React.FC<LayoutProps> = ({
    children,
    opengraph,
}) => (
    <>
        <Head>
            <title>{opengraph?.title || defaultMeta.title}</title>
            <meta name="description" content={opengraph?.description || defaultMeta.description} />
            <meta property="og:title" content={opengraph?.title || defaultMeta.title} />
            <meta property="og:image" content={opengraph?.image || defaultMeta.image} />
            <meta property="og:description" content={opengraph?.description || defaultMeta.description} />
            <link rel="icon" href="/favicon.ico" />
            <script defer data-domain="510k.fyi" src="http://zlfieuwrjks.wcedmisten.dev/js/script.js"></script>
        </Head>
        <main>{children}</main>
    </>
);

export default Layout;
