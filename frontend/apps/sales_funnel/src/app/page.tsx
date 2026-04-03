export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Sales Funnel</h1>
      <p>Welcome to the Insurance Core Sales Funnel</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Get Started</h2>
        <ul>
          <li>Request a quote</li>
          <li>Compare insurance plans</li>
          <li>Purchase a policy</li>
          <li>Talk to an agent</li>
        </ul>
      </div>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f0f0f0', borderRadius: '4px' }}>
        <p><strong>API Status:</strong> Connected to {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
      </div>
    </main>
  )
}
