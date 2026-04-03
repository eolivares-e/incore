export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Admin Portal</h1>
      <p>Welcome to the Insurance Core Admin Portal</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Administrative Features</h2>
        <ul>
          <li>Manage users and roles</li>
          <li>Review and approve policies</li>
          <li>Underwriting oversight</li>
          <li>View analytics and reports</li>
          <li>System configuration</li>
          <li>Manage policy holders</li>
          <li>Process claims</li>
          <li>Financial reporting</li>
        </ul>
      </div>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f0f0f0', borderRadius: '4px' }}>
        <p><strong>API Status:</strong> Connected to {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
      </div>
    </main>
  )
}
