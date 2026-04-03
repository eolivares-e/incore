import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Admin Portal - Insurance Core',
  description: 'Manage insurance operations and administration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
