import BEOForm from '../components/BEOForm'
import { ErrorBoundary } from '../components/ErrorBoundary'

export default function Home() {
  return (
    <ErrorBoundary>
      <main
        style={{
          minHeight: '100vh',
          padding: '20px',
          backgroundColor: '#fffaf0',
        }}
      >
        <BEOForm />
      </main>
    </ErrorBoundary>
  )
}
