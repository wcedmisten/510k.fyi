// `pages/_app.js`
import '../styles/globals.css';

export default function App({ Component, pageProps }: {Component: any; pageProps: any}) {
  return <Component {...pageProps} />;
}
