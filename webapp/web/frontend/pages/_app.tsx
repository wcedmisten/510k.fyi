// `pages/_app.js`
import '../styles/globals.css';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function App({ Component, pageProps }: {Component: any; pageProps: any}) {
  return <Component {...pageProps} />;
}
