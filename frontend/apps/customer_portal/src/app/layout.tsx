import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Customer Portal - Insurance Core',
  description: 'Manage your insurance policies',
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
