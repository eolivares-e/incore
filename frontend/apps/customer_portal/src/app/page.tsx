export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Customer Portal</h1>
      <p>Welcome to the Insurance Core Customer Portal</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Features</h2>
        <ul>
          <li>View your policies</li>
          <li>Manage policy holders</li>
          <li>Track claims</li>
          <li>Update personal information</li>
        </ul>
      </div>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f0f0f0', borderRadius: '4px' }}>
        <p><strong>API Status:</strong> Connected to {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
      </div>
    </main>
  )
}
