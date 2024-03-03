// `pages/_app.js`
import Layout from '../components/Layout';
import '../styles/globals.css';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function App({ Component, pageProps }: {Component: any; pageProps: any}) {

  return <Layout opengraph={pageProps?.opengraph}>
      <Component {...pageProps} />
    </Layout>;
}
